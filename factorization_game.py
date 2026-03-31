"""
================================================================================
                    INTERACTIVE FACTORIZATION v1.4 EN
================================================================================

Description:
    Interactive educational game to practice number factorization.
    Players select two factors from a numerical keyboard to multiply and
    match numbers displayed in the grid.

Features:
    • 4x8 grid with numbers to factorize
    • Numerical keyboard (2-10) for factor selection
    • Scoring system based on time (max 150 seconds)
    • Automatic sound file generation in .wav format
    • Visual and audio feedback for correct/incorrect answers
    • Reset button for new game

================================================================================
                              AUTHORSHIP AND CREDITS
================================================================================

Main Developer:
    Marcos Autúori (MarcosAutuori)
    
Development Assistance:
    GitHub Copilot (@copilot)
    - Code analysis and correction
    - Sound system optimization
    - GUI improvements
    - Debug and troubleshooting
    - Automatic .wav file generation

Technologies Used:
    • Python 3.12.3
    • Pygame 2.5.2 (SDL 2.30.0)
    • Standard Library: wave, struct, math, os, sys

Creation Date:
    2026-03-31

Version:
    1.4 EN (English version with automatic sound generation)

================================================================================
                           LICENSE AND DISTRIBUTION
================================================================================

This project is provided as-is for educational purposes.
Modifications and distributions are permitted with authorship attribution.

================================================================================
"""

import pygame
import sys
import os
import wave
import struct
import math

pygame.init()

ROWS, COLS = 4, 8
CELL_SIZE = 80
MARGIN = 5

WIDTH = COLS * (CELL_SIZE + MARGIN) + MARGIN 
HEIGHT = ROWS * (CELL_SIZE + MARGIN) + MARGIN + 440

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (200, 220, 255)
GREEN = (120, 220, 120)
GRAY = (220, 220, 220)
RED = (255, 100, 100)
DARK_GREEN = (80, 180, 80)
YELLOW = (255, 255, 0)

FONT = pygame.font.SysFont("arial", 24)
FONT_SMALL = pygame.font.SysFont("arial", 20)
FONT_TITLE = pygame.font.SysFont("arial", 26, bold=True)
FONT_BUTTON = pygame.font.SysFont("arial", 22, bold=True)

# ✅ NUMBER GRID
grid = [
    [10, 12, 14, 15, 16, 18, 20, 21],
    [24, 25, 27, 28, 30, 32, 35, 36],
    [40, 42, 45, 48, 50, 54, 56, 60],
    [63, 64, 70, 72, 80, 81, 90, 100]
]

solved = [[False]*COLS for _ in range(ROWS)]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Factorization Game - GET IT RIGHT FAST!")

selected_value = None
selected_pos = None
selected_factors = []
feedback = ""
feedback_timer = 0
feedback_color = BLACK
game_finished = False
final_score = 0
max_time = 150
clock = pygame.time.Clock()

# ⏱️ Timer set at game start
start_time = pygame.time.get_ticks()

# Numerical keyboard
keys = [
    [2, 3, 4],
    [5, 6, 7],
    [8, 9, 10]
]

key_rects = []
restart_button_rect = None

# ========== SOUND FOLDER MANAGEMENT ==========
SOUNDS_FOLDER = "pygame_sounds"

def ensure_sounds_folder():
    """Creates the pygame_sounds folder if it doesn't exist"""
    if not os.path.exists(SOUNDS_FOLDER):
        os.makedirs(SOUNDS_FOLDER)
        print(f"📁 Folder '{SOUNDS_FOLDER}' created\n")

def generate_sine_wave(frequency, duration_ms, sample_rate=44100):
    """
    Generates a pure sine wave for sound synthesis.
    
    Args:
        frequency (int): Frequency in Hz
        duration_ms (int): Duration in milliseconds
        sample_rate (int): Sample rate (default 44100 Hz)
    
    Returns:
        bytes: Raw audio data
    """
    num_samples = int(sample_rate * duration_ms / 1000)
    frames = []
    
    for i in range(num_samples):
        sample = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        frames.append(struct.pack('h', sample))
    
    return b''.join(frames)

