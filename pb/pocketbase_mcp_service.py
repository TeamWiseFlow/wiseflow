#!/usr/bin/env python3
"""
PocketBase MCP Service - Read-only access to PocketBase data.db for RAG integration
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Optional
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pb_data", "data.db")
HOST = "localhost"
PORT = 8765

class PocketBaseDB:
    """Interface to the PocketBase SQLite database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._validate_db()
    
    def _validate_db(self):
        """Validate that the database exists and has the expected tables"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if infos table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='infos'")
        if not cursor.fetchone():
            conn.close()
            raise ValueError("Required 'infos' table not found in database")
        
        conn.close()
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """Get schema information for a specific table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
        
        conn.close()
        return schema
    
    def query_table(self, table_name: str, limit: int = 100, offset: int = 0, 
                   filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query data from a table with optional filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = f"SELECT * FROM {table_name}"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} LIKE ?")
                params.append(f"%{value}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += f" LIMIT {limit} OFFSET {offset}"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results

class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the MCP service"""
    
    def __init__(self, *args, **kwargs):
        self.db = PocketBaseDB(DB_PATH)
        super().__init__(*args, **kwargs)
    
    def _send_json_response(self, data: Any, status: int = 200):
        """Send JSON response with appropriate headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, message: str, status: int = 400):
        """Send error response"""
        self._send_json_response({"error": message}, status)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        try:
            # Route: /tables - List all tables
            if len(path_parts) == 1 and path_parts[0] == "tables":
                tables = self.db.get_tables()
                self._send_json_response({"tables": tables})
                return
            
            # Route: /tables/{table_name}/schema - Get table schema
            if len(path_parts) == 3 and path_parts[0] == "tables" and path_parts[2] == "schema":
                table_name = path_parts[1]
                schema = self.db.get_table_schema(table_name)
                self._send_json_response({"schema": schema})
                return
            
            # Route: /tables/{table_name}/data - Query table data
            if len(path_parts) == 3 and path_parts[0] == "tables" and path_parts[2] == "data":
                table_name = path_parts[1]
                
                # Parse query parameters
                query_params = urllib.parse.parse_qs(parsed_path.query)
                limit = int(query_params.get('limit', ['100'])[0])
                offset = int(query_params.get('offset', ['0'])[0])
                
                # Extract filters
                filters = {}
                for key, value in query_params.items():
                    if key not in ['limit', 'offset']:
                        filters[key] = value[0]
                
                data = self.db.query_table(table_name, limit, offset, filters)
                self._send_json_response({"data": data, "count": len(data), "limit": limit, "offset": offset})
                return
            
            # Default: Not found
            self._send_error("Endpoint not found", 404)
            
        except Exception as e:
            self._send_error(f"Error: {str(e)}", 500)
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    """Main entry point for the MCP service"""
    parser = argparse.ArgumentParser(description='PocketBase MCP Service')
    parser.add_argument('--host', default=HOST, help=f'Host to bind to (default: {HOST})')
    parser.add_argument('--port', type=int, default=PORT, help=f'Port to bind to (default: {PORT})')
    args = parser.parse_args()
    
    print(f"Starting PocketBase MCP Service on {args.host}:{args.port}")
    print(f"Database path: {DB_PATH}")
    
    # Validate database before starting server
    try:
        db = PocketBaseDB(DB_PATH)
        tables = db.get_tables()
        print(f"Available tables: {', '.join(tables)}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return
    
    server = HTTPServer((args.host, args.port), MCPRequestHandler)
    
    try:
        print("Server started. Press Ctrl+C to stop.")
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        server.server_close()

if __name__ == "__main__":
    main()
