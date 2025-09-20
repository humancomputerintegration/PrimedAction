import sys
from magpy import magstim
import pygame
import time

def config(intensity, frequency, period): # This must be executed before any stim functions; this takes roughly 250 ms to execute
    myMagstim.setPower(intensity, receipt=False, delay=False)
    myMagstim.setFrequency(frequency, receipt=False)
    myMagstim.setDuration(period, receipt=False)
    myMagstim.validateSequence()

def stim(): # Output stim with minimal latency; this requires the config() function to be executed beforehand; need to evaluate latency later
    myMagstim.ignoreCoilSafetySwitch()
    myMagstim.fire(receipt=False)

def arm():
    myMagstim.arm(receipt=False, delay=True)

def disarm():
    myMagstim.disarm(receipt=False)
    
def show_message(message, color, y_offset=0):
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text, text_rect)
    pygame.display.flip()

if __name__ == "__main__": 

    myMagstim = magstim.Rapid(serialConnection='<your serial port>', superRapid=1, unlockCode='<you need your own unlock code from Magstim>') # Magstim initialization

    myMagstim.connect() # Connect to magstim device via serial
    myMagstim.rTMSMode(enable=True) # Activate rTMS

    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stim Intensity Control")

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    # Font
    font = pygame.font.Font(None, 74)

    # Initial intensity
    intensity = 40
    config(intensity, 1, 1)
    arm()

    running = True
    while running:
        screen.fill(BLACK)
        show_message(f"Intensity: {intensity}", WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP4:
                    intensity = max(5, intensity - 5)
                    disarm()
                    config(intensity, 1, 1)
                    arm()
                elif event.key == pygame.K_KP6:
                    intensity = min(100, intensity + 5)
                    disarm()
                    config(intensity, 1, 1)
                    arm()
                elif event.key == pygame.K_KP_ENTER:
                    stim()
        
        pygame.display.flip()

    pygame.quit()
    myMagstim.disconnect()
    sys.exit()