def save_wav(filename, frequency, duration_ms, sample_rate=44100):
    """
    Saves a .wav file with the specified frequency and duration.
    
    Args:
        filename (str): Filename (without path)
        frequency (int): Frequency in Hz
        duration_ms (int): Duration in milliseconds
        sample_rate (int): Sample rate
    
    Returns:
        bool: True if saved successfully, False otherwise
    """
    filepath = os.path.join(SOUNDS_FOLDER, filename)
    
    try:
        audio_data = generate_sine_wave(frequency, duration_ms, sample_rate)
        
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16 bits
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
        
        return True
    except Exception as e:
        print(f"✗ Error creating {filename}: {e}")
        return False

def check_and_generate_sounds():
    """
    Checks if sound files exist.
    If they don't exist, generates them automatically.
    """
    ensure_sounds_folder()
    
    sound_files = {
        'click.wav': (800, 50),           # Click sound - 800Hz, 50ms
        'correct.wav': (1000, 200),       # Correct answer - 1000Hz, 200ms
        'incorrect.wav': (400, 200),      # Wrong answer - 400Hz, 200ms
        'complete.wav': (1200, 300),      # Game complete - 1200Hz, 300ms
        'button.wav': (900, 100)          # Button click - 900Hz, 100ms
    }
    
    print("🔊 Checking sounds...\n")
    
    missing_sounds = []
    for filename, (freq, duration) in sound_files.items():
        filepath = os.path.join(SOUNDS_FOLDER, filename)
        if os.path.exists(filepath):
            print(f"✓ {filename} already exists")
        else:
            print(f"🎵 Generating {filename}...")
            if save_wav(filename, freq, duration):
                print(f"✓ {filename} created ({freq}Hz, {duration}ms)")
            else:
                missing_sounds.append(filename)
    
    if missing_sounds:
        print(f"\n⚠️ Unable to generate: {', '.join(missing_sounds)}")
    else:
        print(f"\n✅ All sounds are ready!\n")

# ========== SOUND LOADING ==========
sounds = {}

def load_sounds():
    """Loads sound files from the pygame_sounds folder"""
    global sounds
    
    sound_files = {
        'click': 'click.wav',
        'correct': 'correct.wav',
        'incorrect': 'incorrect.wav',
        'complete': 'complete.wav',
        'button': 'button.wav'
    }
    
    try:
        pygame.mixer.init()
        
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(SOUNDS_FOLDER, filename)
            if os.path.exists(filepath):
                try:
                    sounds[sound_name] = pygame.mixer.Sound(filepath)
                except Exception as e:
                    print(f"✗ Error loading {filename}: {e}")
                    sounds[sound_name] = None
            else:
                sounds[sound_name] = None
        
        if any(sounds.values()):
            print("✅ Sounds loaded successfully!\n")
        else:
            print("⚠️ No sounds loaded.\n")

    except Exception as e:
        print(f"⚠️ Mixer not available: {e}\n")
        sounds = {key: None for key in sound_files}

# ========== SOUND INITIALIZATION ==========
print("="*70)
print("🎮 INTERACTIVE FACTORIZATION - GET IT RIGHT FAST! - Version 1.4")
print("="*70 + "\n")

check_and_generate_sounds()
load_sounds()

def play_sound(sound_name):
    """
    Plays a sound by name.
    
    Args:
        sound_name (str): Sound name ('click', 'correct', etc)
    """
    try:
        if sound_name in sounds and sounds[sound_name] is not None:
            sounds[sound_name].play()
    except:
        pass

