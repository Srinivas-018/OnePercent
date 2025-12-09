#!/usr/bin/env python3
"""
Personal Habit Tracker - Track your daily habits and build streaks
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class HabitTracker:
    """Main class for managing habits and tracking completions"""
    
    def __init__(self, data_file: str = "habits.json"):
        """Initialize the habit tracker with a data file"""
        self.data_file = data_file
        self.habits = self._load_habits()
    
    def _load_habits(self) -> Dict:
        """Load habits from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"habits": {}}
        return {"habits": {}}
    
    def _save_habits(self) -> None:
        """Save habits to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.habits, f, indent=2)
    
    def add_habit(self, name: str, description: str = "") -> bool:
        """Add a new habit to track"""
        if name in self.habits["habits"]:
            return False
        
        self.habits["habits"][name] = {
            "description": description,
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "completions": [],
            "current_streak": 0,
            "longest_streak": 0
        }
        self._save_habits()
        return True
    
    def complete_habit(self, name: str, date: Optional[str] = None) -> bool:
        """Mark a habit as completed for a specific date"""
        if name not in self.habits["habits"]:
            return False
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        habit = self.habits["habits"][name]
        if date not in habit["completions"]:
            habit["completions"].append(date)
            habit["completions"].sort()
            self._update_streaks(name)
            self._save_habits()
            return True
        return False
    
    def _update_streaks(self, name: str) -> None:
        """Update current and longest streak for a habit"""
        habit = self.habits["habits"][name]
        completions = sorted(habit["completions"])
        
        if not completions:
            habit["current_streak"] = 0
            habit["longest_streak"] = 0
            return
        
        # Calculate current streak
        current_streak = 0
        today = datetime.now().date()
        check_date = today
        
        for i in range(len(completions) - 1, -1, -1):
            completion_date = datetime.strptime(completions[i], "%Y-%m-%d").date()
            if completion_date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            elif completion_date < check_date:
                break
        
        # Calculate longest streak
        if len(completions) == 0:
            longest_streak = 0
        else:
            longest_streak = 1
            temp_streak = 1
            
            for i in range(1, len(completions)):
                prev_date = datetime.strptime(completions[i-1], "%Y-%m-%d").date()
                curr_date = datetime.strptime(completions[i], "%Y-%m-%d").date()
                
                if (curr_date - prev_date).days == 1:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1
            
            # Compare with current streak
            longest_streak = max(longest_streak, current_streak)
        
        habit["current_streak"] = current_streak
        habit["longest_streak"] = longest_streak
    
    def delete_habit(self, name: str) -> bool:
        """Delete a habit"""
        if name in self.habits["habits"]:
            del self.habits["habits"][name]
            self._save_habits()
            return True
        return False
    
    def list_habits(self) -> List[Dict]:
        """Get list of all habits with their stats"""
        result = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        for name, habit in self.habits["habits"].items():
            completed_today = today in habit["completions"]
            result.append({
                "name": name,
                "description": habit["description"],
                "created_date": habit["created_date"],
                "total_completions": len(habit["completions"]),
                "current_streak": habit["current_streak"],
                "longest_streak": habit["longest_streak"],
                "completed_today": completed_today
            })
        
        return result
    
    def get_habit_details(self, name: str) -> Optional[Dict]:
        """Get detailed information about a specific habit"""
        if name not in self.habits["habits"]:
            return None
        
        habit = self.habits["habits"][name]
        today = datetime.now().strftime("%Y-%m-%d")
        
        return {
            "name": name,
            "description": habit["description"],
            "created_date": habit["created_date"],
            "completions": habit["completions"],
            "total_completions": len(habit["completions"]),
            "current_streak": habit["current_streak"],
            "longest_streak": habit["longest_streak"],
            "completed_today": today in habit["completions"]
        }


def print_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("  Personal Habit Tracker - OnePercent".center(50))
    print("="*50)
    print("\n1. Add a new habit")
    print("2. Complete a habit for today")
    print("3. View all habits")
    print("4. View habit details")
    print("5. Delete a habit")
    print("6. Exit")
    print("-"*50)


def main():
    """Main CLI interface"""
    tracker = HabitTracker()
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            name = input("Enter habit name: ").strip()
            description = input("Enter habit description (optional): ").strip()
            
            if tracker.add_habit(name, description):
                print(f"✓ Habit '{name}' added successfully!")
            else:
                print(f"✗ Habit '{name}' already exists!")
        
        elif choice == "2":
            habits = tracker.list_habits()
            if not habits:
                print("No habits found. Add a habit first!")
                continue
            
            print("\nYour habits:")
            for i, habit in enumerate(habits, 1):
                status = "✓" if habit["completed_today"] else "○"
                print(f"{i}. {status} {habit['name']}")
            
            name = input("\nEnter habit name to complete: ").strip()
            if tracker.complete_habit(name):
                print(f"✓ Marked '{name}' as complete for today!")
            else:
                print(f"✗ Could not complete habit. Either it doesn't exist or already completed today.")
        
        elif choice == "3":
            habits = tracker.list_habits()
            if not habits:
                print("\nNo habits found. Add a habit first!")
                continue
            
            print("\n" + "="*70)
            print("  Your Habits".center(70))
            print("="*70)
            
            for habit in habits:
                status = "✓" if habit["completed_today"] else "○"
                print(f"\n{status} {habit['name']}")
                if habit["description"]:
                    print(f"   Description: {habit['description']}")
                print(f"   Streak: {habit['current_streak']} days (Longest: {habit['longest_streak']})")
                print(f"   Total completions: {habit['total_completions']}")
            
            print("-"*70)
        
        elif choice == "4":
            name = input("Enter habit name: ").strip()
            details = tracker.get_habit_details(name)
            
            if details:
                print("\n" + "="*50)
                print(f"  {details['name']}".center(50))
                print("="*50)
                if details["description"]:
                    print(f"Description: {details['description']}")
                print(f"Created: {details['created_date']}")
                print(f"Current Streak: {details['current_streak']} days")
                print(f"Longest Streak: {details['longest_streak']} days")
                print(f"Total Completions: {details['total_completions']}")
                print(f"Completed Today: {'Yes' if details['completed_today'] else 'No'}")
                
                if details["completions"]:
                    print(f"\nRecent completions (last 10):")
                    for date in details["completions"][-10:]:
                        print(f"  - {date}")
                print("-"*50)
            else:
                print(f"✗ Habit '{name}' not found!")
        
        elif choice == "5":
            name = input("Enter habit name to delete: ").strip()
            confirm = input(f"Are you sure you want to delete '{name}'? (yes/no): ").strip().lower()
            
            if confirm == "yes":
                if tracker.delete_habit(name):
                    print(f"✓ Habit '{name}' deleted successfully!")
                else:
                    print(f"✗ Habit '{name}' not found!")
            else:
                print("Deletion cancelled.")
        
        elif choice == "6":
            print("\nThank you for using Personal Habit Tracker!")
            print("Keep improving 1% every day! 🚀")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()
