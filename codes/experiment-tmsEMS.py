import sys
sys.path.append('rehastim-lib/ems_interface/modules/')
sys.path.append('rehastim-lib/ems_interface/tools-and-abstractions/')
from magpy import magstim
import singlepulse
import SerialThingy
import serial

from typing import List, Any

import pygame
import threading
import random
import time
import csv
from datetime import datetime
import AppKit

def config(intensity, frequency, period): # This must be executed before any stim functions; this takes roughly 250 ms to execute
    myMagstim.setPower(intensity, receipt=False, delay=False)
    myMagstim.setFrequency(frequency, receipt=False)
    myMagstim.setDuration(period, receipt=False)
    myMagstim.validateSequence()
    print("config")

def tmsStim(): # Output stim with minimal latency; this requires the config() function to be executed beforehand; need to evaluate latency later
    myMagstim.ignoreCoilSafetySwitch()
    myMagstim.fire(receipt=False)
    print("stim")

def emsStim(): #parameters fixed based on John's paper except the intensity
    global channel, pulse_width, emsIntensity, pulse_count, delay
    if ems_device:
        for i in range(pulse_count):
            #channel number (1-8), pulse width (200-450) in microseconds, intensity (0-100mA, limited 32mA)
            ems.write(singlepulse.generate(channel, pulse_width, emsIntensity))
            time.sleep(delay)

def arm():
    myMagstim.arm(receipt=False, delay=True)
    print("arm")

def disarm():
    myMagstim.disarm(receipt=False)
    print("disarm")
    
    
def show_message(message, color, y_offset=0):
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text, text_rect)
    pygame.display.flip()

def play_sound():
    sound.play()

def stim_output():
    tmsStim()

def count_time():
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= float(emsDelay)/1000:
            emsStim()
            break

def display_waiting_screen():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

        # Clear the screen
        screen.fill(BLACK)
        codename = ""
        if condition == "tms-sub":
            codename = "A"
        elif condition == "tms-sham":
            codename = "B"
        elif condition == "ems-flex":
            codename = "C"
        # Render text
        show_message(f"Condition {codename} | Press SPACE to continue", WHITE)

        # Update the display
        pygame.display.flip()

