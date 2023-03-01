import RPi.GPIO as GPIO


stepping_en = 18
stepping_dir = 23
stepping_pul = 24

encoder_1 = 25
encoder_2 = 8
encoder_3 = 7

loadcell_1 = 20#SCK
loadcell_2 = 21#DT

GPIO.setwarnings(False)
    
GPIO.setmode(GPIO.BCM)

GPIO.setup(encoder_1,GPIO.OUT)
GPIO.setup(encoder_2,GPIO.OUT)
GPIO.setup(encoder_3,GPIO.OUT)
GPIO.setup(stepping_en,GPIO.OUT)
GPIO.setup(stepping_dir,GPIO.OUT)
GPIO.setup(stepping_pul,GPIO.OUT)
GPIO.setup(loadcell_1,GPIO.OUT)
GPIO.setup(loadcell_2,GPIO.OUT)


GPIO.cleanup()

print("ラズパイをリセットしました。")
