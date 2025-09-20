import sys
from typing import List

import pygame
import threading
import random
import time
import csv
from datetime import datetime
import AppKit
    
def show_message(message, color, y_offset=0):
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text, text_rect)
    pygame.display.flip()

def play_sound():
    sound.play()

if __name__ == "__main__": 
    #Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound('tone-500Hz.wav')

    # Screen dimensions
    WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Reaction Time Test")

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    # Font
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    # Ask for the user's name
    name = input("Enter your name: ")

    # Number of trials
    num_trials = 10
    trial_data = []
    total = 0.0

    # delay before starting the first trial
    screen.fill(BLACK)
    AppKit.NSCursor.hide()
    show_message("Get Ready!", WHITE)
    pygame.display.flip()
    pygame.time.wait(3000)

    # Game loop
    running = True
    clock = pygame.time.Clock()
    trial_number = 1

    while trial_number <= num_trials and running:
        screen.fill(BLACK)
        show_message(f"Trial {trial_number}", WHITE)
        sound_thread = threading.Thread(target=play_sound)

        pygame.time.wait(2000)
        
        # Fixation period with random wait
        screen.fill(BLACK)
        show_message("+", WHITE)
        pygame.display.flip()
        wait_time = random.uniform(1, 3)
        pygame.time.wait(int(wait_time * 1000))

        sound_thread.start()
        pygame.time.wait(int(20))
        # Display stimulus
        start_time = time.time()
        screen.fill(WHITE)
        pygame.display.flip()
        stimulus_shown = True

        # Wait for response
        response_time = None
        pygame.event.clear()
        while stimulus_shown:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    stimulus_shown = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        response_time = (time.time() - start_time) * 1000
                        response_time = round(response_time, 2)
                        stimulus_shown = False
                        pygame.mixer.stop()
        
        if response_time is not None:
            trial_data.append((trial_number, response_time))
            total += response_time
            trial_number += 1

        screen.fill(BLACK)
        show_message(f"reaction time: {round(response_time)} ms", WHITE)
        pygame.time.wait(2500)
        screen.fill(BLACK)
        show_message("", WHITE)
        pygame.time.wait(1000)

    pygame.quit()
    rt = round((total/(trial_number-1)))
    print(f"reaction time: {rt}")
    # Save data to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/rtPractice_{name}_{timestamp}.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Trial", "Reaction Time (s)"])
        writer.writerows(trial_data)

    print(f"Data saved to {filename}")
    sys.exit()