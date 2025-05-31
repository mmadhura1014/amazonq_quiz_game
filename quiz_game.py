import pygame
import sys
import random
import yaml
import os
import json
from datetime import datetime

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (30, 30, 40)
LIGHT_GRAY = (60, 63, 75)
LIGHT_BLUE = (100, 180, 255)
DARK_BLUE = (50, 100, 200)
GREEN = (0, 200, 100)
RED = (255, 80, 80)
PURPLE = (180, 100, 240)
ORANGE = (255, 165, 0)
CYAN = (0, 200, 200)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The 6th Sense Quiz")

# Fallback to system fonts since we're having issues with custom fonts
font_large = pygame.font.SysFont('Arial', 40)
font_medium = pygame.font.SysFont('Arial', 28)
font_small = pygame.font.SysFont('Arial', 20)
font_instructions = pygame.font.SysFont('Arial', 24)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, LIGHT_BLUE, self.rect, 2, border_radius=10)
        
        # Changed text color to BLACK for better contrast on light backgrounds
        text_color = BLACK if self.color == WHITE else WHITE
        text_surface = font_medium.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class TextInput:
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                self.text += event.unicode
        return False
        
    def draw(self, surface):
        color = LIGHT_BLUE if self.active else LIGHT_GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, LIGHT_BLUE, self.rect, 2, border_radius=5)
        
        if self.text:
            text_surface = font_medium.render(self.text, True, WHITE)
        else:
            text_surface = font_medium.render(self.placeholder, True, GRAY)
            
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)