def restart_game():
    """Restarts the game, clearing state and resetting the timer"""
    global selected_value, selected_pos, selected_factors, feedback, feedback_timer
    global game_finished, final_score, start_time, solved, elapsed_time, score, feedback_color
    
    play_sound('button')
    
    solved = [[False]*COLS for _ in range(ROWS)]
    selected_value = None
    selected_pos = None
    selected_factors = []
    feedback = ""
    feedback_timer = 0
    feedback_color = BLACK
    game_finished = False
    final_score = 0
    start_time = pygame.time.get_ticks()
    elapsed_time = 0
    score = max_time

def draw():
    """Draws all game interface elements"""
    global elapsed_time, score, restart_button_rect, feedback_color
    
    screen.fill(WHITE)

    if not game_finished:
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        score = max(0, max_time - elapsed_time)
    else:
        score = final_score

    # Number grid
    for r in range(ROWS):
        for c in range(COLS):
            x = MARGIN + c * (CELL_SIZE + MARGIN)
            y = MARGIN + r * (CELL_SIZE + MARGIN)

            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            color = GREEN if solved[r][c] else BLUE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

            text = FONT.render(str(grid[r][c]), True, BLACK)
            screen.blit(text, text.get_rect(center=rect.center))

    # Numerical keyboard
    key_rects.clear()
    start_y = ROWS * (CELL_SIZE + MARGIN) + 20
    start_x = 50

    for i, row in enumerate(keys):
        for j, val in enumerate(row):
            x = start_x + j * 100
            y = start_y + i * 60

            rect = pygame.Rect(x, y, 80, 50)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

            text = FONT.render(str(val), True, BLACK)
            screen.blit(text, text.get_rect(center=rect.center))

            key_rects.append((rect, val))

    # ========== STATUS SIDE PANEL ==========
    panel_x = start_x + 320
    panel_y = start_y
    panel_width = 260
    panel_height = 200

    pygame.draw.rect(screen, (245, 245, 245), (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    panel_center_x = panel_x + panel_width // 2
    y_start = panel_y + 15
    line_spacing = 35

    title_text = FONT_TITLE.render("Game Status", True, BLACK)
    title_rect = title_text.get_rect(center=(panel_center_x, y_start))
    screen.blit(title_text, title_rect)

    pygame.draw.line(screen, BLACK, (panel_x + 10, y_start + 20), (panel_x + panel_width - 10, y_start + 20), 1)

    y_offset = y_start + 35

    # Selected number
    if selected_value:
        num_text = FONT.render(f"Factors of:   {selected_value}", True, (0, 0, 150))
        num_rect = num_text.get_rect(center=(panel_center_x, y_offset))
        screen.blit(num_text, num_rect)
    else:
        num_text = FONT_SMALL.render("Select a number", True, (100, 100, 100))
        num_rect = num_text.get_rect(center=(panel_center_x, y_offset))
        screen.blit(num_text, num_rect)

    y_offset += line_spacing

    # Selected factors
    factors_label = FONT_SMALL.render("Factors:", True, BLACK)
    factors_label_rect = factors_label.get_rect(center=(panel_center_x, y_offset))
    screen.blit(factors_label, factors_label_rect)

    y_offset += 25

    factors_text = FONT.render(str(selected_factors) if selected_factors else "[ ]", True, (0, 100, 0))
    factors_rect = factors_text.get_rect(center=(panel_center_x, y_offset))
    screen.blit(factors_text, factors_rect)

    y_offset += line_spacing

    # Feedback with blinking animation
    if feedback and feedback_timer > 0:
        if (feedback_timer // 10) % 2 == 0:
            feedback_text = FONT.render(feedback, True, feedback_color)
            feedback_rect = feedback_text.get_rect(center=(panel_center_x, y_offset))
            screen.blit(feedback_text, feedback_rect)

    y_offset += line_spacing

    # Elapsed time
    time_text = FONT_SMALL.render(f"{elapsed_time}s / {max_time}s", True, BLACK)
    time_rect = time_text.get_rect(center=(panel_center_x, y_offset))
    screen.blit(time_text, time_rect)

    y_offset += 28

    # Score
    score_text = FONT.render(f"Points: {score}", True, (150, 0, 150))
    score_rect = score_text.get_rect(center=(panel_center_x, y_offset + 100))
    screen.blit(score_text, score_rect)

    y_offset += line_spacing

    # ========== RESTART BUTTON ==========
    button_width = 180
    button_height = 50
    button_x = 160 + (WIDTH - button_width) // 2
    button_y = HEIGHT - 220

    restart_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    button_color = DARK_GREEN if game_finished else GRAY
    pygame.draw.rect(screen, button_color, restart_button_rect)
    pygame.draw.rect(screen, BLACK, restart_button_rect, 3)

    button_text = FONT_BUTTON.render("Restart", True, BLACK)
    button_text_rect = button_text.get_rect(center=restart_button_rect.center)
    screen.blit(button_text, button_text_rect)

    # Keyboard hints
    hint_text = FONT_SMALL.render("ESC: Clear | Backspace: Undo | R: Restart", True, (100, 100, 100))
    screen.blit(hint_text, (50, HEIGHT - 30))

    pygame.display.flip()

def check_answer():
    """Checks if the player's answer is correct"""
    global feedback, selected_factors, selected_value, selected_pos, game_finished, final_score, feedback_timer, feedback_color

    if len(selected_factors) != 2:
        return

    a, b = selected_factors

    if a * b == selected_value:
        feedback = "✔️ Correct!"
        feedback_timer = 60
        feedback_color = (0, 150, 0)
        play_sound('correct')
        
        r, c = selected_pos
        solved[r][c] = True

        # Check game completion
        if all(all(row) for row in solved):
            game_finished = True
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            final_score = max(0, max_time - elapsed_time)
            play_sound('complete')

        selected_value = None
        selected_pos = None
        selected_factors = []

    else:
        feedback = "❌ Wrong"
        feedback_timer = 60
        feedback_color = (200, 0, 0)
        play_sound('incorrect')
        selected_factors = []

def reset_selection():
    """Clears the player's current selection"""
    global selected_value, selected_pos, selected_factors, feedback, feedback_timer, feedback_color
    selected_value = None
    selected_pos = None
    selected_factors = []
    feedback = ""
    feedback_timer = 0
    feedback_color = BLACK

print("🎮 Starting Interactive Factorization...\n")

# ========== MAIN GAME LOOP ==========
running = True
while running:
    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Click on restart button
            if restart_button_rect and restart_button_rect.collidepoint(mx, my):
                restart_game()
            
            # Interaction with grid and keyboard (only during game)
            elif not game_finished:
                # Click on number grid
                for r in range(ROWS):
                    for c in range(COLS):
                        x = MARGIN + c * (CELL_SIZE + MARGIN)
                        y = MARGIN + r * (CELL_SIZE + MARGIN)
                        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                        if rect.collidepoint(mx, my) and not solved[r][c]:
                            selected_value = grid[r][c]
                            selected_pos = (r, c)
                            selected_factors = []
                            feedback = ""
                            feedback_timer = 0
                            play_sound('click')

                # Click on numerical keyboard
                for rect, val in key_rects:
                    if rect.collidepoint(mx, my) and selected_value:
                        selected_factors.append(val)
                        play_sound('click')

                        if len(selected_factors) == 2:
                            check_answer()

        elif event.type == pygame.KEYDOWN:
            # Keyboard shortcuts
            if event.key == pygame.K_ESCAPE:
                reset_selection()
            elif event.key == pygame.K_BACKSPACE and selected_factors:
                selected_factors.pop()
                play_sound('click')
            elif event.key == pygame.K_r:
                restart_game()

    # Decrement feedback timer
    if feedback_timer > 0:
        feedback_timer -= 1

    clock.tick(60)  # 60 FPS

pygame.quit()
sys.exit()
