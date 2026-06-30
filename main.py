"""
Habit Tracker - Main Entry Point
A terminal-based habit tracking application
"""

from cli import HabitTrackerCLI

def main():
    """Main entry point for the application"""
    try:
        app = HabitTrackerCLI()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Keep building those habits!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please restart the application.")

if __name__ == "__main__":
    main()
