import socket
import math
import threading
import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title('Parking Sensor')
height = window.winfo_screenheight()
width = window.winfo_screenwidth()
mid_font = ('Noto Sans Mono', 10)
colors = ['mediumblue', 'hotpink', 'darkgreen', 'red', 'orange', 'darkcyan']
ind = 0
canvas_height = height // 2
origin_x, origin_y = width//2, canvas_height//6
magnification = 1

canvas = tk.Canvas(window, height=canvas_height, width=width, bg="white")
canvas.pack()
# 绘制坐标轴
canvas.create_line(0, origin_y, width, origin_y, fill="gray", width=1)
canvas.create_line(origin_x, 0, origin_x, height, fill="gray", width=1)
canvas.create_oval(origin_x - 6, origin_y - 6, origin_x + 6, origin_y + 6, fill='black')
canvas.create_text(origin_x, origin_y - 10, text='sensor', font=mid_font, fill='black', anchor='s')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 8080))


def run_as_thread(func):  # 装饰器，让函数运行时另开一个线程
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()

    return wrapper


def plot_point(distance, degree, period):
    # 极坐标转直角坐标
    r = distance * magnification
    rad = math.radians(degree)
    if 0 <= r:
        x = origin_x + r * math.cos(rad)
        y = origin_y + r * math.sin(rad)  # y轴向下取反
        # print(f'x: {x}, y: {y}')
        # 绘制点
        canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=colors[period % 6], tags=("a", f"p{period}", "b"))
        canvas.delete(f"p{period-2}")


@run_as_thread
def receive_data():
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            msg = eval(data.decode())
            print(msg)
            distance = msg.get("distance", 0)  # cm
            degree = msg.get("degree", 90)  # 度数
            period = msg.get("period", 0)  # 周期
            plot_point(distance, degree, period)
        except Exception as e:
            print("数据解析错误:", e)


def plot_axis():
    global magnification
    car_width = entry1.get()
    try:
        car_width = int(car_width)
        assert 0 < car_width
    except Exception:
        messagebox.showerror('car width should be a positive integer', 'car width should be a positive integer')
        return 0
    canvas.delete('a')
    magnification = width / (car_width / 10 + 90 * 2)  # 放大倍率：屏幕宽度/(车身宽度+90cm*2)，单位：像素/厘米
    # 画出车尾
    left_end = int(origin_x - car_width / 20 * magnification)
    right_end = int(origin_x + car_width / 20 * magnification)
    r1, r2, r3 = 30 * magnification, 60 * magnification, 90 * magnification
    canvas.create_line(left_end, origin_y, right_end, origin_y, fill="black", width=3, tags='a')
    canvas.create_line(left_end, origin_y + r1, right_end, origin_y + r1, fill="red", width=3, tags='a')
    canvas.create_line(left_end, origin_y + r2, right_end, origin_y + r2, fill="blue", width=3, tags='a')
    canvas.create_line(left_end, origin_y + r3, right_end, origin_y + r3, fill="green", width=3, tags='a')
    bbox1 = (left_end - r1, origin_y - r1, left_end + r1, origin_y + r1)
    canvas.create_arc(*bbox1, start=180, extent=90, style=tk.ARC, width=2, outline="red", tags='a')
    bbox2 = (left_end - r2, origin_y - r2, left_end + r2, origin_y + r2)
    canvas.create_arc(*bbox2, start=180, extent=90, style=tk.ARC, width=2, outline="blue", tags='a')
    bbox3 = (left_end - r3, origin_y - r3, left_end + r3, origin_y + r3)
    canvas.create_arc(*bbox3, start=180, extent=90, style=tk.ARC, width=2, outline="green", tags='a')
    bbox4 = (right_end - r1, origin_y - r1, right_end + r1, origin_y + r1)
    canvas.create_arc(*bbox4, start=270, extent=90, style=tk.ARC, width=2, outline="red", tags='a')
    bbox5 = (right_end - r2, origin_y - r2, right_end + r2, origin_y + r2)
    canvas.create_arc(*bbox5, start=270, extent=90, style=tk.ARC, width=2, outline="blue", tags='a')
    bbox6 = (right_end - r3, origin_y - r3, right_end + r3, origin_y + r3)
    canvas.create_arc(*bbox6, start=270, extent=90, style=tk.ARC, width=2, outline="green", tags='a')
    canvas.create_text(right_end + r1, origin_y, text='30cm', font=mid_font, fill='black', anchor='s', tags='a')
    canvas.create_text(left_end - r2, origin_y, text='60cm', font=mid_font, fill='black', anchor='s', tags='a')
    canvas.create_text(origin_x, origin_y + r3, text='90cm', font=mid_font, fill='black', anchor='n', tags='a')


def start():
    canvas.delete('a')
    try:
        sock.sendto('start'.encode('utf-8'), (entry2.get(), 8080))
    except Exception as e:
        messagebox.showerror('ip error', f'cannot send data to {entry2.get()}')
        print(e)


def end():
    try:
        sock.sendto('end'.encode('utf-8'), (entry2.get(), 8080))
    except Exception:
        messagebox.showerror('ip error', f'cannot send data to {entry2.get()}')


receive_data()

label1 = tk.Label(window, text='请输入车尾的宽度：', font=mid_font)
label1.pack()
frm1 = tk.Frame(window)
frm1.pack()
entry1 = tk.Entry(frm1, font=mid_font, width=5)
entry1.grid(row=1, column=1)
entry1.insert('end', '1694')
label2 = tk.Label(frm1, text='mm（应为正整数）', font=mid_font)
label2.grid(row=1, column=2)
button1 = tk.Button(frm1, text='确定', font=mid_font, command=plot_axis)
button1.grid(row=1, column=3, padx=20)
plot_axis()
label3 = tk.Label(window, text='请输入倒车雷达的ip地址：', font=mid_font)
label3.pack()
entry2 = tk.Entry(window, font=mid_font, width=15)
entry2.pack()
entry2.insert('end', '192.168.1.')
frm2 = tk.Frame(window)
frm2.pack()
button2 = tk.Button(frm2, text='启动扫描', font=mid_font, command=start)
button2.grid(row=1, column=1, padx=20)
button3 = tk.Button(frm2, text='结束扫描', font=mid_font, command=end)
button3.grid(row=1, column=2, padx=20)


window.mainloop()
