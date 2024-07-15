from tkinter import *  # 引入模块

root = Tk()  # 创建Tk控件
root.geometry('960x480+200+100')  # 设置窗口大小及位置
root.title('透明按钮')  # 设置窗口标题

canvas = Canvas(root, highlightthickness=0)  # 创建Canvas控件，并设置边框厚度为0
canvas.place(width=960, height=480)  # 设置Canvas控件大小及位置
# 【这里记得要改成对应的路径】
bg = PhotoImage(file='./images/01fb50f74e054643a94561ca29aa7a40.png')

canvas.create_image(480, 240, image=bg)  # 添加背景图片
r1 = canvas.create_rectangle(380, 350, 580, 400, width=2, outline='black')  # 按钮外框
r2 = canvas.create_rectangle(380+3, 350+3, 580-3, 400-3, width=2, outline='black')  # 按钮内框
t = canvas.create_text(480, 375, text='点 我', font=('楷体', 20, 'bold'), fill='black')  # 按钮显示文本

canvas.bind('<Button-1>', lambda event: bind_1(event))  # 关联鼠标点击事件
canvas.bind('<Motion>', lambda event: bind_2(event))  # 关联鼠标经过事件


def bind_1(event):  # 点击响应函数
    if 380 <= event.x <= 580 and 350 <= event.y <= 400:  # 响应的位置
        print('Hello Python!')  # 打印


def bind_2(event):  # 鼠标经过响应函数
    if 380 <= event.x <= 580 and 350 <= event.y <= 400:  # 响应的位置
        canvas.itemconfigure(r1, outline='white')  # 重设外框颜色
        canvas.itemconfigure(r2, outline='white')  # 重设内框颜色
        canvas.itemconfigure(t, fill='white')  # 重设显示文本颜色
    else:
        canvas.itemconfigure(r1, outline='black')  # 恢复外框默认颜色
        canvas.itemconfigure(r2, outline='black')  # 恢复内框默认颜色
        canvas.itemconfigure(t, fill='black')  # 恢复显示文本默认颜色


root.mainloop()  # 窗口进入消息事件循环
