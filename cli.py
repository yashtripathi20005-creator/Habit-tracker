"""
Command Line Interface for the Habit Tracker
"""

import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from habit_tracker import HabitTracker
from config import COLORS, CATEGORIES, WELCOME_MESSAGE, HELP_MESSAGE, FREQUENCIES

class HabitTrackerCLI:
    """Command Line Interface for the habit tracker"""
    
    def __init__(self):
        """Initialize the CLI with habit tracker instance"""
        self.tracker = HabitTracker()
        self.running = True
    
    def run(self):
        """Main loop for the CLI"""
        self.clear_screen()
        self.print_colored(WELCOME_MESSAGE, "CYAN")
        print("\nType 'help' to see available commands\n")
        
        while self.running:
            try:
                command = self.get_input("> ", "WHITE").strip().lower()
                self.handle_command(command)
            except KeyboardInterrupt:
                print("\n")
                break
            except Exception as e:
                self.print_colored(f"❌ Error: {e}", "RED")
    
    def handle_command(self, command: str):
        """Handle user commands"""
        commands = {
            'list': self.list_habits,
            'add': self.add_habit,
            'check': self.check_habit,
            'stats': self.show_stats,
            'view': self.view_habit,
            'edit': self.edit_habit,
            'delete': self.delete_habit,
            'progress': self.show_progress,
            'history': self.show_history,
            'help': self.show_help,
            'exit': self.exit_app,
            'quit': self.exit_app
        }
        
        if command in commands:
            commands[command]()
        else:
            self.print_colored(f"❌ Unknown command: {command}", "RED")
            self.print_colored("Type 'help' for available commands", "YELLOW")
    
    def list_habits(self):
        """List all habits with their status"""
        habits = self.tracker.get_all_habits()
        
        if not habits:
            self.print_colored("\n📭 No habits found. Add one with 'add' command!\n", "YELLOW")
            return
        
        self.print_colored("\n📋 Your Habits:\n", "BOLD")
        self.print_colored("─" * 70, "WHITE")
        
        # Header
        print(f"{'ID':<4} {'Name':<20} {'Frequency':<10} {'Streak':<10} {'Today':<8} {'Status':<10}")
        self.print_colored("─" * 70, "WHITE")
        
        today = date.today().isoformat()
        
        for habit in habits:
            # Check if completed today
            completions = self.tracker.get_completions(habit['id'], 1)
            completed_today = any(c['completed_date'] == today for c in completions)
            
            status = "✅ Done" if completed_today else "⏳ Pending"
            status_color = "GREEN" if completed_today else "YELLOW"
            
            streak_display = f"🔥 {habit['current_streak']}" if habit['current_streak'] > 0 else "0"
            
            print(f"{habit['id']:<4} {habit['name'][:20]:<20} "
                  f"{habit['frequency']:<10} {streak_display:<10} "
                  f"{'✅' if completed_today else '⬜':<8} ", end="")
            self.print_colored(status, status_color)
        
        self.print_colored("─" * 70, "WHITE")
        print(f"Total: {len(habits)} active habits\n")
    
    def add_habit(self):
        """Add a new habit"""
        self.print_colored("\n➕ Add New Habit\n", "BOLD")
        self.print_colored("─" * 40, "WHITE")
        
        # Name
        name = self.get_input("Habit name: ", "CYAN")
        if not name.strip():
            self.print_colored("❌ Habit name cannot be empty", "RED")
            return
        
        # Description
        description = self.get_input("Description (optional): ", "CYAN")
        
        # Category
        self.print_colored("\nAvailable categories:", "WHITE")
        for i, cat in enumerate(CATEGORIES, 1):
            print(f"  {i}. {cat}")
        cat_choice = self.get_input("\nSelect category (1-7): ", "CYAN")
        
        try:
            cat_index = int(cat_choice) - 1
            if cat_index < 0 or cat_index >= len(CATEGORIES):
                category = "Other"
            else:
                category = CATEGORIES[cat_index]
        except ValueError:
            category = "Other"
        
        # Frequency
        self.print_colored("\nFrequency:", "WHITE")
        print("  1. Daily")
        print("  2. Weekly")
        print("  3. Monthly")
        
        freq_choice = self.get_input("Select frequency (1-3): ", "CYAN")
        
        freq_map = {'1': 'daily', '2': 'weekly', '3': 'monthly'}
        frequency = freq_map.get(freq_choice, 'daily')
        
        # Target days
        target_days = None
        if frequency != 'daily':
            try:
                target_input = self.get_input(f"Target days per {frequency} (optional): ", "CYAN")
                if target_input.strip():
                    target_days = int(target_input)
            except ValueError:
                self.print_colored("⚠️  Invalid number, skipping target days", "YELLOW")
        
        # Confirm
        self.print_colored("\n📝 Summary:", "BOLD")
        print(f"  Name: {name}")
        print(f"  Description: {description or 'None'}")
        print(f"  Category: {category}")
        print(f"  Frequency: {frequency}")
        if target_days:
            print(f"  Target: {target_days} days per {frequency}")
        
        confirm = self.get_input("\nAdd this habit? (y/n): ", "CYAN").lower()
        
        if confirm != 'y':
            self.print_colored("❌ Habit creation cancelled", "YELLOW")
            return
        
        try:
            habit_id = self.tracker.add_habit(name, description, category, frequency, target_days)
            self.print_colored(f"✅ Habit added successfully! (ID: {habit_id})", "GREEN")
        except Exception as e:
            self.print_colored(f"❌ Failed to add habit: {e}", "RED")
    
    def check_habit(self):
        """Mark a habit as completed"""
        self.print_colored("\n✅ Mark Habit as Done\n", "BOLD")
        self.print_colored("─" * 40, "WHITE")
        
        # Show habits
        habits = self.tracker.get_all_habits()
        if not habits:
            self.print_colored("📭 No habits available", "YELLOW")
            return
        
        self.print_colored("\nActive habits:", "WHITE")
        for habit in habits:
            print(f"  {habit['id']}. {habit['name']} ({habit['frequency']})")
        
        habit_id = self.get_input("\nEnter habit ID: ", "CYAN")
        
        try:
            habit_id = int(habit_id)
        except ValueError:
            self.print_colored("❌ Invalid ID", "RED")
            return
        
        # Check if habit exists
        habit = self.tracker.get_habit(habit_id)
        if not habit:
            self.print_colored("❌ Habit not found", "RED")
            return
        
        # Check if already completed today
        today = date.today().isoformat()
        completions = self.tracker.get_completions(habit_id, 1)
        if any(c['completed_date'] == today for c in completions):
            self.print_colored("⚠️  This habit is already completed today!", "YELLOW")
            return
        
        # Notes
        notes = self.get_input("Notes (optional): ", "CYAN")
        
        # Confirm
        self.print_colored(f"\nMark '{habit['name']}' as completed today?", "BOLD")
        confirm = self.get_input("Confirm (y/n): ", "CYAN").lower()
        
        if confirm != 'y':
            self.print_colored("❌ Cancelled", "YELLOW")
            return
        
        success = self.tracker.mark_completed(habit_id, notes)
        if success:
            self.print_colored(f"✅ '{habit['name']}' marked as completed! 🎉", "GREEN")
        else:
            self.print_colored("❌ Failed to mark habit as completed", "RED")
    
    def show_stats(self):
        """Show habit statistics"""
        self.print_colored("\n📊 Statistics\n", "BOLD")
        self.print_colored("─" * 50, "WHITE")
        
        stats = self.tracker.get_statistics()
        
        print(f"📌 Total active habits: {stats['total_habits']}")
        print(f"✅ Completed today: {stats['today_completions']}")
        print(f"📅 Active days (last 30): {stats['active_days']}/30")
        print(f"📈 Average streak: {stats['avg_streak']} days")
        print(f"🏆 Longest streak: {stats['max_streak']} days")
        
        # Weekly summary
        self.print_colored("\n📅 Weekly Summary\n", "BOLD")
        self.print_colored("─" * 50, "WHITE")
        
        weekly = self.tracker.get_weekly_summary()
        if not weekly:
            self.print_colored("No data available for this week", "YELLOW")
            return
        
        for habit_name, data in weekly.items():
            print(f"  {habit_name}:")
            print(f"    Completions: {data['total']}/7")
            print(f"    Current streak: {data['streak']} days")
            if data['completed_days']:
                days = [datetime.strptime(d, '%Y-%m-%d').strftime('%a') for d in data['completed_days']]
                print(f"    Done on: {', '.join(days)}")
    
    def view_habit(self):
        """View details of a specific habit"""
        self.print_colored("\n🔍 View Habit\n", "BOLD")
        self.print_colored("─" * 40, "WHITE")
        
        habits = self.tracker.get_all_habits()
        if not habits:
            self.print_colored("📭 No habits available", "YELLOW")
            return
        
        self.print_colored("\nActive habits:", "WHITE")
        for habit in habits:
            print(f"  {habit['id']}. {habit['name']}")
        
        habit_id = self.get_input("\nEnter habit ID: ", "CYAN")
        
        try:
            habit_id = int(habit_id)
        except ValueError:
            self.print_colored("❌ Invalid ID", "RED")
            return
        
        habit = self.tracker.get_habit(habit_id)
        if not habit:
            self.print_colored("❌ Habit not found", "RED")
            return
        
        self.print_colored(f"\n📋 {habit['name']}\n", "BOLD")
        self.print_colored("─" * 50, "WHITE")
        print(f"  ID: {habit['id']}")
        print(f"  Description: {habit['description'] or 'None'}")
        print(f"  Category: {habit['category']}")
        print(f"  Frequency: {habit['frequency']}")
        print(f"  Target days: {habit['target_days'] or 'N/A'}")
        print(f"  Created: {habit['created_at']}")
        print(f"  Updated: {habit['updated_at']}")
        print(f"  Active: {'Yes' if habit['active'] else 'No'}")
        print(f"  Current streak: {habit['current_streak']} days")
        print(f"  Longest streak: {habit['longest_streak']} days")
    
    def edit_habit(self):
        """Edit an existing habit"""
        self.print_colored("\n✏️ Edit Habit\n", "BOLD")
        self.print_colored("─" * 40, "WHITE")
        
        habits = self.tracker.get_all_habits()
        if not habits:
            self.print_colored("📭 No habits available", "YELLOW")
            return
        
        self.print_colored("\nActive habits:", "WHITE")
        for habit in habits:
            print(f"  {habit['id']}. {habit['name']}")
        
        habit_id = self.get_input("\nEnter habit ID to edit: ", "CYAN")
        
        try:
            habit_id = int(habit_id)
        except ValueError:
            self.print_colored("❌ Invalid ID", "RED")
            return
        
        habit = self.tracker.get_habit(habit_id)
        if not habit:
            self.print_colored("❌ Habit not found", "RED")
            return
        
        self.print_colored(f"\nEditing: {habit['name']}", "BOLD")
        self.print_colored("Leave blank to keep current value\n", "YELLOW")
        
        # Edit fields
        name = self.get_input(f"Name ({habit['name']}): ", "CYAN") or habit['name']
        description = self.get_input(f"Description ({habit['description'] or 'None'}): ", "CYAN")
        description = description if description else habit['description']
        
        self.print_colored("\nCategories:", "WHITE")
        for i, cat in enumerate(CATEGORIES, 1):
            print(f"  {i}. {cat}")
        cat_choice = self.get_input(f"Category ({habit['category']}): ", "CYAN")
        try:
            cat_index = int(cat_choice) - 1
            category = CATEGORIES[cat_index] if 0 <= cat_index < len(CATEGORIES) else habit['category']
        except ValueError:
            category = habit['category']
        
        self.print_colored("\nFrequency:", "WHITE")
        print("  1. Daily")
        print("  2. Weekly")
        print("  3. Monthly")
        freq_choice = self.get_input(f"Frequency ({habit['frequency']}): ", "CYAN")
        freq_map = {'1': 'daily', '2': 'weekly', '3': 'monthly'}
        frequency = freq_map.get(freq_choice, habit['frequency'])
        
        # Confirm
        self.print_colored("\n📝 Updated Summary:", "BOLD")
        print(f"  Name: {name}")
        print(f"  Description: {description}")
        print(f"  Category: {category}")
        print(f"  Frequency: {frequency}")
        
        confirm = self.get_input("\nSave changes? (y/n): ", "CYAN").lower()
        
        if confirm != 'y':
            self.print_colored("❌ Edit cancelled", "YELLOW")
            return
        
        success = self.tracker.update_habit(
            habit_id,
            name=name,
            description=description,
            category=category,
            frequency=frequency
        )
        
        if success:
            self.print_colored("✅ Habit updated successfully!", "GREEN")
        else:
            self.print_colored("❌ Failed to update habit", "RED")
    
    def delete_habit(self):
        """Delete a habit"""
        self.print_colored("\n🗑️ Delete Habit\n", "BOLD")
        self.print_colored("─" * 40, "WHITE")
        
        habits = self.tracker.get_all_habits()
        if not habits:
            self.print_colored("📭 No habits available", "YELLOW")
            return
        
        self.print_colored("\nActive habits:", "WHITE")
        for habit in habits:
            print(f"  {habit['id']}. {habit['name']}")
        
        habit_id = self.get_input("\nEnter habit ID to delete: ", "CYAN")
        
        try:
            habit_id = int(habit_id)
        except ValueError:
            self.print_colored("❌ Invalid ID", "RED")
            return
        
        habit = self.tracker.get_habit(habit_id)
        if not habit:
            self.print_colored("❌ Habit not found", "RED")
            return
        
        self.print_colored(f"\n⚠️  Are you sure you want to delete '{habit['name']}'?", "RED")
        self.print_colored("This action cannot be undone!", "RED")
        
        confirm = self.get_input("\nDelete habit? (y/n): ", "CYAN").lower()
        
        if confirm != 'y':
            self.print_colored("❌ Deletion cancelled", "YELLOW")
            return
        
        success = self.tracker.delete_habit(habit_id)
        if success:
            self.print_colored("✅ Habit deleted successfully!", "GREEN")
        else:
            self.print_colored("❌ Failed to delete habit", "RED")
    
    def show_progress(self):
        """Show progress chart for a habit"""
        self.print_colored("\n📈 Progress Chart\n", "BOLD")
        self.print_colored("─" * 40, "WHITE")
        
        habits = self.tracker.get_all_habits()
        if not habits:
            self.print_colored("📭 No habits available", "YELLOW")
            return
        
        self.print_colored("\nActive habits:", "WHITE")
        for habit in habits:
            print(f"  {habit['id']}. {habit['name']}")
        
        habit_id = self.get_input("\nEnter habit ID: ", "CYAN")
        
        try:
            habit_id = int(habit_id)
        except ValueError:
            self.print_colored("❌ Invalid ID", "RED")
            return
        
        period_days = 30
        try:
            days_input = self.get_input("Number of days to show (default 30): ", "CYAN")
            if days_input.strip():
                period_days = int(days_input)
        except ValueError:
            pass
        
        progress = self.tracker.get_habit_progress(habit_id, period_days)
        if not progress:
            self.print_colored("❌ Habit not found", "RED")
            return
        
        habit = progress['habit']
        self.print_colored(f"\n📊 Progress for: {habit['name']}", "BOLD")
        print(f"  Completion rate: {progress['completion_rate']:.1f}%")
        print(f"  Total completions: {progress['completion_count']}")
        print(f"  Current streak: {habit['current_streak']} days")
        print(f"  Longest streak: {habit['longest_streak']} days")
        
        # Simple visual progress chart
        self.print_colored("\nLast 30 days:", "WHITE")
        self.print_colored("─" * 50, "WHITE")
        
        # Create a simple bar chart
        for i, data in enumerate(progress['progress'][-30:]):
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
            date_str = date_obj.strftime('%d')
            symbol = "█" if data['completed'] else "░"
            color = "GREEN" if data['completed'] else "WHITE"
            
            # Show day number and symbol
            day_display = f"{date_str:>2}"
            print(f"{day_display} ", end="")
            self.print_colored(f"{symbol} ", color)
        
        print("\n")
        self.print_colored("█ = Completed   ░ = Not completed", "WHITE")
    
    def show_history(self):
        """Show completion history for a habit"""
        self.print_colored("\n📅 Habit History\n", "BOLD")
        self.print_colored("─" * 40, "WHITE")
        
        habits = self.tracker.get_all_habits()
        if not habits:
            self.print_colored("📭 No habits available", "YELLOW")
            return
        
        self.print_colored("\nActive habits:", "WHITE")
        for habit in habits:
            print(f"  {habit['id']}. {habit['name']}")
        
        habit_id = self.get_input("\nEnter habit ID: ", "CYAN")
        
        try:
            habit_id = int(habit_id)
        except ValueError:
            self.print_colored("❌ Invalid ID", "RED")
            return
        
        habit = self.tracker.get_habit(habit_id)
        if not habit:
            self.print_colored("❌ Habit not found", "RED")
            return
        
        days = 30
        try:
            days_input = self.get_input("Number of days of history (default 30): ", "CYAN")
            if days_input.strip():
                days = int(days_input)
        except ValueError:
            pass
        
        completions = self.tracker.get_completions(habit_id, days)
        
        self.print_colored(f"\n📋 History for: {habit['name']}", "BOLD")
        self.print_colored("─" * 50, "WHITE")
        
        if not completions:
            self.print_colored("No completions recorded yet", "YELLOW")
            return
        
        for completion in completions:
            date_obj = datetime.strptime(completion['completed_date'], '%Y-%m-%d')
            date_str = date_obj.strftime('%Y-%m-%d %A')
            notes = completion['notes'] or "No notes"
            print(f"  {date_str}")
            print(f"    Notes: {notes}")
    
    def show_help(self):
        """Show help message"""
        self.print_colored(HELP_MESSAGE, "CYAN")
    
    def exit_app(self):
        """Exit the application"""
        self.print_colored("\n👋 Goodbye! Keep building those habits!", "GREEN")
        self.running = False
        self.tracker.close()
    
    def get_input(self, prompt: str, color: str = "WHITE") -> str:
        """Get user input with colored prompt"""
        color_code = COLORS.get(color, COLORS["WHITE"])
        print(f"{color_code}{prompt}{COLORS['RESET']}", end="")
        return input()
    
    def print_colored(self, message: str, color: str = "WHITE"):
        """Print colored message"""
        color_code = COLORS.get(color, COLORS["WHITE"])
        print(f"{color_code}{message}{COLORS['RESET']}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
