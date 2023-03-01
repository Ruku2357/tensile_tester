import time
import RPi.GPIO as GPIO

encoder_1 = 22 #a相
encoder_2 = 24 #b相
encoder_3 = 26 #z相

agree = 0
status = "first"
encoder_1_status = 0
encoder_2_status = 0
encoder_3_status = 0
encoder_1_status_ago = 0
encoder_2_status_ago = 0

def reading():
    
    GPIO.setwarnings(False)
     
    GPIO.setmode(GPIO.BCM)
     
    GPIO.setup(encoder_1,GPIO.IN)
    GPIO.setup(encoder_2,GPIO.IN)
    GPIO.setup(encoder_3, GPIO.IN)
    time.sleep(0.5)

    while True:
        if GPIO.input(encoder_1) == 1 and encoder_1_status == 0:
            encoder_1_status = 1
        elif GPIO.input(encoder_1) == 0 and encoder_1_status == 1:
            encoder_1_status = 0
        if GPIO.input(encoder_2) == 1 and encoder_2_status == 0:
            encoder_2_status = 1
        elif GPIO.input(encoder_2) == 0 and encoder_2_status == 1:
            encoder_2_status = 0
        if encoder_1_status == encoder_1_status_ago and encoder_2_status == encoder_2_status_ago:
            status = "stop"
        elif encoder_1_status != encoder_1_status_ago and encoder_2_status == encoder_2_status_ago:
            status = "+"
        elif encoder_1_status == encoder_1_status_ago and encoder_2_status != encoder_2_status_ago:
            status = "-"
        if encoder_1_status == 1 and status == "+":
            agree = agree + 0.36
        elif encoder_1_status == 1 and status == "-":
            agree = agree - 0.36
        encoder_1_status_ago = encoder_1_status
        encoder_2_status_ago = encoder_2_status
        encoder_3_status_ago = encoder_3_status
