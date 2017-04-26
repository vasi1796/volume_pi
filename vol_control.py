# include RPi libraries in to Python code
import RPi.GPIO as GPIO
import time
import pygame
import threading
from threading import Thread
import argparse

# instantiate GPIO as an object
GPIO.setmode(GPIO.BCM)

# define GPIO pins
a_pin = 18
b_pin = 23
led_pins=[5,6,13,19,26]
for pin in led_pins:
    GPIO.setup(pin,GPIO.OUT)
GPIO.setwarnings(False)

# create discharge function for reading capacitor data
def discharge():
    #se da curent catre condensator din pinul a=18
    GPIO.setup(a_pin, GPIO.IN)
    #pinul b lasa curentul sa treaca
    GPIO.setup(b_pin, GPIO.OUT)
    #se opreste voltajul catre pinul b
    GPIO.output(b_pin, GPIO.LOW)
    #se asteapta 0.005 secunde incarcarea condensatorului
    time.sleep(0.005)

# create time function for capturing analog count value
def charge_time():
    #se inverseaza pinii, analog read potentiometer raspberry pi
    GPIO.setup(b_pin, GPIO.IN)
    GPIO.setup(a_pin, GPIO.OUT)
    count = 0
    GPIO.output(a_pin, GPIO.HIGH)
    #se numara valoarea analogica a potentiometrului
    while not GPIO.input(b_pin):
        count = count +1
    #se returneaza valoarea pentru a fi folosita de leduri
    return count

# create analog read function for reading charging and discharging data
#toata functia este pe partea electronica a potentiometrului, nu are legatura cu ledurile
def analog_read():
    discharge()
    return charge_time()

def turn_leds_off(from_pin):
    for pin in led_pins[from_pin:]:
        GPIO.output(pin,GPIO.LOW)

def turn_leds_on(to_pin):
    for pin in led_pins[:to_pin]:
        GPIO.output(pin,GPIO.HIGH)

#control the leds
def light_led(vol):
    if vol<100:
        turn_leds_on(1)
        turn_leds_off(1)
    elif vol>100 and vol<200:
        turn_leds_on(2)
        turn_leds_off(2)
    elif vol>200 and vol<300:
        turn_leds_on(3)
        turn_leds_off(3)
    elif vol>300 and vol<400:
        turn_leds_on(4)
        turn_leds_off(4)
    elif vol>400:
        turn_leds_on(5)

#control volume of song
def vol_control(vol):
    """if vol<100:
        pygame.mixer.music.set_volume(0.1)
    elif vol>100 and vol<200:
        pygame.mixer.music.set_volume(0.3)
    elif vol>200 and vol<300:
        pygame.mixer.music.set_volume(0.5)
    elif vol>300 and vol<400:
        pygame.mixer.music.set_volume(0.7)
    elif vol>400:
        pygame.mixer.music.set_volume(0.9)"""
    #not stable because of potentiometer quality
    #but it works better because of discretization of volume values
    max_pot=480.0
    pygame.mixer.music.set_volume(vol/max_pot)

#function for parsing files
def parse_args():
    #descriere ce face scriptul, exemplu cauta python script help
    parser = argparse.ArgumentParser(description='Volume controller for song')
    parser.add_argument('--file', help='Path to song file', type=str)
    args = parser.parse_args()
    #returneaza rick.mp3 sau orice melodie ai pus in argumentul --file
    return args.file

if __name__ == "__main__":
    args=parse_args()
    pygame.mixer.init()
    #in args este un string cu numele melodiei, fie e calea catre melodie fie e doar numele fisierului
    pygame.mixer.music.load(args)
    pygame.mixer.music.play()
    try:
        while pygame.mixer.music.get_busy() == True:
            vol=analog_read()
            Thread(target = vol_control, args=[vol]).start()
            Thread(target = light_led, args=[vol]).start()
            print(vol)
            time.sleep(0.4)
    except KeyboardInterrupt:
        print "you pressed ctrl-c"
    finally:
        GPIO.cleanup()
