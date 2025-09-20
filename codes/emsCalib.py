# PARAMETERS
# start with following:
# ems.write(singlepulse.generate(1,300,7)) #channel number (1-8), pulse width (200-450) in microseconds, intensity (0-100mA, limited 32mA)

import sys
sys.path.append('rehastim-lib/ems_interface/modules/')
sys.path.append('rehastim-lib/ems_interface/tools-and-abstractions/')
import pygame
import singlepulse
import SerialThingy
import time
import serial

from typing import List, Any

ems_device = True
FAKE_SERIAL = False
serial_response_active = False

# EMS parameters
# ======================================================= #
channel = 1
pulse_width = 400
intensity = 4
pulse_count = 70
delay = 0.02
# ======================================================= #

prevChannel = 1


ems = SerialThingy.SerialThingy(FAKE_SERIAL)
ems.open_port('<your serial port>',serial_response_active)
# if len(sys.argv) > 1:
#         ems.open_port(str(sys.argv[1]),serial_response_active) # pass the port via the command line, as an argument
# else:
#         ems.open_port(serial_response_active)

def stim(): #parameters fixed based on John's paper except the intensity
    global channel, pulse_width, intensity, pulse_count, delay
    if ems_device:
        for i in range(pulse_count):
            #channel number (1-8), pulse width (200-450) in microseconds, intensity (0-100mA, limited 32mA)
            ems.write(singlepulse.generate(channel, pulse_width, intensity))
            time.sleep(delay)


def show_message(message, color, y_offset=0):
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text, text_rect)
    pygame.display.flip()


if __name__ == "__main__":
    # First connect to EMS hardware
    # if ems_device: ems_init()

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

    running = True
    while running:
        screen.fill(BLACK)
        show_message(f"Intensity: {intensity} | Channel: {channel}", WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP4 or event.key == pygame.K_4:
                    intensity = max(1, intensity - 1)
                elif event.key == pygame.K_KP6 or event.key == pygame.K_6:
                    intensity = min(20, intensity + 1)
                elif event.key == pygame.K_KP2 or event.key == pygame.K_2:
                    prevChannel = channel
                    channel = max(1, channel - 1)
                elif event.key == pygame.K_KP8 or event.key == pygame.K_8:
                    prevChannel = channel
                    channel = min(2, channel + 1)
                elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    stim()

                if channel != prevChannel:
                    intensity = 4
                    prevChannel = channel
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()
