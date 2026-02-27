"""
NocoDB Client for MoltBot
Async REST API client to replace MongoDB operations
"""
import httpx
import os
import logging
from typing import Optional, Dict, List, Any
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
    
    async def find_one(self, collection: str, query: Dict, projection: Dict = None) -> Optional[Dict]:
        """Find a single record matching query (MongoDB-like interface)"""
        try:
            # Build NocoDB where clause
            where_conditions = []
            for key, value in query.items():
                if key == "_id":
                    # Special handling for _id field (maps to record_id)
                    where_conditions.append(f"(record_id,eq,{value})")
                elif isinstance(value, dict):
                    # Handle operators like $ne, $gt, etc.
                    # For now, just handle equality
                    continue
                else:
                    where_conditions.append(f"(record_data,like,%{key}%)")
            
            # Add collection type filter
            where_conditions.append(f"(collection_type,eq,{collection})")
            where_clause = f"@and({','.join(where_conditions)})" if where_conditions else f"@(collection_type,eq,{collection})"
            
            params = {
                'where': where_clause,
                'limit': 1
            }
            
            result = await self._request('GET', '', params=params)
            records = result.get('list', []) if isinstance(result, dict) else result
            
            if not records:
                return None
            
            record = records[0]
            # Parse the stored data
            return self._parse_record(record)
            
        except Exception as e:
            logger.error(f"find_one error: {e}")
            return None
    
    async def find(self, collection: str, query: Dict = None, projection: Dict = None, limit: int = 1000) -> List[Dict]:
        """Find multiple records (MongoDB-like interface)"""
        try:
            query = query or {}
            
            # Build where clause
            where_conditions = [f"(collection_type,eq,{collection})"]
            
            for key, value in query.items():
                if key != "_id" and not isinstance(value, dict):
                    # Simple equality search (store full records in record_data as JSON string)
                    pass  # Will filter after retrieval
            
            where_clause = "@and(" + ",".join(where_conditions) + ")"
            
            params = {
                'where': where_clause,
                'limit': limit
            }
            
            result = await self._request('GET', '', params=params)
            records = result.get('list', []) if isinstance(result, dict) else result
            
            # Parse and filter records
            parsed_records = []
            for record in records:
                parsed = self._parse_record(record)
                if parsed:
                    # Apply query filters
                    matches = True
                    for key, value in query.items():
                        if key != "_id" and parsed.get(key) != value:
                            matches = False
                            break
                    if matches:
                        parsed_records.append(parsed)
            
            return parsed_records
            
        except Exception as e:
            logger.error(f"find error: {e}")
            return []
    
    async def insert_one(self, collection: str, document: Dict) -> Dict:
        """Insert a single record (MongoDB-like interface)"""
        try:
            # Generate a unique record_id if not provided
            record_id = document.get('_id') or document.get('user_id') or document.get('session_token') or str(datetime.now(timezone.utc).timestamp())
            
            # Serialize datetime objects
            serialized_doc = self._serialize_document(document)
            
            # Create NocoDB record
            nocodb_record = {
                'record_id': str(record_id),
                'collection_type': collection,
                'record_data': str(serialized_doc),  # Store as JSON string
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            result = await self._request('POST', '', json_data=nocodb_record)
            return {"ok": True, "inserted_id": record_id}
            
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
            updated_doc = existing.copy()
            updated_doc.pop('_nocodb_id', None)
            
            if '$set' in update:
                updated_doc.update(update['$set'])
            
            if '$setOnInsert' in update and not existing:
                updated_doc.update(update['$setOnInsert'])
            
            # Serialize and update
            serialized_doc = self._serialize_document(updated_doc)
            nocodb_record = {
                'record_data': str(serialized_doc),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
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
    
    def _serialize_document(self, doc: Dict) -> Dict:
        """Serialize document for storage (convert datetime to ISO strings)"""
        serialized = {}
        for key, value in doc.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value
        return serialized
    
    def _parse_record(self, record: Dict) -> Optional[Dict]:
        """Parse NocoDB record back to MongoDB-like document"""
        try:
            if not record:
                return None
            
            # Extract record_data
            record_data_str = record.get('record_data', '{}')
            
            # Parse the stored data
            import json
            if isinstance(record_data_str, str):
                try:
                    parsed = json.loads(record_data_str.replace("'", '"'))
                except:
                    # If it's not valid JSON, try eval (careful!)
                    try:
                        parsed = eval(record_data_str)
                    except:
                        parsed = {}
            else:
                parsed = record_data_str if isinstance(record_data_str, dict) else {}
            
            # Store NocoDB ID for updates/deletes
            parsed['_nocodb_id'] = record.get('Id') or record.get('id')
            
            return parsed
            
        except Exception as e:
            logger.error(f"parse_record error: {e}")
            return None


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
