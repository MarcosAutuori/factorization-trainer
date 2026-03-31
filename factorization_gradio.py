import gradio as gr
import random

# Core game logic
class FactorizationGame:
    def __init__(self):
        self.score = 0
        self.current_number = self.generate_number()

    def generate_number(self):
        return random.randint(10, 100)

    def check_answer(self, factors):
        if self.current_number % factors == 0:
            self.score += 1
            self.current_number = self.generate_number()
            return True, self.current_number, self.score
        else:
            return False, self.current_number, self.score

# Initialize the game
game = FactorizationGame()

# Gradio web interface

def interactive_game(factors):
    is_correct, number, score = game.check_answer(factors)
    if is_correct:
        return f"Correct! Next number: {number}", score
    else:
        return f"Incorrect! Try again: {number}", score

iface = gr.Interface(
    fn=interactive_game,
    inputs=gr.inputs.Slider(minimum=1, maximum=10, default=1),
    outputs="text",
    title="Factorization Game",
    description="Select a factor of the number displayed to score points!"
)

iface.launch()