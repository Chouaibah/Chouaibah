from time import sleep
from random import uniform
from machine import Pin, UART

# Configuration des broches
led_R = Pin(2, Pin.OUT)
led_G = Pin(3, Pin.OUT)
led_Y = Pin(4, Pin.OUT)

uart = UART(1, baudrate=9600, tx=8, rx=9, timeout=2000)

# Declaration des variables pH et salinity
ph = 0
salt = 0
led_R.value(0)
led_G.value(0)
led_Y.value(0)


def generate_values():
    global ph, salt
    ph = round(uniform(6.5, 8.5), 2) 
    salt = round(uniform(0.01, 0.1), 3) 

def send_at_command(command):
    uart.write(command + b'\r\n')
    sleep(1)
    response = uart.read()
    if response:
        print("Réponse du module GSM:", response.decode())
    else:
        print("Aucune réponse du module GSM")
        return send_at_command(command)

def envoyer_sms(numero, message):
    send_at_command(b'AT+CMGF=1')
    sleep(1)
    send_at_command(b'AT+CMGS="' + numero + b'"')
    sleep(1)
    send_at_command(message)
    sleep(1)
    uart.write(bytes([26]))
    sleep(1)

def ecouter_appels():
    send_at_command(b'AT+CLIP=1')
    while True:
        led_R.value(1)
        if uart.any():
            response = uart.readline().strip()
            if response.startswith(b'+CLIP:'):
                led_R.value(0)
                led_Y.value(1)
                print("Appel entrant détecté")
                numero_appelant = response.split(b'"')[1]
                sleep(1)
                send_at_command(b'ATH')
                sleep(3)
                generate_values()
                print("Nouvelle valeur de pH: {}, nouvelle valeur de salinité: {}".format(ph,salt))
                envoyer_sms(numero_appelant, b"La valeur de PH : {} et La valeur de Salinite : {}".format(ph,salt))
                led_Y.value(0)
                led_G.value(1)
                sleep(3)
                led_R.value(1)
                led_G.value(0)
sleep(3)
ecouter_appels()
