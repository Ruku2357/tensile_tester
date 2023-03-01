
import time
import RPi.GPIO as GPIO
from loadsell import HX711
import smbus
import threading

#ピン配置
stepping_en = 18
stepping_dir = 23
stepping_pul = 24
stepping_on = 12

Frag = False
pulse_rev = 6400 #pulse/revの値

encoder_1 = 25
encoder_2 = 8
encoder_3 = 7
encoder_on = 16

loadcell_1 = 20#SCK
loadcell_2 = 21#DT

#計測値
agree = 0
load = 0
Frag = True
lazer_dis = 0

#設定値
loadcell_setting_rate = 0.0000432867  #ロードセルの調整値
date_save=0.1
encoder_Frag = 0
lazer_Frag = 0
load_Frag = 0
stepp_Frag = 0

#ステッピングモーター
def stepping_move(direction,agree:float,speed:float):#方向(右:1、左:2)　角度(deg)　スピード(ms/r)

    global Frag
    global stepp_Frag
    GPIO.setwarnings(False)
     
    GPIO.setmode(GPIO.BCM)
     
    GPIO.setup(stepping_dir,GPIO.OUT)
    GPIO.setup(stepping_pul,GPIO.OUT)
    GPIO.setup(stepping_en, GPIO.OUT)
    GPIO.setup(stepping_on, GPIO.OUT)
    time.sleep(0.5)

    movetime_pulse = int(float(agree) * pulse_rev // 360) * 2
    movespeed = speed / pulse_rev / 2
    #print(movetime_pulse)
    #aa = int(input("開始パルス->"))
    start = time.time()
    print("ステッピングモータ開始")
    stepp_Frag = 1
    if direction == 1:#本番
        GPIO.output(stepping_dir,True)
        GPIO.output(stepping_en,True)
        for a in range(movetime_pulse):
            GPIO.output(stepping_pul,True)
            time.sleep(movespeed/2)
            GPIO.output(stepping_pul,False)
            time.sleep(movespeed/2)
            #if a == aa:
                #GPIO.output(stepping_on,True)
            #elif a == aa + 12800:
                #GPIO.output(stepping_on,False)

    elif direction == 2:
        GPIO.output(stepping_dir,False)
        GPIO.output(stepping_en,True)
        for a in range(movetime_pulse):
            GPIO.output(stepping_pul,True)
            time.sleep(movespeed/2)
            GPIO.output(stepping_pul,False)
            time.sleep(movespeed/2)

    Frag = False
    stepp_Frag = 0
    GPIO.output(stepping_en,False)
    GPIO.output(stepping_dir,False)
    GPIO.output(stepping_pul,False)
    GPIO.output(stepping_on,False)
    end_time = time.time()-start
    print(str(end_time) + "s")
    print("ステッピングモータ終了")

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
    print("エンコーダ開始")
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
            if encoder_Frag == 0:
                break
    print("エンコーダ終了")
            
        #print(agree*2/360)
    #print(i)
    #print(str(end_time) + "s")

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
            if load_Frag == 0:
                break
        except:
            print("ロードセルでエラーが起きました。")

def lazer():
    global lazer_dis
    i2c = smbus.SMBus(1)
    addr=0x68 #アドレス?編集が必要
    config = 0b10011011 #右から4つ目はシステム稼働時は0のほうがいいかも。大丈夫そうな１のまま。
    Vref=0.25733 #2.048 #基準電圧そのままでいい
    
    i2c.write_byte(addr, config) #16bit
    time.sleep(0.1)
    
    def swap16(x):
        return (((x << 8) & 0xFF00) | ((x >> 8) & 0x00FF))

    def sign16(x):
        return ( -(x & 0b1000000000000000) | (x & 0b0111111111111111) )
    data = i2c.read_word_data(addr, config)
    raw = swap16(int(hex(data), 16))
    raw_s = sign16(raw)
    volts_f = (round((Vref * raw_s / 32767), 4) * -2817.0422 + 720.314702)
    print("レーザー開始")
    
    while True:
        data = i2c.read_word_data(addr, config)
        raw = swap16(int(hex(data), 16))
        raw_s = sign16(raw)
        lazer_dis = volts_f - (round((Vref * raw_s / 32767), 4) * -2817.0422 + 720.314702)
        #print(lazer_dis)
        time.sleep(date_save)
        if lazer_Frag == 0:
            break
    print("レーザー終了")

print("テスト開始")
step_control = threading.Thread(target=stepping_move, args=(2,45.0,240.0-1.93))
step_control.setDaemon(True)
step_control.start()
encoder_Frag = 1
encoder_control = threading.Thread(target=encoder_reading)
encoder_control.setDaemon(True)
encoder_control.start()
aa = 0
while True:
    if stepp_Frag == 1:
        break
while True:
    if stepp_Frag == 0:
        break
    elif aa >= 40:
        print("ステッピングモータ異常1*************")
        break
    aa = aa + 1
    time.sleep(1)
if agree <= 46 and agree >=44:
    print("エンコーダ正常-----------------")
    print(agree)
else:
    print("エンコーダ異常*************")
    print(agree)
encoder_Frag = 0
time.sleep(2)
lazer_Frag = 1
lazer_control = threading.Thread(target=lazer)
lazer_control.setDaemon(True)
lazer_control.start()
time.sleep(1)
step_control = threading.Thread(target=stepping_move, args=(1,720.0,5.0-1.93))
step_control.setDaemon(True)
step_control.start()
aa = 0
while True:
    if stepp_Frag == 1:
        break
while True:
    if stepp_Frag == 0:
        break
    elif aa >= 20:
        print("ステッピングモータ異常2*************")
        break
    aa = aa + 1
    time.sleep(1)
if lazer_dis <= 5 and lazer_dis >= 3:
    print("レーザー変位計正常-----------------")
    print(lazer_dis)
else:
    print("レーザー変位計異常*************")
    print(lazer_dis)
lazer_Frag = 0
loadsell_readig()
aa = 0
while True:
    if load <= 0.01 and load >=-0.01:
        time.sleep(1)
        if load <= 0.01 and load >=-0.01:
            time.sleep(1)
            if load <= 0.01 and load >=-0.01:
                time.sleep(1)
                if load <= 0.01 and load >=-0.01:
                    time.sleep(1)
                    if load <= 0.01 and load >=-0.01:
                        print("ロードセル正常-----------------")
                        load_Frag = 0
                        break
    elif aa > 10:
        print("ロードセル異常****************")
        print(load)
        load_Frag = 0
        break
    aa = aa + 1
    time.sleep(1)
