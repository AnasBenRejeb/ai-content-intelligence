"""Memory system for agents"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum


class MemoryType(Enum):
    """Types of memory"""
    EPISODIC = "episodic"  # Specific experiences
    SEMANTIC = "semantic"  # General knowledge
    PROCEDURAL = "procedural"  # How-to knowledge
    WORKING = "working"  # Short-term context


@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str
    type: MemoryType
    content: Dict[str, Any]
    timestamp: datetime
    importance: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['type'] = self.type.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data


class MemoryStore:
    """Persistent memory storage"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                importance REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                metadata TEXT
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_type ON memories(type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance DESC)
        """)
        conn.commit()
        conn.close()
    
    def store(self, entry: MemoryEntry):
        """Store memory entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, type, content, timestamp, importance, access_count, last_accessed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.type.value,
            json.dumps(entry.content),
            entry.timestamp.isoformat(),
            entry.importance,
            entry.access_count,
            entry.last_accessed.isoformat() if entry.last_accessed else None,
            json.dumps(entry.metadata) if entry.metadata else None
        ))
        conn.commit()
        conn.close()
    
    def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve specific memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_entry(row)
    
    def query(self, memory_type: Optional[MemoryType] = None, 
              limit: int = 10, min_importance: float = 0.0) -> List[MemoryEntry]:
        """Query memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM memories WHERE importance >= ?"
        params = [min_importance]
        
        if memory_type:
            query += " AND type = ?"
            params.append(memory_type.value)
        
        query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_entry(row) for row in rows]
    
    def update_access(self, memory_id: str):
        """Update access statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE memories 
            SET access_count = access_count + 1,
                last_accessed = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), memory_id))
        conn.commit()
        conn.close()
    
    def _row_to_entry(self, row) -> MemoryEntry:
        """Convert database row to MemoryEntry"""
        return MemoryEntry(
            id=row[0],
            type=MemoryType(row[1]),
            content=json.loads(row[2]),
            timestamp=datetime.fromisoformat(row[3]),
            importance=row[4],
            access_count=row[5],
            last_accessed=datetime.fromisoformat(row[6]) if row[6] else None,
            metadata=json.loads(row[7]) if row[7] else None
        )
