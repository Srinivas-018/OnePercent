# OnePercent - Personal Habit Tracker

A simple and effective command-line habit tracker to help you improve 1% every day! 🚀

## Features

- ✅ **Add Habits**: Create custom habits you want to track
- 📅 **Daily Tracking**: Mark habits as complete each day
- 🔥 **Streak Tracking**: Monitor your current and longest streaks
- 📊 **Statistics**: View completion rates and progress
- 💾 **Persistent Storage**: All data saved locally in JSON format

## Installation

No external dependencies required! Just Python 3.6 or higher.

```bash
git clone https://github.com/Srinivas-018/OnePercent.git
cd OnePercent
```

## Usage

Run the habit tracker:

```bash
python3 habit_tracker.py
```

### Menu Options

1. **Add a new habit** - Create a habit you want to track
2. **Complete a habit for today** - Mark a habit as done for today
3. **View all habits** - See all your habits with streaks and stats
4. **View habit details** - Get detailed information about a specific habit
5. **Delete a habit** - Remove a habit you no longer want to track
6. **Exit** - Close the application

## Example

```bash
$ python3 habit_tracker.py

==================================================
       Personal Habit Tracker - OnePercent       
==================================================

1. Add a new habit
2. Complete a habit for today
3. View all habits
4. View habit details
5. Delete a habit
6. Exit
--------------------------------------------------

Enter your choice (1-6): 1
Enter habit name: Exercise
Enter habit description (optional): 30 minutes of exercise
✓ Habit 'Exercise' added successfully!
```

## Data Storage

All habit data is stored in `habits.json` in the same directory as the script. The file is created automatically when you add your first habit.

## Philosophy

Inspired by the concept of improving 1% every day, this tracker helps you build and maintain positive habits consistently. Small daily improvements compound into significant results over time!

## License

MIT License - Feel free to use and modify as you wish!