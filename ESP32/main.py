from hcsr04 import HCSR04
import time
import machine
from servo import Servo
import socket
import network
import _thread


def connect_wifi(ssid, password, timeout=5):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        wlan.disconnect()
        time.sleep(1)

    wlan.connect(ssid, password)
    print(f"尝试连接到 {ssid} ...")

    start = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
            print(f"连接 {ssid} 超时")
            wlan.disconnect()
            time.sleep(1)
            return False
        time.sleep(0.3)

    print(f"已连接到 {ssid}，网络配置：{wlan.ifconfig()}")
    return True


# 主网络失败后尝试备用网络
wifi_connected = connect_wifi('CrownYou', '3141592653', timeout=5)
# if not wifi_connected:
#    wifi_connected = connect_wifi('CMCC-G4AH', 'QR7VPSQ5', timeout=5)
if not wifi_connected:
    wifi_connected = connect_wifi('CMCC-2UCK', 'ZNQ7UYCZ', timeout=5)

if wifi_connected:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 8081))
    target_ip = None
    flag = False


    def listen_task():
        global target_ip, flag
        while True:
            msg, addr = sock.recvfrom(1024)
            target_ip = addr[0].strip("'").strip("\"")
            msg = msg.decode('utf-8')
            print(f"收到来自 {target_ip} 的消息：{msg}")
            flag = True if msg == 'start' else False


    _thread.start_new_thread(listen_task, ())

    my_servo = Servo(machine.Pin(16))
    sensor = HCSR04(trigger_pin=22, echo_pin=32)  # 定义超声波模块Tring控制管脚及超声波模块Echo控制管脚
    delay = 0.1
    min = 15
    max = 165


    def send_msg(i, us_dis, period):
        reply = str({'degree': 180 - i, 'distance': us_dis, 'period': period})
        print(reply)
        sock.sendto(reply, (target_ip, 8081))
        time.sleep(delay)


    def do_task(i, period):
        if flag:
            my_servo.write_angle(i)
            time.sleep(delay)
            us_dis = sensor.distance_cm()  # 获取超声波计算距离 ，也可以调用sensor.distance_mm() 得到mm值
            send_msg(i, us_dis, period)


    period = 1
    while True:
        if flag:
            for i in range(min, max, 15):
                do_task(i, period)
            period += 1
            for i in range(max, min, -15):
                do_task(i, period)
            period += 1
