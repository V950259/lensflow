import sqlite3
import datetime
import os

class HistoryManager:
    def __init__(self, db_path="data/history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                category TEXT,
                title TEXT,
                summary TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_record(self, category, title, summary):
        """添加一条识别记录"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO scan_history (timestamp, category, title, summary)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, category, title, summary))
        conn.commit()
        conn.close()

    def get_recent_records(self, limit=10):
        """获取最近的记录"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT timestamp, category, title, summary 
            FROM scan_history 
            ORDER BY id DESC 
            LIMIT ?
        ''', (limit,))
        rows = c.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            records.append({
                "timestamp": row[0],
                "category": row[1],
                "title": row[2],
                "summary": row[3]
            })
        return records
