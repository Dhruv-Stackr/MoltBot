"""
Backend API Tests for NocoDB Migration
Testing data persistence and retrieval through NocoDB REST API
"""
import pytest
import requests
import os
import json
from datetime import datetime, timezone, timedelta
import uuid

# Base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
# NocoDB credentials for direct verification
NOCODB_URL = "https://app.nocodb.com/api/v2/tables/mofz1f3ftcxtks5/records"
NOCODB_TOKEN = "bnxELWAHG5z41N8JTGDjRBp4k8r8q41cMh_abecn"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def nocodb_client():
    """Direct NocoDB client for verification"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "xc-token": NOCODB_TOKEN
    })
    return session


@pytest.fixture(scope="module")
def test_user_session(nocodb_client):
    """Create test user and session in NocoDB for authenticated tests"""
    test_user_id = f"pytest_user_{uuid.uuid4().hex[:8]}"
    session_token = f"pytest_session_{uuid.uuid4().hex[:16]}"
    expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    
    # Create user
    user_data = {
        "Title": json.dumps({
            "_collection": "users",
            "user_id": test_user_id,
            "email": f"{test_user_id}@pytest.com",
            "name": "PyTest User",
            "picture": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    }
    response = nocodb_client.post(NOCODB_URL, json=user_data)
    assert response.status_code == 200, f"Failed to create test user: {response.text}"
    user_nocodb_id = response.json().get("Id")
    
    # Create session
    session_data = {
        "Title": json.dumps({
            "_collection": "user_sessions",
            "user_id": test_user_id,
            "session_token": session_token,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    }
    response = nocodb_client.post(NOCODB_URL, json=session_data)
    assert response.status_code == 200, f"Failed to create test session: {response.text}"
    session_nocodb_id = response.json().get("Id")
    
    yield {
        "user_id": test_user_id,
        "session_token": session_token,
        "email": f"{test_user_id}@pytest.com"
    }
    
    # Cleanup: Delete test data
    try:
        nocodb_client.delete(f"{NOCODB_URL}/{user_nocodb_id}")
        nocodb_client.delete(f"{NOCODB_URL}/{session_nocodb_id}")
    except Exception as e:
        print(f"Cleanup warning: {e}")


# ==== Root API Tests ====

class TestRootAPI:
    """Test root API endpoint"""
    
    def test_root_endpoint_returns_message(self, api_client):
        """GET /api/ returns API info"""
        response = api_client.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "OpenClaw Hosting API"
        print(f"Root API response: {data}")


# ==== Instance Locking Tests ====

class TestInstanceLocking:
    """Test instance lock status endpoint"""
    
    def test_get_instance_status_unauthenticated(self, api_client):
        """GET /api/auth/instance returns lock status for unauthenticated users"""
        response = api_client.get(f"{BASE_URL}/api/auth/instance")
        assert response.status_code == 200
        data = response.json()
        assert "locked" in data
        # Can be True or False depending on whether instance is locked
        assert isinstance(data["locked"], bool)
        print(f"Instance locked status: {data}")


# ==== Authentication Tests ====

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_auth_me_without_token_returns_401(self, api_client):
        """GET /api/auth/me returns 401 without authentication"""
        response = api_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "authenticated" in data["detail"].lower()
        print(f"Unauthenticated /auth/me response: {data}")
    
    def test_auth_me_with_valid_token_returns_user(self, api_client, test_user_session):
        """GET /api/auth/me returns user data with valid Bearer token"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {test_user_session['session_token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user_session["user_id"]
        assert data["email"] == test_user_session["email"]
        assert data["name"] == "PyTest User"
        print(f"Authenticated user data: {data}")
    
    def test_auth_me_with_invalid_token_returns_401(self, api_client):
        """GET /api/auth/me returns 401 with invalid token"""
        response = api_client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401
        print("Invalid token correctly rejected with 401")
    
    def test_auth_session_validates_session_id(self, api_client):
        """POST /api/auth/session validates the session_id parameter"""
        # Test with invalid session_id - should return 401 from Emergent auth
        response = api_client.post(
            f"{BASE_URL}/api/auth/session",
            json={"session_id": "invalid_emergent_session_id"}
        )
        # Expect 401 since invalid session_id won't validate with Emergent
        assert response.status_code == 401
        print("Invalid session_id correctly rejected")
    
    def test_auth_logout_clears_session(self, api_client, test_user_session):
        """POST /api/auth/logout clears session and returns success"""
        # First verify the user is logged in
        response = api_client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {test_user_session['session_token']}"}
        )
        assert response.status_code == 200, "User should be authenticated before logout"
        
        # Now logout with cookie
        response = api_client.post(
            f"{BASE_URL}/api/auth/logout",
            cookies={"session_token": test_user_session['session_token']}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") == True
        assert "logged out" in data.get("message", "").lower()
        print(f"Logout response: {data}")


# ==== Status Check Tests (Data Persistence) ====

class TestStatusChecks:
    """Test status check endpoints - validates NocoDB data persistence"""
    
    def test_create_status_check_persists_data(self, api_client, nocodb_client):
        """POST /api/status creates and persists data in NocoDB"""
        unique_client = f"pytest_client_{uuid.uuid4().hex[:8]}"
        
        # Create status check via API
        response = api_client.post(
            f"{BASE_URL}/api/status",
            json={"client_name": unique_client}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["client_name"] == unique_client
        assert "id" in data
        assert "timestamp" in data
        print(f"Created status check: {data}")
        
        # Verify data in NocoDB directly
        nocodb_response = nocodb_client.get(f"{NOCODB_URL}?limit=100")
        assert nocodb_response.status_code == 200
        records = nocodb_response.json().get("list", [])
        
        # Find our record
        found = False
        for record in records:
            title = record.get("Title")
            if title and unique_client in title:
                parsed = json.loads(title)
                assert parsed.get("_collection") == "status_checks"
                assert parsed.get("client_name") == unique_client
                found = True
                print(f"Verified data in NocoDB: {parsed}")
                break
        
        assert found, f"Status check '{unique_client}' not found in NocoDB"
    
    def test_get_status_checks_retrieves_data(self, api_client):
        """GET /api/status retrieves status checks from NocoDB"""
        response = api_client.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Retrieved {len(data)} status checks")
        
        if len(data) > 0:
            # Verify structure of first item
            check = data[0]
            assert "id" in check
            assert "client_name" in check
            assert "timestamp" in check
            print(f"Sample status check: {check}")


# ==== Gateway Tests ====

class TestGatewayOperations:
    """Test OpenClaw gateway operations"""
    
    def test_openclaw_status_without_auth(self, api_client):
        """GET /api/openclaw/status works for unauthenticated users"""
        response = api_client.get(f"{BASE_URL}/api/openclaw/status")
        assert response.status_code == 200
        data = response.json()
        assert "running" in data
        print(f"Gateway status (unauthenticated): {data}")
    
    def test_openclaw_start_requires_auth(self, api_client):
        """POST /api/openclaw/start requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/openclaw/start",
            json={"provider": "emergent"}
        )
        assert response.status_code == 401
        print("Gateway start correctly requires authentication")
    
    def test_openclaw_stop_requires_auth(self, api_client):
        """POST /api/openclaw/stop requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/openclaw/stop")
        assert response.status_code == 401
        print("Gateway stop correctly requires authentication")
    
    def test_openclaw_status_with_auth(self, api_client, test_user_session):
        """GET /api/openclaw/status returns detailed status for authenticated users"""
        response = api_client.get(
            f"{BASE_URL}/api/openclaw/status",
            headers={"Authorization": f"Bearer {test_user_session['session_token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "running" in data
        # If running, should have additional fields
        if data["running"]:
            assert "provider" in data
            assert "started_at" in data
            assert "controlUrl" in data
            assert "is_owner" in data
        print(f"Gateway status (authenticated): {data}")


# ==== NocoDB Direct Verification Tests ====

class TestNocoDBPersistence:
    """Verify NocoDB data structure and persistence"""
    
    def test_nocodb_connection(self, nocodb_client):
        """Verify NocoDB API is accessible"""
        response = nocodb_client.get(f"{NOCODB_URL}?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert "list" in data
        assert "pageInfo" in data
        print(f"NocoDB connection verified. Total records: {data['pageInfo']['totalRows']}")
    
    def test_nocodb_record_structure(self, nocodb_client):
        """Verify NocoDB records have correct structure"""
        response = nocodb_client.get(f"{NOCODB_URL}?limit=50")
        assert response.status_code == 200
        records = response.json().get("list", [])
        
        collections_found = set()
        for record in records:
            title = record.get("Title")
            if title:
                try:
                    parsed = json.loads(title)
                    collection = parsed.get("_collection")
                    if collection:
                        collections_found.add(collection)
                except json.JSONDecodeError:
                    pass
        
        print(f"Collections found in NocoDB: {collections_found}")
        # Should have at least status_checks from our tests
        assert len(collections_found) > 0, "No collections found in NocoDB"


# ==== Cleanup ====

@pytest.fixture(scope="module", autouse=True)
def cleanup_pytest_data(nocodb_client):
    """Clean up pytest-generated data after all tests"""
    yield
    
    # Get all records
    try:
        response = nocodb_client.get(f"{NOCODB_URL}?limit=1000")
        if response.status_code == 200:
            records = response.json().get("list", [])
            deleted = 0
            for record in records:
                title = record.get("Title")
                if title and ("pytest_" in title or "pytest_user_" in title or "pytest_client_" in title or "pytest_session_" in title):
                    nocodb_client.delete(f"{NOCODB_URL}/{record['Id']}")
                    deleted += 1
            if deleted > 0:
                print(f"\nCleaned up {deleted} pytest records from NocoDB")
    except Exception as e:
        print(f"Cleanup warning: {e}")
