import RPi.GPIO as GPIO
import time

#ピン配置
stepping_en = 18
stepping_dir = 23
stepping_pul = 24
stepping_on = 12

Frag = False
pulse_rev = 6400 #pulse/revの値

#ステッピングモーター
def stepping():
    global Frag
    order_direction = int(input("どっち? 上げる:1、下げる:2 -> "))
    order_agree = 360 * float(input("何回転(小数点可)? -> "))
    order_speed = float(input("1回転あたりの時間(s/r)? -> ")) -1.93
    stepping_move(order_direction,order_agree,order_speed)

def stepping_move(direction,agree:float,speed:float):#方向(右:1、左:2)　角度(deg)　スピード(ms/r)

    global Frag
    GPIO.setwarnings(False)
     
    GPIO.setmode(GPIO.BCM)
     
    GPIO.setup(stepping_dir,GPIO.OUT)
    GPIO.setup(stepping_pul,GPIO.OUT)
    GPIO.setup(stepping_en, GPIO.OUT)
    GPIO.setup(stepping_on, GPIO.OUT)
    time.sleep(0.1)

    movetime_pulse = int(float(agree) * pulse_rev // 360) * 2
    movespeed = speed / pulse_rev / 2
    print(movetime_pulse)
    start = time.time()

    if direction == 1:#本番
        GPIO.output(stepping_dir,True)
        GPIO.output(stepping_en,True)
        for a in range(movetime_pulse):
            GPIO.output(stepping_pul,True)
            time.sleep(movespeed/2)
            GPIO.output(stepping_pul,False)
            time.sleep(movespeed/2)
            if a == aa:
                GPIO.output(stepping_on,True)
            elif a == aa + 12800:
                GPIO.output(stepping_on,False)

    elif direction == 2:
        GPIO.output(stepping_dir,False)
        GPIO.output(stepping_en,True)
        for a in range(movetime_pulse):
            GPIO.output(stepping_pul,True)
            time.sleep(movespeed/2)
            GPIO.output(stepping_pul,False)
            time.sleep(movespeed/2)

    Frag = False
    GPIO.output(stepping_en,False)
    GPIO.output(stepping_dir,False)
    GPIO.output(stepping_pul,False)
    GPIO.output(stepping_on,False)
    end_time = time.time()-start
    print(str(end_time) + "s")

stepping()
