"""
Data models for the Habit Tracker
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List

@dataclass
class Habit:
    """Represents a habit"""
    id: int
    name: str
    description: str
    category: str
    frequency: str
    target_days: Optional[int] = None
    created_at: date = None
    updated_at: date = None
    active: bool = True
    
    def __post_init__(self):
        """Convert string dates to date objects if needed"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(self.created_at, '%Y-%m-%d').date()
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.strptime(self.updated_at, '%Y-%m-%d').date()
    
    def is_due(self) -> bool:
        """Check if the habit is due today"""
        from config import FREQUENCIES
        # This would need to check completion history
        return True  # Placeholder
    
    def get_frequency_label(self) -> str:
        """Get a human-readable frequency label"""
        from config import FREQUENCIES
        return self.frequency.capitalize()

@dataclass
class Completion:
    """Represents a habit completion"""
    id: int
    habit_id: int
    completed_date: date
    notes: str = ""
    
    def __post_init__(self):
        """Convert string date to date object if needed"""
        if isinstance(self.completed_date, str):
            self.completed_date = datetime.strptime(self.completed_date, '%Y-%m-%d').date()

@dataclass
class Streak:
    """Represents a habit streak"""
    habit_id: int
    current_streak: int = 0
    longest_streak: int = 0
    last_completed_date: Optional[date] = None
    
    def __post_init__(self):
        """Convert string date to date object if needed"""
        if self.last_completed_date and isinstance(self.last_completed_date, str):
            self.last_completed_date = datetime.strptime(
                self.last_completed_date, '%Y-%m-%d'
            ).date()
