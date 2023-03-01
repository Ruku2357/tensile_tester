from os import terminal_size
import RPi.GPIO as GPIO
import time
import csv
import numpy
from loadsell import HX711
import threading
import datetime
from matplotlib import pyplot

"""
ステッピングモータ
標線間の距離の1%を1分間で伸ばすスピード
分解能0.00015625mm/パルス
分解能0.028125deg/パルス
エンコーダ
分解能0.36deg
"""

#ピン配置
stepping_en = 18
stepping_dir = 23
stepping_pul = 24

encoder_1 = 25
encoder_2 = 8
encoder_3 = 7

loadcell_1 = 20#SCK
loadcell_2 = 21#DT

#設定値
update_time = 1 #グラフの更新時間とデータ取得の時間
speed = 50
movespeed = (120/0.001/speed - 1.93) / 6400 / 2#ステッピングモータの1パルスあたりの時間　1分間に0.5mm
over_rate = 1 #自動の時の測定を開始する閾値(N)
date_read_time = 0.05
date_save_time = 0.2
date_amount = 50

Frag = False
loadcell_setting_rate = 0.0001259 #ロードセルの調整値
Frag_stop = False
frag_preparation_load = False
name = ""

#計測値
agree = 0
dis_encoder = 0
dis_step = 0
load = 0

#エンコーダの読み取り
def encoder_reading():
    global agree
    global dis_encoder
    encoder_2_status = 0
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(encoder_1,GPIO.IN)
    GPIO.setup(encoder_2,GPIO.IN)
    time.sleep(0.1)
    fragg = 0
    sleep_time = 0.04
    print("エンコーダ開始")
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
                agree = agree - 1.2 #0.36
            dis_encoder = agree * 2 / 360 * -1
    print("エンコーダ終了")

#ステッピングモーター
def stepping_move():
    global dis_step
    #print("ステッピングモーター開始")
    GPIO.setwarnings(False)
     
    GPIO.setmode(GPIO.BCM)
     
    GPIO.setup(stepping_dir,GPIO.OUT)
    GPIO.setup(stepping_pul,GPIO.OUT)
    GPIO.setup(stepping_en, GPIO.OUT)
    time.sleep(0.1)

    GPIO.output(stepping_dir,True)#向きを合わせる
    GPIO.output(stepping_en,True)
    while Frag:
        GPIO.output(stepping_pul,True)
        time.sleep(movespeed/2)
        GPIO.output(stepping_pul,False)
        time.sleep(movespeed/2)
        dis_step = dis_step + (0.028125 * 2 / 360)


    GPIO.output(stepping_en,False)
    GPIO.output(stepping_dir,False)
    GPIO.output(stepping_pul,False)
    print("ステッピングモータ終了")

#ロードセルの読み取り
#出てくる数字が適当だからキャビテーションする
def loadcell_readig():
    global load
    global frag_preparation_load
    referenceUnit = 1
    first_load = 0
    print("ロードセル開始")
    hx = HX711(loadcell_2,loadcell_1)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(referenceUnit)
    hx.reset()
    hx.tare()
    while Frag:
        try:
            load = hx.get_weight(5) * loadcell_setting_rate - first_load
            hx.power_down()
            hx.power_up()
            time.sleep(date_read_time)
            if frag_preparation_load == True:
                first_load = load
                frag_preparation_load = False
        except:
            print("ロードセルでエラーが起きました。")
    print("ロードセル終了")

"""
def lazer_reading():
    global dis_lazer 
    global frag_preparation_lazer
    i2c = smbus.SMBus(1)
    addr=0x68 #アドレス?編集が必要
    config = 0b10011011 #右から4つ目はシステム稼働時は0のほうがいいかも。大丈夫そうな１のまま。
    Vref=0.25733 #2.048 #基準電圧そのままでいい
    first_dis_lazer = 0
    
    i2c.write_byte(addr, config) #16bit
    time.sleep(0.1)
    
    def swap16(x):
        return (((x << 8) & 0xFF00) | ((x >> 8) & 0x00FF))

    def sign16(x):
        return ( -(x & 0b1000000000000000) | (x & 0b0111111111111111) )
    print("レーザー変位計開始")
    data = i2c.read_word_data(addr, config)
    raw = swap16(int(hex(data), 16))
    raw_s = sign16(raw)
    dis_lazer_first = (round((Vref * raw_s / 32767), 4) * -2817.0422 + 720.314702)
    time.sleep(0.1)
    
    while Frag:
        data = i2c.read_word_data(addr, config)
        raw = swap16(int(hex(data), 16))
        raw_s = sign16(raw)
        dis_lazer = dis_lazer_first - (round((Vref * raw_s / 32767), 4) * -2817.0422 + 720.314702) - first_dis_lazer
        time.sleep(date_read_time)
        if frag_preparation_lazer == True:
            first_dis_lazer = dis_lazer
            frag_preparation_lazer = False
    print("レーザー変位計終了")
"""

