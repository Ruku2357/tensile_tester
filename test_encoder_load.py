import RPi.GPIO as GPIO
import time
from loadsell import HX711
import smbus
import time

encoder_1 = 25
encoder_2 = 8
encoder_3 = 7
encoder_on = 16

loadcell_1 = 5#SCK
loadcell_2 = 6#DT

#計測値
agree = 0
load = 0
Frag = True

#設定値
loadcell_setting_rate = 0.0000432867  #ロードセルの調整値
date_save=0

#エンコーダの読み取り
def encoder_reading():
    global agree
    encoder_2_status = 0
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(encoder_1,GPIO.IN)
    GPIO.setup(encoder_2,GPIO.IN)
    GPIO.setup(encoder_on,GPIO.IN)
    time.sleep(0.1)
    fragg = 0
    i=0
    end_time = 0
    sleep_time = 0.04
    while True:
        if GPIO.input(encoder_on) == 1:
            break
    print("エンコーダstart")
    start = time.time()
    while Frag:
        while True:
            if GPIO.input(encoder_1) == 0:
                time.sleep(sleep_time)
                if GPIO.input(encoder_1) == 0:
                    break
            encoder_2_status = GPIO.input(encoder_2)
            fragg = 1
            time.sleep(sleep_time)
        if fragg == 1:
            fragg = 0
            if encoder_2_status == 1:
                agree = agree + 1.2#0.36
            elif encoder_2_status == 0:
                agree = agree - 1.2#0.36
                i = i + 1
            end_time = time.time()-start
            if GPIO.input(encoder_on) == 0:
                break
            
        print(agree*2/360)
    print(i)
    print(str(end_time) + "s")

#ロードセルの読み取り
def loadsell_readig():
    global load
    referenceUnit = 1
    hx = HX711(loadcell_2,loadcell_1)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(referenceUnit)
    hx.reset()
    hx.tare()
    while True:
        try:
            load = hx.get_weight(5) * loadcell_setting_rate
            print(str(load) + "N")
            hx.power_down()
            hx.power_up()
            time.sleep(date_save) 
        except:
            print("ロードセルでエラーが起きました。")

do = int(input("何を動かしますか？\nエンコーダ：1\nロードセル：2\n->"))
if do == 1:
    encoder_reading()
elif do == 2:
    loadsell_readig()
else:
    print("end")