if __name__ == "__main__":

    myMagstim = magstim.Rapid(serialConnection='<your serial port>', superRapid=1, unlockCode='<you need your own unlock code from Magstim>') # Magstim initialization

    myMagstim.connect() # Connect to magstim device via serial
    myMagstim.rTMSMode(enable=True) # Activate rTMS

    tmsIntensity = 0

    ems_device = True
    FAKE_SERIAL = False
    serial_response_active = False

    # EMS parameters
    channel = 1
    pulse_width = 400
    emsIntensity = 0
    pulse_count = 1
    delay = 0.01

    ems = SerialThingy.SerialThingy(FAKE_SERIAL)
    ems.open_port('<your serial port>',serial_response_active)

    # Initialize Pygame
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

    # Ask for the user's name and intensities
    name = input("Enter your name: ")
    stimIntensity_sub = int(input("Enter sub-threshold intensity: "))
    stimIntensity_sham = stimIntensity_sub #int(input("Enter supra-threshold intensity: "))
    stimIntensity_flex = int(input("Enter flexor intensity: "))
    #stimIntensity_ext = int(input("Enter extensor intensity: "))
    rt = int(input("Enter original reaction time: "))
    emsDelta = int(input("Enter ems adjustment: ")) #80 = original
    #emsToTouch = 50
    #preemptiveGain = 30
    emsDelay = rt - emsDelta #- emsToTouch - preemptiveGain
    print(f"{emsDelay}")

    # Conditions
    conditionOrder = input("condition order: ")
    if conditionOrder == "abc": # tms, sham, ems
        conditions = ["tms-sub", "tms-sham", "ems-flex"]
    elif conditionOrder == "acb": # tms, ems, sham
        conditions = ["tms-sub", "ems-flex", "tms-sham"]
    elif conditionOrder == "bac": # sham, tms, ems
        conditions = ["tms-sham", "tms-sub", "ems-flex"]
    elif conditionOrder == "bca": # sham, ems, tms
        conditions = ["tms-sham", "ems-flex", "tms-sub"]
    elif conditionOrder == "cab": # ems, tms, sham
        conditions = ["ems-flex", "tms-sub", "tms-sham"]
    elif conditionOrder == "cba": # ems, sham, tms
        conditions = ["ems-flex", "tms-sham", "tms-sub"]
    else:
        print("please restart")

    #conditions = ["tms-sub", "tms-sham", "ems-flex", "ems-ext", "no stimulation"]
    #random.shuffle(conditions)

    # Number of trials per condition
    num_trials = 20
    trial_data = []
    total = 0.0

    for condition in conditions:
        display_waiting_screen()
        screen.fill(BLACK)
        AppKit.NSCursor.hide()
        show_message(f"Get Ready!", WHITE) # Condition: {condition}
        pygame.display.flip()
        pygame.time.wait(3000)

        trial_number = 1
        while trial_number <= num_trials:
            screen.fill(BLACK)
            show_message(f"Trial {trial_number}", WHITE)
            sound_thread = threading.Thread(target=play_sound)
            stim_thread = threading.Thread(target=stim_output)
            time_thread = threading.Thread(target=count_time)

            if condition == "tms-sub":
                tmsIntensity = stimIntensity_sub
                config(tmsIntensity, 1, 1)
                arm()
            elif condition == "tms-sham":
                tmsIntensity = stimIntensity_sham
                config(tmsIntensity, 1, 1)
                arm()
            elif condition == "ems-flex":
                channel = 1
                emsIntensity = stimIntensity_flex
            elif condition == "ems-ext":
                channel = 2
                emsIntensity = stimIntensity_ext
            else:
                tmsIntensity = 0  # No stimulation
                emsIntensity = 0

            pygame.time.wait(2000)
            
            # Fixation period with random wait
            screen.fill(BLACK)
            show_message("+", WHITE)
            pygame.display.flip()
            wait_time = random.uniform(1, 3)
            pygame.time.wait(int(wait_time * 1000))

            # Display stimulus and apply stimulation if needed
            sound_thread.start()
            if condition == "tms-sub" or "tms-sham":
                pygame.time.wait(int(45))
            elif condition == "ems-flex":
                pygame.time.wait(int(20))
            start_time = time.time()
            #if condition != "no stimulation":
            if condition == "tms-sub" or condition == "tms-sham":
                stim_thread.start()
            elif condition == "ems-ext" or condition == "ems-flex":
                time_thread.start()
            screen.fill(WHITE)
            pygame.display.flip()
            stimulus_shown = True

            # Wait for response
            response_time = None
            pygame.event.clear()
            while stimulus_shown:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        myMagstim.disconnect()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            response_time = (time.time() - start_time) * 1000
                            response_time = round(response_time, 2)
                            stimulus_shown = False
                            pygame.mixer.stop()
                
                # if condition == "ems-flex" and time.time() == start_time + emsDelay:
                #     emsStim()
            
            if response_time is not None:
                # Ask for Likert scale rating
                rating = None
                screen.fill(BLACK)
                # if condition == "tms-supra" or condition == "ems-ext":
                #     show_message("not at all -> 1 2 3 4 5 6 7 <- totally distracted", WHITE)
                # else:
                show_message("I did not do it -> 1 2 3 4 5 6 7 <- I did it", WHITE)
                pygame.display.flip()
                waiting_for_rating = True
                while waiting_for_rating:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            myMagstim.disconnect()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if pygame.K_1 <= event.key <= pygame.K_7:
                                rating = event.key - pygame.K_0
                                waiting_for_rating = False

                trial_data.append((condition, trial_number, response_time, tmsIntensity, emsIntensity, rating, emsDelta))
                total += response_time
                trial_number += 1

            screen.fill(BLACK)
            show_message(f"reaction time: {round(response_time)} ms", WHITE)
            pygame.time.wait(2500)
            screen.fill(BLACK)
            show_message("", WHITE)
            pygame.time.wait(1000)

    pygame.quit()
    rt = round((total/(trial_number-1)*3))
    print(f"reaction time: {rt}")

    # Save data to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/tmsEMS_{name}_{timestamp}.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Condition", "Trial", "Reaction Time (ms)", "TMS Intensity", "EMS Intensity", "Rating", "EMS Timing (ms)"])
        writer.writerows(trial_data)

    print(f"Data saved to {filename}")
    myMagstim.disconnect()
    sys.exit()
