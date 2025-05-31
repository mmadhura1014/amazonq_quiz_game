# Knowledge Quest - Quiz Game

A Pygame-based educational quiz game designed for 17-year-old students.

## Features

- 10 questions per quiz (5 easy, 3 medium, 2 difficult)
- Questions from multiple categories: Physics, Chemistry, Mathematics, Biology, Social Science, Computer Science
- Player name tracking and score history
- Performance evaluation based on score
- Attractive and intuitive user interface

## Requirements

- Python 3.6+
- Pygame
- PyYAML

## Installation

1. Make sure you have Python installed on your system
2. Install the required packages:
   ```
   pip install pygame pyyaml
   ```
3. Clone or download this repository

## How to Play

1. Run the game:
   ```
   python quiz_game.py
   ```
2. Enter your name on the main menu
3. Click "Start Quiz" to begin
4. Answer each question by clicking on the correct option
5. View your results at the end of the quiz
6. Choose to play again or quit

## Scoring System

- 8-10 correct answers: Excellent
- 6-7 correct answers: Good
- 0-5 correct answers: Keep practicing

## Game Structure

- `quiz_game.py`: Main game file with Pygame implementation
- `questions.yaml`: Database of questions organized by category and difficulty
- `player_records.json`: Automatically generated file to store player scores and history

## Customization

You can modify the questions in the `questions.yaml` file to add new questions or change existing ones. Follow the same format:

```yaml
categories:
  Category_Name:
    easy/medium/difficult:
      - question: "Question text"
        options: ["Option 1", "Option 2", "Option 3", "Option 4"]
        correct: "Correct option"
```

## Future Enhancements

- Time limit for questions
- Sound effects and background music
- More categories and questions
- Difficulty selection
- Multiplayer mode