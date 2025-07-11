#!/usr/bin/env python3
"""
🗄️ Shared Database Manager
Centralized database operations and utilities for AI Governance Study Portal.

Features:
- Shared connection management
- Common CRUD operations
- Error handling and logging
- Database initialization
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path
        # Ensure data directory exists
        Path(db_path).parent.mkdir(exist_ok=True)
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: Tuple = (), fetch: str = None) -> Any:
        """Execute a query with error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch == "one":
                    return cursor.fetchone()
                elif fetch == "all":
                    return cursor.fetchall()
                elif fetch == "lastrowid":
                    conn.commit()
                    return cursor.lastrowid
                else:
                    conn.commit()
                    return cursor.rowcount
                    
        except Exception as e:
            print(f"❌ Database error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise e
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute many queries with the same statement"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"❌ Database batch error: {e}")
            raise e
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,), fetch="one")
        return result is not None
    
    def create_table_if_not_exists(self, table_name: str, schema: str):
        """Create table if it doesn't exist"""
        if not self.table_exists(table_name):
            self.execute_query(f"CREATE TABLE {table_name} ({schema})")
            print(f"✅ Created table: {table_name}")
    
    def get_table_info(self, table_name: str) -> List[Tuple]:
        """Get table schema information"""
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query, fetch="all")
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterations
        )
        
        return password_hash.hex(), salt
    
    def insert_record(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a record and return the ID"""
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]
        values = list(data.values())
        
        query = f"""
            INSERT INTO {table} ({', '.join(columns)}) 
            VALUES ({', '.join(placeholders)})
        """
        
        return self.execute_query(query, tuple(values), fetch="lastrowid")
    
    def update_record(self, table: str, data: Dict[str, Any], where_clause: str, where_params: Tuple = ()) -> int:
        """Update records and return number of affected rows"""
        set_clauses = [f"{key} = ?" for key in data.keys()]
        values = list(data.values()) + list(where_params)
        
        query = f"""
            UPDATE {table} 
            SET {', '.join(set_clauses)} 
            WHERE {where_clause}
        """
        
        return self.execute_query(query, tuple(values))
    
    def delete_record(self, table: str, where_clause: str, where_params: Tuple = ()) -> int:
        """Delete records and return number of affected rows"""
        query = f"DELETE FROM {table} WHERE {where_clause}"
        return self.execute_query(query, where_params)
    
    def get_records(self, table: str, where_clause: str = "", where_params: Tuple = (), 
                   order_by: str = "", limit: Optional[int] = None) -> List[Tuple]:
        """Get records with optional filtering, ordering, and limiting"""
        query = f"SELECT * FROM {table}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
            
        return self.execute_query(query, where_params, fetch="all")
    
    def get_single_record(self, table: str, where_clause: str, where_params: Tuple = ()) -> Optional[Tuple]:
        """Get a single record"""
        query = f"SELECT * FROM {table} WHERE {where_clause} LIMIT 1"
        return self.execute_query(query, where_params, fetch="one")
    
    def count_records(self, table: str, where_clause: str = "", where_params: Tuple = ()) -> int:
        """Count records with optional filtering"""
        query = f"SELECT COUNT(*) FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        result = self.execute_query(query, where_params, fetch="one")
        return result[0] if result else 0
    
    def record_exists(self, table: str, where_clause: str, where_params: Tuple = ()) -> bool:
        """Check if a record exists"""
        count = self.count_records(table, where_clause, where_params)
        return count > 0
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        try:
            with self.get_connection() as source:
                backup = sqlite3.connect(backup_path)
                source.backup(backup)
                backup.close()
            print(f"✅ Database backed up to: {backup_path}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            raise e
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        # Get all table names
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = self.execute_query(tables_query, fetch="all")
        
        for (table_name,) in tables:
            count = self.count_records(table_name)
            stats[table_name] = count
        
        # Get database size
        try:
            db_size = Path(self.db_path).stat().st_size
            stats["database_size_mb"] = round(db_size / (1024 * 1024), 2)
        except:
            stats["database_size_mb"] = 0
        
        return stats 