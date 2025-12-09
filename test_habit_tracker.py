#!/usr/bin/env python3
"""
Unit tests for Personal Habit Tracker
"""

import unittest
import os
import json
from datetime import datetime, timedelta
from habit_tracker import HabitTracker


class TestHabitTracker(unittest.TestCase):
    """Test cases for HabitTracker class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.test_file = "test_habits.json"
        self.tracker = HabitTracker(self.test_file)
    
    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_add_habit_success(self):
        """Test adding a new habit successfully"""
        result = self.tracker.add_habit("Exercise", "30 minutes daily")
        self.assertTrue(result)
        habits = self.tracker.list_habits()
        self.assertEqual(len(habits), 1)
        self.assertEqual(habits[0]["name"], "Exercise")
        self.assertEqual(habits[0]["description"], "30 minutes daily")
    
    def test_add_duplicate_habit(self):
        """Test that adding a duplicate habit fails"""
        self.tracker.add_habit("Exercise", "30 minutes daily")
        result = self.tracker.add_habit("Exercise", "Different description")
        self.assertFalse(result)
        habits = self.tracker.list_habits()
        self.assertEqual(len(habits), 1)
    
    def test_complete_habit_success(self):
        """Test completing a habit successfully"""
        self.tracker.add_habit("Exercise", "30 minutes daily")
        result = self.tracker.complete_habit("Exercise")
        self.assertTrue(result)
        
        habit_details = self.tracker.get_habit_details("Exercise")
        self.assertTrue(habit_details["completed_today"])
        self.assertEqual(habit_details["total_completions"], 1)
    
    def test_complete_nonexistent_habit(self):
        """Test completing a habit that doesn't exist"""
        result = self.tracker.complete_habit("NonExistent")
        self.assertFalse(result)
    
    def test_complete_habit_twice_same_day(self):
        """Test that completing a habit twice on the same day doesn't double count"""
        self.tracker.add_habit("Exercise", "30 minutes daily")
        self.tracker.complete_habit("Exercise")
        result = self.tracker.complete_habit("Exercise")
        self.assertFalse(result)
        
        habit_details = self.tracker.get_habit_details("Exercise")
        self.assertEqual(habit_details["total_completions"], 1)
    
    def test_streak_calculation(self):
        """Test that streak is calculated correctly"""
        self.tracker.add_habit("Exercise", "30 minutes daily")
        
        # Complete habit for today and yesterday
        today = datetime.now()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        
        self.tracker.complete_habit("Exercise", yesterday)
        self.tracker.complete_habit("Exercise", today_str)
        
        habit_details = self.tracker.get_habit_details("Exercise")
        self.assertEqual(habit_details["current_streak"], 2)
        self.assertEqual(habit_details["longest_streak"], 2)
    
    def test_delete_habit_success(self):
        """Test deleting a habit successfully"""
        self.tracker.add_habit("Exercise", "30 minutes daily")
        result = self.tracker.delete_habit("Exercise")
        self.assertTrue(result)
        
        habits = self.tracker.list_habits()
        self.assertEqual(len(habits), 0)
    
    def test_delete_nonexistent_habit(self):
        """Test deleting a habit that doesn't exist"""
        result = self.tracker.delete_habit("NonExistent")
        self.assertFalse(result)
    
    def test_list_multiple_habits(self):
        """Test listing multiple habits"""
        self.tracker.add_habit("Exercise", "30 minutes daily")
        self.tracker.add_habit("Reading", "Read 20 pages")
        self.tracker.add_habit("Meditation", "10 minutes meditation")
        
        habits = self.tracker.list_habits()
        self.assertEqual(len(habits), 3)
        
        habit_names = [h["name"] for h in habits]
        self.assertIn("Exercise", habit_names)
        self.assertIn("Reading", habit_names)
        self.assertIn("Meditation", habit_names)
    
    def test_get_habit_details_nonexistent(self):
        """Test getting details for a nonexistent habit"""
        details = self.tracker.get_habit_details("NonExistent")
        self.assertIsNone(details)
    
    def test_data_persistence(self):
        """Test that data persists across tracker instances"""
        self.tracker.add_habit("Exercise", "30 minutes daily")
        self.tracker.complete_habit("Exercise")
        
        # Create new tracker instance with same file
        new_tracker = HabitTracker(self.test_file)
        habits = new_tracker.list_habits()
        
        self.assertEqual(len(habits), 1)
        self.assertEqual(habits[0]["name"], "Exercise")
        self.assertEqual(habits[0]["total_completions"], 1)
    
    def test_empty_tracker(self):
        """Test tracker with no habits"""
        habits = self.tracker.list_habits()
        self.assertEqual(len(habits), 0)
    
    def test_longest_streak_tracking(self):
        """Test that longest streak is tracked correctly"""
        self.tracker.add_habit("Exercise", "30 minutes daily")
        
        # Create a streak of 3 days in the past
        base_date = datetime.now() - timedelta(days=10)
        for i in range(3):
            date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            self.tracker.complete_habit("Exercise", date)
        
        # Create a current streak of 2 days
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        self.tracker.complete_habit("Exercise", yesterday)
        self.tracker.complete_habit("Exercise", today)
        
        habit_details = self.tracker.get_habit_details("Exercise")
        self.assertEqual(habit_details["current_streak"], 2)
        self.assertEqual(habit_details["longest_streak"], 3)


if __name__ == "__main__":
    unittest.main()