class QuizGame:
    def __init__(self):
        self.state = "menu"
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.player_name = ""
        self.selected_option = None
        self.question_answered = False
        self.categories = []
        self.selected_categories = []  # New: to store user-selected categories
        self.difficulty_counts = {"easy": 5, "medium": 3, "difficult": 2}
        self.player_records_file = "player_records.json"
        self.feedback_message = ""  # New: to store feedback messages
        self.feedback_color = WHITE  # New: color for feedback messages
        self.feedback_timer = 0  # New: timer for feedback messages
        self.load_questions()
        
        # Lists of encouraging and motivating messages
        self.correct_messages = [
            "Excellent! You nailed it!",
            "Well done! That's correct!",
            "Brilliant answer!",
            "You're on fire!",
            "Spot on! Keep it up!",
            "That's right! You're crushing it!",
            "Perfect! You're a natural!",
            "Correct! You're doing great!"
        ]
        
        self.incorrect_messages = [
            "Oops! Not quite right.",
            "Almost there! Keep going!",
            "Nice try! You'll get the next one!",
            "Don't worry, learning is a journey!",
            "That's not it, but keep your spirits up!",
            "Not correct, but you're still awesome!",
            "Wrong answer, but stay positive!",
            "Keep going! Mistakes help us learn!"
        ]
        
    def load_questions(self):
        with open("questions.yaml", "r") as file:
            data = yaml.safe_load(file)
            
        self.categories = list(data["categories"].keys())
        
    def select_questions(self):
        with open("questions.yaml", "r") as file:
            data = yaml.safe_load(file)
        
        selected_questions = []
        
        # If no categories are selected, use all categories
        categories_to_use = self.selected_categories if self.selected_categories else self.categories
        
        # Select questions based on difficulty distribution
        for difficulty, count in self.difficulty_counts.items():
            for _ in range(count):
                # Randomly select a category from user-selected categories
                if not categories_to_use:  # Safety check
                    category = random.choice(self.categories)
                else:
                    category = random.choice(categories_to_use)
                
                # Make sure the category has questions of this difficulty
                attempts = 0
                while (difficulty not in data["categories"][category] or 
                       not data["categories"][category][difficulty]) and attempts < 10:
                    if not categories_to_use:  # Safety check
                        category = random.choice(self.categories)
                    else:
                        category = random.choice(categories_to_use)
                    attempts += 1
                
                if attempts < 10:
                    # Select a random question from this category and difficulty
                    question = random.choice(data["categories"][category][difficulty])
                    question["category"] = category
                    question["difficulty"] = difficulty
                    
                    # Shuffle the options and track the correct answer
                    correct_answer = question["correct"]
                    options = question["options"].copy()
                    random.shuffle(options)
                    
                    # Update the question with shuffled options and new correct answer index
                    question["options"] = options
                    question["correct"] = correct_answer
                    
                    selected_questions.append(question)
                    
                    # Remove the question to avoid duplicates
                    data["categories"][category][difficulty].remove(question)
        
        # Shuffle the questions
        random.shuffle(selected_questions)
        self.questions = selected_questions
        
    def save_player_record(self):
        records = []
        if os.path.exists(self.player_records_file):
            try:
                with open(self.player_records_file, "r") as file:
                    records = json.load(file)
            except:
                records = []
        
        # Add new record
        records.append({
            "name": self.player_name,
            "score": self.score,
            "total_questions": len(self.questions),
            "categories": self.selected_categories if self.selected_categories else ["All"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Save records
        with open(self.player_records_file, "w") as file:
            json.dump(records, file, indent=4)
    
    def get_player_stats(self, name):
        if not os.path.exists(self.player_records_file):
            return {"games_played": 0, "average_score": 0, "best_score": 0}
        
        try:
            with open(self.player_records_file, "r") as file:
                records = json.load(file)
            
            player_records = [r for r in records if r["name"].lower() == name.lower()]
            
            if not player_records:
                return {"games_played": 0, "average_score": 0, "best_score": 0}
            
            games_played = len(player_records)
            average_score = sum(r["score"] for r in player_records) / games_played
            best_score = max(r["score"] for r in player_records)
            
            return {
                "games_played": games_played,
                "average_score": round(average_score, 1),
                "best_score": best_score
            }
        except:
            return {"games_played": 0, "average_score": 0, "best_score": 0}
    
    def draw_menu(self):
        screen.fill(DARK_GRAY)
        
        # Title - changed to LIGHT_BLUE and bold
        title = font_large.render("The 6th Sense Quiz", True, LIGHT_BLUE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Subtitle - changed to PURPLE and bold
        subtitle = font_medium.render("Six Fields. One Brain.", True, PURPLE)
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 100))
        
        # Create two columns with clear separation for instructions and stats
        left_column_x = 70
        right_column_x = 580  # Moved slightly left to give more room for category names
        
        # Left side - Instructions (moved up)
        instructions_title = font_medium.render("Instructions:", True, LIGHT_BLUE)
        screen.blit(instructions_title, (left_column_x, 170))
        
        instructions = [
            "• Answer 10 questions from selected subjects",
            "• Questions range from Easy to Difficult levels",
            "• If no categories selected, all subjects included",
            "• Scoring System:",
            "  • 8-10 correct: Excellent! Knowledge Master",
            "  • 6-7 correct: Good! Solid Understanding",
            "  • 0-5 correct: Keep Learning & Try Again"
        ]
        
        # Increased line spacing for instructions even more
        line_spacing = 35  # Increased from 30
        
        for i, line in enumerate(instructions):
            # Use different colors for scoring system
            if i >= 4:
                if i == 4:
                    color = GREEN
                elif i == 5:
                    color = ORANGE
                else:
                    color = RED
            else:
                color = WHITE  # All main instruction points are white now
                
            # Using larger font for instructions
            text = font_instructions.render(line, True, color)
            screen.blit(text, (left_column_x, 205 + i*line_spacing))
        
        # Name input (moved to right column)
        name_label = font_medium.render("Enter Your Name:", True, LIGHT_BLUE)
        screen.blit(name_label, (right_column_x, 170))
        
        # Adjust name input position
        self.name_input.rect.x = right_column_x
        self.name_input.rect.y = 205
        self.name_input.rect.width = 300
        self.name_input.draw(screen)
        
        # Category selection
        category_label = font_medium.render("Select Categories:", True, LIGHT_BLUE)
        screen.blit(category_label, (right_column_x, 270))
        
        # Draw category checkboxes with increased spacing and larger font
        checkbox_y = 320  # Increased from 300 to create more space between heading and categories
        category_spacing = 40  # Increased from 35 for more vertical space
        
        for i, category in enumerate(self.categories):
            # Determine position (2 columns)
            col = i % 2
            row = i // 2
            checkbox_x = right_column_x + col * 200  # Increased from 180 to provide more space
            current_y = checkbox_y + row * category_spacing
            
            # Draw checkbox (slightly larger)
            checkbox_rect = pygame.Rect(checkbox_x, current_y, 24, 24)  # Increased from 20x20
            pygame.draw.rect(screen, LIGHT_GRAY, checkbox_rect)
            pygame.draw.rect(screen, LIGHT_BLUE, checkbox_rect, 2)
            
            # Fill checkbox if selected
            if category in self.selected_categories:
                inner_rect = pygame.Rect(checkbox_x + 5, current_y + 5, 14, 14)  # Adjusted for larger checkbox
                pygame.draw.rect(screen, LIGHT_BLUE, inner_rect)
            
            # Draw category name with larger font
            # Special handling for Computer Science to prevent it from being cut off
            if category == "Computer Science":
                # Use a slightly smaller font for this category
                cat_text = font_small.render(category, True, WHITE)
            else:
                cat_text = font_instructions.render(category, True, WHITE)
            screen.blit(cat_text, (checkbox_x + 35, current_y))
            
            # Store checkbox position for click detection
            self.category_checkboxes[i] = checkbox_rect
        
        # Right side - Player stats (only if name is entered and stats exist)
        if self.name_input.text:
            stats = self.get_player_stats(self.name_input.text)
            
            # Draw a box for player stats - moved to left side to avoid overlapping with start button
            stats_box = pygame.Rect(left_column_x, 450, 300, 130)  # Adjusted y position to account for larger instructions
            pygame.draw.rect(screen, LIGHT_GRAY, stats_box, border_radius=10)
            pygame.draw.rect(screen, LIGHT_BLUE, stats_box, 2, border_radius=10)
            
            # Stats title
            stats_title = font_medium.render("Player Stats:", True, CYAN)
            screen.blit(stats_title, (stats_box.centerx - stats_title.get_width()//2, stats_box.y + 10))
            
            # Stats content
            stats_text = [
                f"Games Played: {stats['games_played']}",
                f"Average Score: {stats['average_score']}",
                f"Best Score: {stats['best_score']}"
            ]
            
            for i, line in enumerate(stats_text):
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (stats_box.x + 20, stats_box.y + 45 + i*25))
        
        # Start button - centered at bottom
        self.start_button.rect.x = SCREEN_WIDTH//2 - 100
        self.start_button.rect.y = 600  # Moved down from 550 to provide more space
        self.start_button.draw(screen)
    
    def draw_question(self):
        screen.fill(DARK_GRAY)
        
        # Question number and score
        question_num = font_medium.render(f"Question {self.current_question + 1}/{len(self.questions)}", True, WHITE)
        screen.blit(question_num, (100, 30))
        
        score_text = font_medium.render(f"Score: {self.score}", True, CYAN)
        screen.blit(score_text, (SCREEN_WIDTH - 200, 30))
        
        # Make sure we don't try to access a question beyond the list
        if self.current_question >= len(self.questions):
            self.save_player_record()
            self.state = "results"
            return
            
        # Category and difficulty
        question = self.questions[self.current_question]
        category_text = font_small.render(f"Category: {question['category']}", True, PURPLE)
        screen.blit(category_text, (100, 70))
        
        difficulty_color = GREEN if question['difficulty'] == 'easy' else ORANGE if question['difficulty'] == 'medium' else RED
        difficulty_text = font_small.render(f"Difficulty: {question['difficulty'].capitalize()}", True, difficulty_color)
        screen.blit(difficulty_text, (SCREEN_WIDTH - 250, 70))
        
        # Question text
        self.draw_wrapped_text(question['question'], font_medium, LIGHT_BLUE, 100, 120, SCREEN_WIDTH - 200)
        
        # Options
        option_y = 200
        for i, option in enumerate(question['options']):
            button = self.option_buttons[i]
            
            # Change color if question is answered
            if self.question_answered:
                if option == question['correct']:
                    button.color = GREEN
                    button.hover_color = GREEN
                elif i == self.selected_option and option != question['correct']:
                    button.color = RED
                    button.hover_color = RED
            
            button.draw(screen)
            option_y += 70
        
        # Display feedback message if timer is active
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            feedback_text = font_medium.render(self.feedback_message, True, self.feedback_color)
            # Center the feedback message at the bottom of the screen
            feedback_x = SCREEN_WIDTH // 2 - feedback_text.get_width() // 2
            feedback_y = 470  # Position above the next button
            screen.blit(feedback_text, (feedback_x, feedback_y))
        
        # Next button (only show if question is answered)
        if self.question_answered:
            self.next_button.draw(screen)
    
    def draw_results(self):
        screen.fill(DARK_GRAY)
        
        # Title
        title = font_large.render("Quiz Results", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Player name and score
        name_text = font_medium.render(f"Player: {self.player_name}", True, WHITE)
        screen.blit(name_text, (SCREEN_WIDTH//2 - name_text.get_width()//2, 120))
        
        score_text = font_large.render(f"Score: {self.score}/{len(self.questions)}", True, LIGHT_BLUE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 170))
        
        # Categories played
        categories_text = "Categories: " + (", ".join(self.selected_categories) if self.selected_categories else "All")
        categories_rendered = font_small.render(categories_text, True, PURPLE)
        screen.blit(categories_rendered, (SCREEN_WIDTH//2 - categories_rendered.get_width()//2, 220))
        
        # Performance message
        if self.score >= 8:
            message = "Excellent! You're a Knowledge Master!"
            color = GREEN
        elif self.score >= 6:
            message = "Good! You have solid understanding!"
            color = ORANGE
        else:
            message = "Keep Learning & Try Again! You'll improve!"
            color = RED
            
        performance = font_medium.render(message, True, color)
        screen.blit(performance, (SCREEN_WIDTH//2 - performance.get_width()//2, 270))
        
        # Player stats
        stats = self.get_player_stats(self.player_name)
        
        stats_title = font_medium.render("Your Statistics:", True, CYAN)
        screen.blit(stats_title, (SCREEN_WIDTH//2 - stats_title.get_width()//2, 350))
        
        stats_text = [
            f"Games Played: {stats['games_played']}",
            f"Average Score: {stats['average_score']}",
            f"Best Score: {stats['best_score']}"
        ]
        
        for i, line in enumerate(stats_text):
            text = font_medium.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 400 + i*40))
        
        # Play again button
        self.play_again_button.draw(screen)
        
        # Quit button
        self.quit_button.draw(screen)
    
    def draw_wrapped_text(self, text, font, color, x, y, max_width):
        # Special handling for subscripts and mathematical notation
        # Replace common mathematical notations with better representations
        text = text.replace("₁₀", "10")  # Fix log base 10
        text = text.replace("C₆H₁₂O₆", "C6H12O6")  # Fix glucose formula
        text = text.replace("H₂O", "H2O")  # Fix water formula
        text = text.replace("CO₂", "CO2")  # Fix carbon dioxide formula
        text = text.replace("O₂", "O2")  # Fix oxygen formula
        
        # Handle other subscripts
        for i in range(10):
            text = text.replace(f"₍{i}₎", f"({i})")  # Subscript in parentheses
            text = text.replace(f"₊{i}", f"+{i}")  # Subscript with plus
            text = text.replace(f"₋{i}", f"-{i}")  # Subscript with minus
            text = text.replace(f"₌{i}", f"={i}")  # Subscript with equals
            text = text.replace(f"ₓ{i}", f"x{i}")  # Subscript with x
            text = text.replace(f"ₙ{i}", f"n{i}")  # Subscript with n
            text = text.replace(f"_{i}", f"{i}")  # Subscript with underscore
        
        # Now proceed with normal text wrapping
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
            
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (x, y + i * (font.get_linesize() + 5)))
    
    def run(self):
        # Create UI elements
        self.name_input = TextInput(SCREEN_WIDTH//2 - 150, 220, 300, 40, "type your name here...")
        self.start_button = Button(SCREEN_WIDTH//2 - 100, 600, 200, 50, "Start Quiz", DARK_BLUE, (50, 120, 220))
        
        # Changed option button colors for better contrast
        self.option_buttons = [
            Button(100, 200, SCREEN_WIDTH - 200, 50, "", DARK_BLUE, (50, 120, 220)),
            Button(100, 270, SCREEN_WIDTH - 200, 50, "", DARK_BLUE, (50, 120, 220)),
            Button(100, 340, SCREEN_WIDTH - 200, 50, "", DARK_BLUE, (50, 120, 220)),
            Button(100, 410, SCREEN_WIDTH - 200, 50, "", DARK_BLUE, (50, 120, 220))
        ]
        
        self.next_button = Button(SCREEN_WIDTH//2 - 100, 530, 200, 50, "Next Question", DARK_BLUE, (50, 120, 220))
        
        self.play_again_button = Button(SCREEN_WIDTH//2 - 220, 600, 200, 50, "Play Again", DARK_BLUE, (50, 120, 220))
        self.quit_button = Button(SCREEN_WIDTH//2 + 20, 600, 200, 50, "Quit", DARK_BLUE, (50, 120, 220))
        
        # Dictionary to store category checkbox positions
        self.category_checkboxes = {}
        
        clock = pygame.time.Clock()
        
        # Main game loop
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_click = True
                    
                    # Check if a category checkbox was clicked
                    if self.state == "menu":
                        for i, checkbox_rect in self.category_checkboxes.items():
                            if checkbox_rect.collidepoint(event.pos):
                                category = self.categories[i]
                                if category in self.selected_categories:
                                    self.selected_categories.remove(category)
                                else:
                                    self.selected_categories.append(category)
                
                if self.state == "menu":
                    self.name_input.handle_event(event)
            
            # State machine
            if self.state == "menu":
                self.start_button.check_hover(mouse_pos)
                
                if self.start_button.is_clicked(mouse_pos, mouse_click) and self.name_input.text:
                    self.player_name = self.name_input.text
                    self.select_questions()
                    self.current_question = 0
                    self.score = 0
                    self.state = "question"
                    self.question_answered = False
                    self.selected_option = None
                
                self.draw_menu()
                
            elif self.state == "question":
                # Update option button texts
                question = self.questions[self.current_question]
                for i, option in enumerate(question['options']):
                    self.option_buttons[i].text = option
                    self.option_buttons[i].check_hover(mouse_pos)
                    
                    # Handle option selection
                    if self.option_buttons[i].is_clicked(mouse_pos, mouse_click) and not self.question_answered:
                        self.selected_option = i
                        self.question_answered = True
                        
                        # Update score if correct and show feedback message
                        question = self.questions[self.current_question]
                        if question['options'][i] == question['correct']:
                            self.score += 1
                            # Show a random encouraging message
                            self.feedback_message = random.choice(self.correct_messages)
                            self.feedback_color = GREEN
                        else:
                            # Show a random motivating message
                            self.feedback_message = random.choice(self.incorrect_messages)
                            self.feedback_color = ORANGE
                        
                        # Set the feedback timer (will show for about 3 seconds at 60 FPS)
                        self.feedback_timer = 180
                
                # Handle next button
                self.next_button.check_hover(mouse_pos)
                if self.next_button.is_clicked(mouse_pos, mouse_click) and self.question_answered:
                    self.current_question += 1
                    
                    # Reset for next question or go to results
                    if self.current_question < len(self.questions):
                        self.question_answered = False
                        self.selected_option = None
                        self.feedback_timer = 0  # Reset feedback timer
                        
                        # Reset button colors - ensure they're all DARK_BLUE
                        for button in self.option_buttons:
                            button.color = DARK_BLUE
                            button.hover_color = (50, 120, 220)
                    else:
                        self.save_player_record()
                        self.state = "results"
                        continue  # Skip drawing the question and go directly to results
                
                self.draw_question()
                
            elif self.state == "results":
                self.play_again_button.check_hover(mouse_pos)
                self.quit_button.check_hover(mouse_pos)
                
                if self.play_again_button.is_clicked(mouse_pos, mouse_click):
                    self.state = "menu"
                
                if self.quit_button.is_clicked(mouse_pos, mouse_click):
                    running = False
                
                self.draw_results()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = QuizGame()
    game.run()