def date_save():
    now_date = datetime.datetime.now()
    print("データ記録開始")

    with open(now_date.strftime('%m月%d日%H_%M_%S_') + name + '.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(["time" ,"load","agree" ,"dis(encoder)", "dis(step)"])
    while Frag:
        now = datetime.datetime.now()
        time_now = now.strftime("%H:%M:%S")
        with open(now_date.strftime('%m月%d日%H_%M_%S_') + name + '.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([time_now ,load,agree , dis_encoder, dis_step])
        
        time.sleep(date_save_time)
    
    print("データ記録終了")

def date_show():

    load_list = [0] * date_amount
    distance_encoder_list = [0] * date_amount
    distance_step_list = [0] * date_amount

    fig = pyplot.figure(figsize=(12, 8))
    load_plot_fig = fig.add_subplot(2, 1,1)
    distance_encoder_plot_fig = fig.add_subplot(2, 2, 3)
    distance_step_plot_fig = fig.add_subplot(2, 2, 4)

    time_list = numpy.arange(date_amount*update_time*-1+update_time, 1,update_time)

    load_list_np = numpy.array(load_list)
    load_plot, = load_plot_fig.plot(time_list,load_list_np)#荷重グラフ
    load_plot_fig.set_title('load graph')
    load_plot_fig.set_xlabel("time(s)")
    load_plot_fig.set_ylabel("load(N)")

    distance_encoder_list_np = numpy.array(distance_encoder_list)
    distance_encoder_plot, = distance_encoder_plot_fig.plot(time_list,distance_encoder_list_np)#伸びグラフ
    distance_encoder_plot_fig.set_title('position encoder graph')
    distance_encoder_plot_fig.set_xlabel("time(s)")
    distance_encoder_plot_fig.set_ylabel("position(mm)")

    distance_step_list_np = numpy.array(distance_step_list)
    distance_step_plot, = distance_step_plot_fig.plot(time_list,distance_step_list_np)#伸びグラフ
    distance_step_plot_fig.set_title('position step graph')
    distance_step_plot_fig.set_xlabel("time(s)")
    distance_step_plot_fig.set_ylabel("position(mm)")

    print("データ表示開始")

    while Frag:
    
        load_list.pop(0)
        load_list.append(load)
        load_plot.set_ydata(load_list) 

        distance_encoder_list.pop(0)
        distance_encoder_list.append(dis_encoder)
        distance_encoder_plot.set_ydata(distance_encoder_list)

        distance_step_list.pop(0)
        distance_step_list.append(dis_step)
        distance_step_plot.set_ydata(distance_step_list)

        load_plot_fig.set_xlim(date_amount*-1+1,0)
        load_plot_fig.set_ylim((load-6.0),(load+6.0))
        load_plot_fig.grid(which = "major", axis = "x", color = "blue", alpha = 0.8,linestyle = "--", linewidth = 1)
        load_plot_fig.grid(which = "major", axis = "y", color = "green", alpha = 0.8,linestyle = "--", linewidth = 1)

        distance_encoder_plot_fig.set_xlim(date_amount*-1+1,0)
        distance_encoder_plot_fig.set_ylim((dis_encoder-1.0),(dis_encoder+1.0))
        distance_encoder_plot_fig.grid(which = "major", axis = "x", color = "blue", alpha = 0.8,linestyle = "--", linewidth = 1)
        distance_encoder_plot_fig.grid(which = "major", axis = "y", color = "green", alpha = 0.8,linestyle = "--", linewidth = 1)

        distance_step_plot_fig.set_xlim(date_amount*-1+1,0)
        distance_step_plot_fig.set_ylim((dis_step-1.0),(dis_step+1.0))
        distance_step_plot_fig.grid(which = "major", axis = "x", color = "blue", alpha = 0.8,linestyle = "--", linewidth = 1)
        distance_step_plot_fig.grid(which = "major", axis = "y", color = "green", alpha = 0.8,linestyle = "--", linewidth = 1)

        pyplot.pause(update_time/2)
    print("データ表示終了")

def controller():
    global Frag
    global Frag_stop
    global over_rate
    global agree
    global dis_step
    global frag_preparation_load
    global name
    global movespeed
    global speed
    Frag = True
    Frag_stop = False
    encoder_control = threading.Thread(target=encoder_reading)
    encoder_control.setDaemon(True)
    encoder_control.start()
    loadcell_control = threading.Thread(target=loadcell_readig)
    loadcell_control.setDaemon(True)
    loadcell_control.start()
    time.sleep(0.1)
    name = input("名前->")
    speed = float(input("標線間長さ(mm)->"))
    movespeed = (120/0.001/speed - 1.93) / 6400 / 2
    over_rate = float(input("閾値(10N以下) -> "))
    print("試験開始")

    stepping_control = threading.Thread(target=stepping_move)
    stepping_control.setDaemon(True)
    stepping_control.start()
    while True:
        if load >= over_rate:
            time.sleep(0.5)
            if load >= over_rate:
                time.sleep(0.5)
                if load >= over_rate:
                    time.sleep(0.5)
                    if load >= over_rate:
                        time.sleep(0.5)
                        if load >= over_rate:
                            break
        print(str(load) + "N")
        time.sleep(0.05)
    print("計測開始")
    agree = 0
    dis_step = 0
    frag_preparation_load = True
    time.sleep(0.5)
    date_save_control = threading.Thread(target=date_save)
    date_save_control.setDaemon(True)
    date_save_control.start()
    date_save_control = threading.Thread(target=date_show)
    date_save_control.setDaemon(True)
    date_save_control.start()
    while Frag:
        if load <= over_rate/2:#10N超えたらカウント開始
            time.sleep(2)
            if load <= over_rate/2:#10N超えたらカウント開始
                time.sleep(2)
                if load <= over_rate/2:#10N超えたらカウント開始
                    time.sleep(2)
                    #print("a")
                    if load <= over_rate/2:#10N超えたらカウント開始
                        time.sleep(2)
                        if load <= over_rate/2:#10N超えたらカウント開始
                            time.sleep(2)
                            if load <= over_rate/2:#10N超えたらカウント開始
                                time.sleep(2)
                                if load <= over_rate/2:#10N超えたらカウント開始
                                    time.sleep(2)
                                    Frag = False
                                    Frag_stop = True
                                    print("試験終了\n stopを入力してください")
        time.sleep(0.5)
    while Frag_stop:
        time.sleep(1)


controller()
