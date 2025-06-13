import sqlite3
from typing import List, Dict, Any
import json

def init_db():
    """Initialize the database and create necessary tables if they don't exist."""
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    
    # Create table for storing last day number
    c.execute('''
        CREATE TABLE IF NOT EXISTS last_day_number (
            phone TEXT PRIMARY KEY,
            day_number INTEGER NOT NULL
        )
    ''')
    
    # Create table for storing chat history
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            role TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_last_day_number(phone: str) -> int:
    """Get the last day number for a given phone number."""
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT day_number FROM last_day_number WHERE phone = ?', (phone,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def set_last_day_number(phone: str, day_number: int):
    """Set the last day number for a given phone number."""
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO last_day_number (phone, day_number)
        VALUES (?, ?)
    ''', (phone, day_number))
    conn.commit()
    conn.close()

def get_chat_history(phone: str) -> List[Dict[str, Any]]:
    """Get chat history for a given phone number."""
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''
        SELECT role, message 
        FROM chat_history 
        WHERE phone = ? 
        ORDER BY timestamp ASC
    ''', (phone,))
    history = [{'role': row[0], 'parts': row[1]} for row in c.fetchall()]
    conn.close()
    return history

def add_chat_message(phone: str, role: str, message: str):
    """Add a new message to the chat history."""
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO chat_history (phone, role, message)
        VALUES (?, ?, ?)
    ''', (phone, role, message))
    conn.commit()
    conn.close()

def clear_chat_history(phone: str):
    """Clear chat history for a given phone number."""
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('DELETE FROM chat_history WHERE phone = ?', (phone,))
    conn.commit()
    conn.close() 