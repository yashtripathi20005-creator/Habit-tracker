"""
Core habit tracker logic
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from database import Database
from models import Habit, Completion, Streak

class HabitTracker:
    """Main habit tracker class that handles all business logic"""
    
    def __init__(self):
        """Initialize the habit tracker with database connection"""
        self.db = Database()
    
    def add_habit(self, name: str, description: str, category: str, 
                  frequency: str, target_days: int = None) -> int:
        """
        Add a new habit
        
        Args:
            name: Habit name
            description: Habit description
            category: Habit category
            frequency: daily, weekly, or monthly
            target_days: Target days per period (optional)
        
        Returns:
            The ID of the newly created habit
        """
        if not name or not name.strip():
            raise ValueError("Habit name cannot be empty")
        
        if frequency not in ['daily', 'weekly', 'monthly']:
            raise ValueError("Frequency must be daily, weekly, or monthly")
        
        return self.db.add_habit(
            name.strip(),
            description.strip(),
            category,
            frequency,
            target_days
        )
    
    def get_all_habits(self) -> List[Dict[str, Any]]:
        """Get all active habits with their current streaks"""
        return self.db.get_all_habits(active_only=True)
    
    def get_habit(self, habit_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific habit by ID"""
        return self.db.get_habit(habit_id)
    
    def update_habit(self, habit_id: int, **kwargs) -> bool:
        """Update an existing habit"""
        return self.db.update_habit(habit_id, **kwargs)
    
    def delete_habit(self, habit_id: int) -> bool:
        """Delete a habit"""
        return self.db.delete_habit(habit_id)
    
    def mark_completed(self, habit_id: int, notes: str = "") -> bool:
        """Mark a habit as completed today"""
        return self.db.mark_completed(habit_id, notes)
    
    def get_completions(self, habit_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get completion history for a habit"""
        return self.db.get_completions(habit_id, days)
    
    def get_habits_by_frequency(self, frequency: str) -> List[Dict[str, Any]]:
        """Get habits filtered by frequency"""
        return self.db.get_habits_by_frequency(frequency)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        return self.db.get_statistics()
    
    def get_habit_progress(self, habit_id: int, period_days: int = 30) -> Dict[str, Any]:
        """Get progress data for a habit"""
        habit = self.get_habit(habit_id)
        if not habit:
            return {}
        
        completions = self.get_completions(habit_id, period_days)
        
        # Create a list of dates in the period
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        
        progress_data = []
        for i in range(period_days + 1):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.isoformat()
            
            # Check if completed on this date
            completed = any(c['completed_date'] == date_str for c in completions)
            
            progress_data.append({
                'date': date_str,
                'completed': completed
            })
        
        return {
            'habit': habit,
            'progress': progress_data,
            'completion_count': len(completions),
            'completion_rate': len(completions) / period_days * 100
        }
    
    def get_weekly_summary(self) -> Dict[str, Any]:
        """Get a summary of the last 7 days"""
        habits = self.get_all_habits()
        summary = {}
        
        for habit in habits:
            completions = self.get_completions(habit['id'], 7)
            summary[habit['name']] = {
                'total': len(completions),
                'completed_days': [c['completed_date'] for c in completions],
                'streak': habit['current_streak']
            }
        
        return summary
    
    def close(self):
        """Clean up resources"""
        self.db.close()
