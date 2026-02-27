"""
NocoDB Client for MoltBot
Async REST API client to replace MongoDB operations
Stores all data as JSON in the Title field of NocoDB records
"""
import httpx
import os
import logging
import json
from typing import Optional, Dict, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class NocoDBClient:
    """Async client for NocoDB REST API operations"""
    
    def __init__(self):
        self.base_url = os.environ.get('NOCODB_URL', 'https://app.nocodb.com/api/v2/tables/mofz1f3ftcxtks5/records')
        self.token = os.environ.get('NOCODB_TOKEN', '')
        self.headers = {
            'xc-token': self.token,
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }
        # In-memory cache for faster lookups (collection -> list of records)
        self._cache = {}
        
    async def _request(self, method: str, endpoint: str = "", json_data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request to NocoDB API"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json_data,
                    params=params
                )
                response.raise_for_status()
                
                if response.status_code == 204:
                    return {"ok": True}
                    
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"NocoDB API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"NocoDB request error: {e}")
                raise
    
    async def _get_all_records(self) -> List[Dict]:
        """Fetch all records from NocoDB"""
        try:
            result = await self._request('GET', '', params={'limit': 1000})
            return result.get('list', [])
        except Exception as e:
            logger.error(f"Error fetching all records: {e}")
            return []
    
    def _parse_record(self, record: Dict) -> Optional[Dict]:
        """Parse NocoDB record Title field into Python dict"""
        try:
            title = record.get('Title', '{}')
            if not title:
                return None
            
            # Parse JSON from Title field
            data = json.loads(title)
            
            # Add NocoDB ID for updates/deletes
            data['_nocodb_id'] = record.get('Id')
            
            return data
        except Exception as e:
            logger.error(f"Error parsing record: {e}")
            return None
    
    def _serialize_record(self, collection: str, document: Dict) -> str:
        """Serialize document to JSON string for Title field"""
        # Add collection type and metadata
        record = {
            '_collection': collection,
            **self._serialize_document(document)
        }
        return json.dumps(record)
    
    def _serialize_document(self, doc: Dict) -> Dict:
        """Serialize document (convert datetime to ISO strings)"""
        serialized = {}
        for key, value in doc.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value
        return serialized
    
    async def find_one(self, collection: str, query: Dict, projection: Dict = None) -> Optional[Dict]:
        """Find a single record matching query (MongoDB-like interface)"""
        try:
            # Get all records
            all_records = await self._get_all_records()
            
            # Filter by collection and query
            for record in all_records:
                parsed = self._parse_record(record)
                if not parsed:
                    continue
                
                # Check collection match
                if parsed.get('_collection') != collection:
                    continue
                
                # Check query match
                matches = True
                for key, value in query.items():
                    if key in ["_id", "record_id"]:
                        # Check both _id and record_id
                        if parsed.get('_id') != value and parsed.get('record_id') != value:
                            matches = False
                            break
                    elif parsed.get(key) != value:
                        matches = False
                        break
                
                if matches:
                    return parsed
            
            return None
            
        except Exception as e:
            logger.error(f"find_one error: {e}")
            return None
    
    async def find(self, collection: str, query: Dict = None, projection: Dict = None, limit: int = 1000) -> List[Dict]:
        """Find multiple records (MongoDB-like interface)"""
        try:
            query = query or {}
            
            # Get all records
            all_records = await self._get_all_records()
            
            # Filter by collection and query
            results = []
            for record in all_records:
                parsed = self._parse_record(record)
                if not parsed:
                    continue
                
                # Check collection match
                if parsed.get('_collection') != collection:
                    continue
                
                # Check query match
                matches = True
                for key, value in query.items():
                    if key not in ["_id", "_nocodb_id"] and parsed.get(key) != value:
                        matches = False
                        break
                
                if matches:
                    results.append(parsed)
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"find error: {e}")
            return []
    
    async def insert_one(self, collection: str, document: Dict) -> Dict:
        """Insert a single record (MongoDB-like interface)"""
        try:
            # Serialize document to JSON string
            title_data = self._serialize_record(collection, document)
            
            # Create NocoDB record
            nocodb_record = {'Title': title_data}
            
            result = await self._request('POST', '', json_data=nocodb_record)
            
            # Get the generated ID
            nocodb_id = result.get('Id')
            
            return {"ok": True, "inserted_id": nocodb_id}
            
        except Exception as e:
            logger.error(f"insert_one error: {e}")
            raise
    
    async def update_one(self, collection: str, query: Dict, update: Dict, upsert: bool = False) -> Dict:
        """Update a single record (MongoDB-like interface)"""
        try:
            # Find existing record
            existing = await self.find_one(collection, query)
            
            if not existing:
                if upsert:
                    # Insert new record
                    doc_to_insert = {}
                    
                    # Handle $setOnInsert
                    if '$setOnInsert' in update:
                        doc_to_insert.update(update['$setOnInsert'])
                    
                    # Handle $set
                    if '$set' in update:
                        doc_to_insert.update(update['$set'])
                    
                    # Add query fields
                    doc_to_insert.update(query)
                    
                    return await self.insert_one(collection, doc_to_insert)
                return {"ok": False, "matched": 0}
            
            # Get the NocoDB record ID
            nocodb_id = existing.get('_nocodb_id')
            if not nocodb_id:
                logger.error("No NocoDB ID found for update")
                return {"ok": False}
            
            # Apply updates
            updated_doc = {k: v for k, v in existing.items() if k not in ['_nocodb_id', '_collection']}
            
            if '$set' in update:
                updated_doc.update(update['$set'])
            
            if '$setOnInsert' in update and not existing:
                updated_doc.update(update['$setOnInsert'])
            
            # Serialize and update
            title_data = self._serialize_record(collection, updated_doc)
            nocodb_record = {'Title': title_data}
            
            await self._request('PATCH', f'/{nocodb_id}', json_data=nocodb_record)
            return {"ok": True, "matched": 1, "modified": 1}
            
        except Exception as e:
            logger.error(f"update_one error: {e}")
            raise
    
    async def delete_one(self, collection: str, query: Dict) -> Dict:
        """Delete a single record (MongoDB-like interface)"""
        try:
            # Find the record first
            existing = await self.find_one(collection, query)
            if not existing:
                return {"ok": True, "deleted": 0}
            
            nocodb_id = existing.get('_nocodb_id')
            if not nocodb_id:
                return {"ok": False}
            
            await self._request('DELETE', f'/{nocodb_id}')
            return {"ok": True, "deleted": 1}
            
        except Exception as e:
            logger.error(f"delete_one error: {e}")
            raise


