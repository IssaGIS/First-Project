import tkinter as tk
import random

# Window and canvas configuration
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

# Snake configuration
SEGMENT_SIZE = 10    # Width of each snake segment
INITIAL_SPEED = 100  # Starting speed (ms between moves)
SPEED_INCREASE_FACTOR = 0.97  # Each orb eaten => speed * 0.97 (~3% faster)

# Directions
UP = "Up"
DOWN = "Down"
LEFT = "Left"
RIGHT = "Right"

class SnakeGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Issa's Snake Game")

        # Make the window open large
        self.root.geometry("900x900")

        # --- START MENU --- #
        self.menu_frame = tk.Frame(self.root, bg="#261447")  # dark purple
        self.menu_frame.pack(fill="both", expand=True)

        # Title in WHITE now (no color cycling for the menu title)
        self.menu_title_label = tk.Label(
            self.menu_frame,
            text="SNAKE GAME",
            fg="white",           # Title is white
            bg="#261447",
            font=("Helvetica", 48, "bold")
        )
        self.menu_title_label.pack(pady=40)

        # Bullet-point style instructions
        instructions_text = (
            "INSTRUCTIONS:\n"
            "• Use Arrow Keys or W, A, S, D to move.\n"
            "• Press SPACEBAR to Pause/Unpause.\n"
            "• Eat the red orbs to grow (and speed up!).\n"
            "• The snake changes color each time it eats!\n"
            "• Don't crash into walls or yourself.\n"
        )
        self.instructions_label = tk.Label(
            self.menu_frame,
            text=instructions_text,
            fg="white",
            bg="#261447",
            font=("Helvetica", 16),
            justify="left"
        )
        self.instructions_label.pack(pady=10)

        # Start button
        self.start_button = tk.Button(
            self.menu_frame,
            text="ENTER THE WORLD OF SNAKE",
            command=self.start_game,
            fg="black",
            bg="#07b531",     # Bright green
            activeforeground="black",
            activebackground="#4fff6e",
            font=("Helvetica", 16, "bold"),
            relief="raised",
            borderwidth=4
        )
        self.start_button.pack(pady=30)

        # Game variables
        self.canvas = None
        self.snake_segments = []
        self.segment_objects = []
        self.direction = RIGHT
        self.score = 0
        self.game_over = False
        self.is_paused = False
        self.game_speed = INITIAL_SPEED

        self.food_position = None
        self.food = None
        self.score_text = None

        # List of colors the snake can change to whenever it eats
        self.snake_colors = ["green", "blue", "yellow", "pink", "orange", "purple"]
        self.snake_color_index = 0
        self.current_snake_color = self.snake_colors[self.snake_color_index]

    def start_game(self):
        """Destroys the start menu and sets up the main Snake game interface."""
        # Destroy any old frames (like the menu)
        if self.menu_frame:
            self.menu_frame.destroy()

        # If there's an existing canvas (from a previous game), remove it
        if self.canvas:
            self.canvas.destroy()

        # Create the canvas
        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            background="black"
        )
        self.canvas.pack()

        # Reset key variables
        self.direction = RIGHT
        self.score = 0
        self.game_over = False
        self.is_paused = False
        self.game_speed = INITIAL_SPEED

        # Reset snake color to the first color
        self.snake_color_index = 0
        self.current_snake_color = self.snake_colors[self.snake_color_index]

        # Initialize snake length 9 (triple the original 3)
        midpoint_x = WINDOW_WIDTH // 2
        midpoint_y = WINDOW_HEIGHT // 2
        self.snake_segments = []
        start_x = midpoint_x - SEGMENT_SIZE * 8  # Enough space for 9 segments

        for i in range(9):
            x = start_x + i * SEGMENT_SIZE
            y = midpoint_y
            self.snake_segments.append((x, y))

        # Draw the initial snake
        self.segment_objects = []
        for (x, y) in self.snake_segments:
            seg = self.canvas.create_rectangle(
                x, y,
                x + SEGMENT_SIZE,
                y + SEGMENT_SIZE,
                fill=self.current_snake_color,
                outline="darkgreen"
            )
            self.segment_objects.append(seg)

        # Place initial food
        self.food_position = self.place_food()
        self.food = self.canvas.create_oval(
            self.food_position[0],
            self.food_position[1],
            self.food_position[0] + SEGMENT_SIZE,
            self.food_position[1] + SEGMENT_SIZE,
            fill="red",
            outline="red"
        )

        # Create score display
        self.score_text = self.canvas.create_text(
            60, 15,
            fill="white",
            font=("Helvetica", 16, "bold"),
            text=f"Score: {self.score}"
        )

        # Bind keyboard events (arrows + W, A, S, D + space)
        self.root.bind("<KeyPress>", self.on_key_press)

        # Start the main loop
        self.game_loop()

    def place_food(self):
        """
        Place the food in a random position on the grid (aligned to SEGMENT_SIZE)
        and ensure it's NOT on top of the snake.
        """
        snake_set = set(self.snake_segments)  # For quick membership checks

        while True:
            max_x = (WINDOW_WIDTH // SEGMENT_SIZE) - 1
            max_y = (WINDOW_HEIGHT // SEGMENT_SIZE) - 1
            food_x = random.randint(0, max_x) * SEGMENT_SIZE
            food_y = random.randint(0, max_y) * SEGMENT_SIZE

            if (food_x, food_y) not in snake_set:
                return (food_x, food_y)

    def on_key_press(self, event):
        """Handle movement keys plus spacebar to toggle pause."""
        if event.keysym == "space":
            self.is_paused = not self.is_paused
            return

        # Map W, A, S, D to Up, Left, Down, Right
        key_map = {
            "w": UP, "W": UP,
            "a": LEFT, "A": LEFT,
            "s": DOWN, "S": DOWN,
            "d": RIGHT, "D": RIGHT
        }

        new_direction = key_map.get(event.keysym, event.keysym)

        # Disallow 180-degree reversals
        opposites = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        if new_direction in opposites and opposites[new_direction] != self.direction:
            self.direction = new_direction

    def move_snake(self):
        """Move the snake one step in the current direction."""
        head_x, head_y = self.snake_segments[-1]

        if self.direction == UP:
            new_head = (head_x, head_y - SEGMENT_SIZE)
        elif self.direction == DOWN:
            new_head = (head_x, head_y + SEGMENT_SIZE)
        elif self.direction == LEFT:
            new_head = (head_x - SEGMENT_SIZE, head_y)
        elif self.direction == RIGHT:
            new_head = (head_x + SEGMENT_SIZE, head_y)
        else:
            new_head = (head_x, head_y)  # No movement

        # Add the new head
        # Use self.current_snake_color for the new segment
        new_seg = self.canvas.create_rectangle(
            new_head[0], new_head[1],
            new_head[0] + SEGMENT_SIZE,
            new_head[1] + SEGMENT_SIZE,
            fill=self.current_snake_color,
            outline="darkgreen"
        )
        self.segment_objects.append(new_seg)
        self.snake_segments.append(new_head)

        # Check if snake ate the food
        if new_head == self.food_position:
            self.score += 1
            self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")
            self.canvas.delete(self.food)

            # Speed up by ~3%
            self.game_speed = int(self.game_speed * SPEED_INCREASE_FACTOR)

            # Change snake color to next color
            self.snake_color_index = (self.snake_color_index + 1) % len(self.snake_colors)
            self.current_snake_color = self.snake_colors[self.snake_color_index]

            # Place new food (ensure it's not under the snake)
            self.food_position = self.place_food()
            self.food = self.canvas.create_oval(
                self.food_position[0], self.food_position[1],
                self.food_position[0] + SEGMENT_SIZE,
                self.food_position[1] + SEGMENT_SIZE,
                fill="red",
                outline="red"
            )
        else:
            # Remove the tail segment
            tail_obj = self.segment_objects.pop(0)
            self.canvas.delete(tail_obj)
            self.snake_segments.pop(0)

    def check_collisions(self):
        """Check if the snake has collided with walls or itself."""
        head_x, head_y = self.snake_segments[-1]

        # Collisions with walls
        if head_x < 0 or head_x >= WINDOW_WIDTH or head_y < 0 or head_y >= WINDOW_HEIGHT:
            self.end_game("You hit the wall!")
            return

        # Collisions with self
        if (head_x, head_y) in self.snake_segments[:-1]:
            self.end_game("You ran into yourself!")
            return

    def end_game(self, message):
        """Stop the game and display 'Game Over' message with orb count.
           Also show 'Play Again' and 'Back to Menu' buttons.
        """
        self.game_over = True

        # Display the Game Over text
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2,
            fill="white",
            font=("Helvetica", 24, "bold"),
            text=f"Game Over!\n{message}\nYou ate {self.score} orbs!"
        )

        # Create "Play Again" button on the canvas
        play_again_btn = tk.Button(
            self.canvas,
            text="Play Again",
            font=("Helvetica", 14, "bold"),
            bg="#ffbe0b",
            fg="black",
            command=self.play_again
        )
        self.canvas.create_window(
            WINDOW_WIDTH // 2,
            (WINDOW_HEIGHT // 2) + 60,
            window=play_again_btn
        )

        # Create "Back to Menu" button on the canvas
        menu_btn = tk.Button(
            self.canvas,
            text="Back to Menu",
            font=("Helvetica", 14, "bold"),
            bg="#ffbe0b",
            fg="black",
            command=self.back_to_menu
        )
        self.canvas.create_window(
            WINDOW_WIDTH // 2,
            (WINDOW_HEIGHT // 2) + 120,
            window=menu_btn
        )

    def play_again(self):
        """
        Removes the old canvas and starts a new game in the same window.
        """
        if self.canvas:
            self.canvas.destroy()
        self.start_game()

    def back_to_menu(self):
        """
        Removes the old canvas and recreates the original menu screen.
        """
        # Destroy the game canvas
        if self.canvas:
            self.canvas.destroy()

        # Rebuild the menu frame from scratch
        self.menu_frame = tk.Frame(self.root, bg="#261447")
        self.menu_frame.pack(fill="both", expand=True)

        # Title in white
        self.menu_title_label = tk.Label(
            self.menu_frame,
            text="SNAKE GAME",
            fg="white",
            bg="#261447",
            font=("Helvetica", 48, "bold")
        )
        self.menu_title_label.pack(pady=40)

        instructions_text = (
            "INSTRUCTIONS:\n"
            "• Use Arrow Keys or W, A, S, D to move.\n"
            "• Press SPACEBAR to Pause/Unpause.\n"
            "• Eat the red orbs to grow (and speed up!).\n"
            "• The snake changes color each time it eats!\n"
            "• Don't crash into walls or yourself.\n"
        )
        self.instructions_label = tk.Label(
            self.menu_frame,
            text=instructions_text,
            fg="white",
            bg="#261447",
            font=("Helvetica", 16),
            justify="left"
        )
        self.instructions_label.pack(pady=10)

        # Start button
        self.start_button = tk.Button(
            self.menu_frame,
            text="ENTER THE WORLD OF SNAKE",
            command=self.start_game,
            fg="black",
            bg="#07b531",
            activeforeground="black",
            activebackground="#4fff6e",
            font=("Helvetica", 16, "bold"),
            relief="raised",
            borderwidth=4
        )
        self.start_button.pack(pady=30)

    def game_loop(self):
        """Main loop for movement and collision checks."""
        if not self.game_over:
            if not self.is_paused:
                self.move_snake()
                self.check_collisions()
            self.root.after(self.game_speed, self.game_loop)

def main():
    root = tk.Tk()
    app = SnakeGameApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
