import time

import RPi.GPIO as GPIO

def reading(sensor):
    
    GPIO.setwarnings(False)
     
    GPIO.setmode(GPIO.BCM)
    TRIG = 14
    ECHO = 15

    miss_distance = -1
     
    if sensor == 1:
        GPIO.setup(TRIG,GPIO.OUT)
        GPIO.setup(ECHO,GPIO.IN)
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(0.3)
         
        GPIO.output(TRIG, True)#超音波の送信
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
 
        while GPIO.input(ECHO) == 0: #ECHOがHIGHになってる
          signaloff = time.time()
         
        while GPIO.input(ECHO) == 1: #ECHOがLOWになった瞬間
          signalon = time.time()
 
        timepassed = signalon - signaloff #送信から受信の時間
        distance = timepassed * 340 * 100 / 2 #cm 
        
        if distance <= 300:
          #print("sensor1：" + str(distance) + "cm")
          return distance
        if distance > 300:
          #print("エラー1(300cmまで)")
          return miss_distance

    else:
        print("1でセンサー起動．")


"ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー"


import time
import sys

import motor_arm

import RPi.GPIO as GPIO

def move(order, second):

    #左
    motor1_pin = 17 #前
    motor2_pin = 27 #後

    #右
    motor3_pin = 24 #前
    motor4_pin = 23 #後


    motor5_pin = 5
    motor6_pin = 6

    GPIO.setwarnings(False)
     
    GPIO.setmode(GPIO.BCM)
    # GPIO出力モードを1に設定する
    GPIO.setup(motor1_pin,GPIO.OUT)
    GPIO.setup(motor2_pin,GPIO.OUT)
    GPIO.setup(motor3_pin,GPIO.OUT)
    GPIO.setup(motor4_pin,GPIO.OUT)
    GPIO.setup(motor5_pin,GPIO.OUT)
    GPIO.setup(motor6_pin,GPIO.OUT)
    time.sleep(0.3)

    if order == "go":
        if second == 0:
            print("goを止めるときはstop 0コマンド！")
        else:
            print(str(second)+"s,go")  
        GPIO.output(motor1_pin, True)
        GPIO.output(motor2_pin, False)
        GPIO.output(motor3_pin, True)
        GPIO.output(motor4_pin, False)
        
    elif order == "back":
        if second == 0:
            print("backを止めるときはstop 0コマンド！")
        else:
            print(str(second)+"s,go")  
        GPIO.output(motor1_pin, False)
        GPIO.output(motor2_pin, True)
        GPIO.output(motor3_pin, False)
        GPIO.output(motor4_pin, True)

    elif order == "right":
        if second == 0:
            print("右回転を止めるときはstop 0コマンド！")
        else:
            print(str(second)+"s,右回転")
        #GPIO.cleanup()
        GPIO.output(motor1_pin, True)
        GPIO.output(motor2_pin, False)
        GPIO.output(motor3_pin, False)
        GPIO.output(motor4_pin, True)
    elif order == "left":
        if second == 0:
            print("左回転を止めるときはstop 0コマンド！")
        else:
            print(str(second)+"s,左回転")  
        #GPIO.cleanup()
        GPIO.output(motor1_pin, False)
        GPIO.output(motor2_pin, True)
        GPIO.output(motor3_pin, True)
        GPIO.output(motor4_pin, False)

    elif order == "right_only":
        if second == 0:
            print("right_onlyを止める時は 0コマンド！")
        else:
            print(str(second)+"s,right_only")
        GPIO.output(motor3_pin, True)
        GPIO.output(motor4_pin, False)

    elif order == "left_only":
        if second == 0:
            print("left_onlyを止める時は 0コマンド！")
        else:
            print(str(second)+"s,left_only")
        GPIO.output(motor1_pin, True)
        GPIO.output(motor2_pin, False)

    elif order == "right_only_back":
        if second == 0:
            print("right_onlyを止める時は 0コマンド！")
        else:
            print(str(second)+"s,right_only")
        GPIO.output(motor3_pin, False)
        GPIO.output(motor4_pin, True)

    elif order == "left_only_back":
        if second == 0:
            print("left_onlyを止める時は 0コマンド！")
        else:
            print(str(second)+"s,left_only")
        GPIO.output(motor1_pin, False)
        GPIO.output(motor2_pin, True)

    elif order == "arm_only":
        if second == 0:
            print("arm_onlyを止める時は 0コマンド！")
        else:
            print(str(second)+"s,arm_only")
        GPIO.output(motor5_pin, False)
        GPIO.output(motor6_pin, True)

    elif order == "dan":
        if second == 0:
            print("left_onlyを止める時は 0コマンド！")
        else:
            print(str(second)+"s,only")
        GPIO.output(motor1_pin, True)
        GPIO.output(motor2_pin, False)
        GPIO.output(motor3_pin, True)
        GPIO.output(motor4_pin, False)
        GPIO.output(motor5_pin, True)
        GPIO.output(motor6_pin, False)

    elif order == "end":
        if second == 0:
            print("left_を止める時は 0コマンド！")
        else:
            print(str(second))
        GPIO.cleanup()


    time.sleep(second)

    # 第4引数が0の場合は、ブレーキをしない
    # 第3引数がbreakの場合は、ブレーキ
    if order == "stop" or second != 0:
        print("モーターstop")
        GPIO.output(motor1_pin, True)
        GPIO.output(motor2_pin, True)
        GPIO.output(motor3_pin, True)
        GPIO.output(motor4_pin, True)
        GPIO.output(motor5_pin, True)
        GPIO.output(motor6_pin, True)

    GPIO.output(motor1_pin, False)
    GPIO.output(motor2_pin, False)
    GPIO.output(motor3_pin, False)
    GPIO.output(motor4_pin, False)
    GPIO.output(motor5_pin, False)
    GPIO.output(motor6_pin, False)
    