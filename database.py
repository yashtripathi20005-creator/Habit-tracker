"""
Database operations for the Habit Tracker
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from config import DB_PATH

class Database:
    """Handles all database operations for the habit tracker"""
    
    def __init__(self):
        """Initialize database connection and create tables if they don't exist"""
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create the necessary tables if they don't exist"""
        # Habits table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                frequency TEXT NOT NULL,
                target_days INTEGER,
                created_at DATE NOT NULL,
                updated_at DATE NOT NULL,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Habit completions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_date DATE NOT NULL,
                notes TEXT,
                FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
                UNIQUE(habit_id, completed_date)
            )
        ''')
        
        # Habit streaks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS streaks (
                habit_id INTEGER PRIMARY KEY,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_completed_date DATE,
                FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    def add_habit(self, name: str, description: str, category: str, 
                  frequency: str, target_days: int = None) -> int:
        """Add a new habit and return its ID"""
        today = date.today().isoformat()
        self.cursor.execute('''
            INSERT INTO habits (name, description, category, frequency, target_days, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, category, frequency, target_days, today, today))
        
        habit_id = self.cursor.lastrowid
        
        # Initialize streak record
        self.cursor.execute('''
            INSERT INTO streaks (habit_id, current_streak, longest_streak)
            VALUES (?, 0, 0)
        ''', (habit_id,))
        
        self.conn.commit()
        return habit_id
    
    def get_all_habits(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all habits, optionally only active ones"""
        query = '''
            SELECT h.*, 
                   COALESCE(s.current_streak, 0) as current_streak,
                   COALESCE(s.longest_streak, 0) as longest_streak,
                   COUNT(c.id) as total_completions
            FROM habits h
            LEFT JOIN streaks s ON h.id = s.habit_id
            LEFT JOIN completions c ON h.id = c.habit_id
        '''
        
        if active_only:
            query += " WHERE h.active = 1"
        
        query += " GROUP BY h.id ORDER BY h.name"
        
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in self.cursor.description]
        
        habits = []
        for row in rows:
            habit = dict(zip(columns, row))
            habits.append(habit)
        
        return habits
    
    def get_habit(self, habit_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific habit by ID"""
        self.cursor.execute('''
            SELECT h.*, 
                   COALESCE(s.current_streak, 0) as current_streak,
                   COALESCE(s.longest_streak, 0) as longest_streak
            FROM habits h
            LEFT JOIN streaks s ON h.id = s.habit_id
            WHERE h.id = ?
        ''', (habit_id,))
        
        row = self.cursor.fetchone()
        if row:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, row))
        return None
    
    def update_habit(self, habit_id: int, **kwargs) -> bool:
        """Update habit fields"""
        allowed_fields = ['name', 'description', 'category', 'frequency', 'target_days', 'active']
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        values.append(habit_id)
        values.append(date.today().isoformat())
        updates.append("updated_at = ?")
        
        query = f"UPDATE habits SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()
        return True
    
    def delete_habit(self, habit_id: int) -> bool:
        """Delete a habit and all associated data"""
        self.cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        self.conn.commit()
        return True
    
    def mark_completed(self, habit_id: int, notes: str = "") -> bool:
        """Mark a habit as completed for today"""
        today = date.today().isoformat()
        
        try:
            # Check if already completed today
            self.cursor.execute('''
                SELECT id FROM completions 
                WHERE habit_id = ? AND completed_date = ?
            ''', (habit_id, today))
            
            if self.cursor.fetchone():
                return False  # Already completed today
            
            # Add completion
            self.cursor.execute('''
                INSERT INTO completions (habit_id, completed_date, notes)
                VALUES (?, ?, ?)
            ''', (habit_id, today, notes))
            
            # Update streak
            self._update_streak(habit_id)
            
            self.conn.commit()
            return True
        
        except sqlite3.IntegrityError:
            return False
    
    def _update_streak(self, habit_id: int):
        """Update streak for a habit"""
        # Get habit frequency
        self.cursor.execute("SELECT frequency FROM habits WHERE id = ?", (habit_id,))
        result = self.cursor.fetchone()
        if not result:
            return
        
        frequency = result[0]
        
        # Get last completion date
        self.cursor.execute('''
            SELECT completed_date FROM completions 
            WHERE habit_id = ? 
            ORDER BY completed_date DESC 
            LIMIT 1
        ''', (habit_id,))
        
        result = self.cursor.fetchone()
        if not result:
            # First completion
            self.cursor.execute('''
                UPDATE streaks 
                SET current_streak = 1, longest_streak = 1, last_completed_date = ?
                WHERE habit_id = ?
            ''', (date.today().isoformat(), habit_id))
            return
        
        last_date = datetime.strptime(result[0], '%Y-%m-%d').date()
        today = date.today()
        days_diff = (today - last_date).days
        
        # Get current streak
        self.cursor.execute('''
            SELECT current_streak, longest_streak FROM streaks WHERE habit_id = ?
        ''', (habit_id,))
        current_streak, longest_streak = self.cursor.fetchone()
        
        # Determine if streak continues
        if frequency == "daily" and days_diff == 1:
            current_streak += 1
        elif frequency == "weekly" and days_diff <= 7:
            current_streak += 1
        elif frequency == "monthly" and days_diff <= 30:
            current_streak += 1
        elif days_diff > self._get_frequency_days(frequency):
            current_streak = 1
        else:
            current_streak = 1
        
        # Update longest streak
        if current_streak > longest_streak:
            longest_streak = current_streak
        
        # Save streak
        self.cursor.execute('''
            UPDATE streaks 
            SET current_streak = ?, longest_streak = ?, last_completed_date = ?
            WHERE habit_id = ?
        ''', (current_streak, longest_streak, today.isoformat(), habit_id))
    
    def _get_frequency_days(self, frequency: str) -> int:
        """Get the number of days for a frequency type"""
        from config import FREQUENCIES
        return FREQUENCIES.get(frequency, 1)
    
    def get_completions(self, habit_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get completions for a habit"""
        self.cursor.execute('''
            SELECT completed_date, notes, created_at 
            FROM completions 
            WHERE habit_id = ? 
            ORDER BY completed_date DESC 
            LIMIT ?
        ''', (habit_id, days))
        
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        
        completions = []
        for row in rows:
            completion = dict(zip(columns, row))
            completions.append(completion)
        
        return completions
    
    def get_habits_by_frequency(self, frequency: str) -> List[Dict[str, Any]]:
        """Get habits by frequency"""
        self.cursor.execute('''
            SELECT * FROM habits 
            WHERE frequency = ? AND active = 1
            ORDER BY name
        ''', (frequency,))
        
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        
        habits = []
        for row in rows:
            habits.append(dict(zip(columns, row)))
        
        return habits
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        stats = {}
        
        # Total habits
        self.cursor.execute("SELECT COUNT(*) FROM habits WHERE active = 1")
        stats['total_habits'] = self.cursor.fetchone()[0]
        
        # Total completions today
        today = date.today().isoformat()
        self.cursor.execute('''
            SELECT COUNT(*) FROM completions WHERE completed_date = ?
        ''', (today,))
        stats['today_completions'] = self.cursor.fetchone()[0]
        
        # Completion rate (last 30 days)
        thirty_days_ago = (date.today() - datetime.timedelta(days=30)).isoformat()
        self.cursor.execute('''
            SELECT COUNT(DISTINCT completed_date) FROM completions 
            WHERE completed_date >= ?
        ''', (thirty_days_ago,))
        stats['active_days'] = self.cursor.fetchone()[0]
        
        # Average streaks
        self.cursor.execute('''
            SELECT AVG(current_streak), MAX(longest_streak) FROM streaks
        ''')
        avg_streak, max_streak = self.cursor.fetchone()
        stats['avg_streak'] = round(avg_streak or 0, 1)
        stats['max_streak'] = max_streak or 0
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.conn.close()