class NocoDBCollection:
    """MongoDB-like collection interface for NocoDB"""
    
    def __init__(self, client: NocoDBClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name
    
    async def find_one(self, query: Dict, projection: Dict = None) -> Optional[Dict]:
        """Find one record"""
        return await self.client.find_one(self.collection_name, query, projection)
    
    async def find(self, query: Dict = None, projection: Dict = None) -> 'NocoDBCursor':
        """Find multiple records"""
        query = query or {}
        return NocoDBCursor(self.client, self.collection_name, query, projection)
    
    async def insert_one(self, document: Dict) -> Dict:
        """Insert one record"""
        return await self.client.insert_one(self.collection_name, document)
    
    async def update_one(self, query: Dict, update: Dict, upsert: bool = False) -> Dict:
        """Update one record"""
        return await self.client.update_one(self.collection_name, query, update, upsert)
    
    async def delete_one(self, query: Dict) -> Dict:
        """Delete one record"""
        return await self.client.delete_one(self.collection_name, query)


class NocoDBCursor:
    """Cursor-like interface for NocoDB queries"""
    
    def __init__(self, client: NocoDBClient, collection: str, query: Dict, projection: Dict = None):
        self.client = client
        self.collection = collection
        self.query = query
        self.projection = projection
        self.limit_count = 1000
    
    async def to_list(self, length: int = None) -> List[Dict]:
        """Convert cursor to list"""
        limit = length if length is not None else self.limit_count
        return await self.client.find(self.collection, self.query, self.projection, limit)


class NocoDBDatabase:
    """MongoDB-like database interface for NocoDB"""
    
    def __init__(self):
        self.client = NocoDBClient()
        self._collections = {}
    
    def __getattr__(self, name: str) -> NocoDBCollection:
        """Get collection by name"""
        if name not in self._collections:
            self._collections[name] = NocoDBCollection(self.client, name)
        return self._collections[name]
    
    def __getitem__(self, name: str) -> NocoDBCollection:
        """Get collection by name using bracket notation"""
        return self.__getattr__(name)
