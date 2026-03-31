import gradio as gr
import time
import numpy as np
import simpleaudio as sa

class FactorizationGame:
    def __init__(self):
        self.score = 0
        self.start_time = None
        self.grid_size = (4, 8)
        self.numbers = list(range(2, 11))
        self.target_number = None
        self.user_input = None
        self.sound_buffer = None

    def generate_sound(self, number):
        frequency = 440 + (number - 2) * 20  # Simple sound frequency mapping
        t = np.linspace(0, 0.5, int(44100 * 0.5), False)
        tone = np.sin(frequency * t * 2 * np.pi)
        tone *= 32767 / np.max(np.abs(tone))  # Scale to int16
        self.sound_buffer = tone.astype(np.int16)

    def generate_target(self):
        self.target_number = np.random.choice(self.numbers)
        self.generate_sound(self.target_number)  # Generate sound for the target

    def check_answer(self):
        if self.user_input is not None and self.target_number:
            if self.user_input in self.factorize(self.target_number):
                feedback = "Correct!"
                self.score += 1
            else:
                feedback = "Incorrect."
            self.user_input = None
            self.generate_target()  # Update target number
            return feedback, self.score

    def factorize(self, num):
        factors = []
        for i in range(2, num + 1):
            if num % i == 0:
                factors.append(i)
        return factors[:3]  # Return first three factors for simplicity

    def start_game(self):
        self.start_time = time.time()
        self.score = 0
        self.generate_target()  # Start with a target number

    def get_time_remaining(self):
        elapsed_time = time.time() - self.start_time
        return max(0, 150 - elapsed_time)  # Returns time remaining in seconds

    def get_game_state(self):
        return self.target_number, self.get_time_remaining(), self.score

    def play_sound(self):
        if self.sound_buffer is not None:
            wave_obj = sa.WaveObject(self.sound_buffer, 1, 2, 44100)
            wave_obj.play()


def main():
    game = FactorizationGame()

    def reset_game():
        game.start_game()
        return game.get_game_state()

    def answer(number):
        game.user_input = number
        feedback, score = game.check_answer()
        game.play_sound()  # Play sound feedback
        return feedback, game.get_game_state()

    with gr.Blocks() as demo:
        gr.Markdown("# Factorization Game")
        with gr.Row():
            target_display = gr.Textbox(label="Target Number", interactive=False)
            time_display = gr.Textbox(label="Time Remaining", interactive=False)
            score_display = gr.Textbox(label="Score", interactive=False)
        with gr.Row():
            number_buttons = [gr.Button(str(num), elem_id=str(num)) for num in game.numbers]
            for button in number_buttons:
                button.click(fn=answer, inputs=button, outputs=["feedback", (target_display, time_display, score_display)])
        reset_btn = gr.Button("Reset Game")
        reset_btn.click(reset_game, outputs=[target_display, time_display, score_display])
        
        # Initial state
        reset_game()

    demo.launch()

if __name__ == '__main__':
    main()