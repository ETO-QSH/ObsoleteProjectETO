
#import PyUserInput
from tkinter import *
from datetime import datetime
from tkinter.messagebox import *

#mouse = PyUserInput.Mouse()
#keyboard = PyUserInput.Keyboard()

class TestTime(object):
    def __init__(self, master=None):
        self.root = master
        self.root.geometry('1600x900')
        self.root.resizable(width=False, height=False)
        self.label_a = Label(self.root, text='当前本地时间为：\t\t', bg='#add123', font=("萝莉体", 30, "bold"), fg='pink')
        self.label_a.pack()
        self.label_b = Label(self.root, text="", bg='#add123', font=("萝莉体", 30, "bold"), fg='pink')
        self.label_b.pack()
        self.label_c = Label(self.root, text='\n距离中午吃饭还有：\t\t', bg='#add123', font=("萝莉体", 30, "bold"), fg='pink')
        self.label_c.pack()
        self.label_d = Label(self.root, text="", bg='#add123', font=("萝莉体", 30, "bold"), fg='pink')
        self.label_d.pack()
        self.label_e = Label(self.root, text='\n距离今天下班还有：\t\t', bg='#add123', font=("萝莉体", 30, "bold"), fg='pink')
        self.label_e.pack()
        self.label_f = Label(self.root, text="", bg='#add123', font=("萝莉体", 30, "bold"), fg='pink')
        self.label_f.pack()
        self.update_time()

    def update_time(self):
        self.update_a()
        self.update_b()
        self.update_c()

    def update_a(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.label_b.configure(text=now)
        self.root.after(1000, self.update_a)

    def update_b(self):
        a = '2023-07-14' + ' 12:00:00'
        new_time = datetime.strptime(a, "%Y-%m-%d %H:%M:%S")
        t = new_time - datetime.strptime(str(datetime.now()).split('.')[0], "%Y-%m-%d %H:%M:%S")
        self.label_d.configure(text=t)
        self.root.after(1000, self.update_b)

    def update_c(self):
        a = '2023-07-14' + ' 12:00:00'
        new_time = datetime.strptime(a, "%Y-%m-%d %H:%M:%S")
        t = (new_time - datetime.now()).seconds
        self.label_f.configure(text=t)
        self.root.after(1000, self.update_c)

def close_window(event):
    event.widget.destroy()

#def simulate_input(event):
#    if event.type == '2':
#        mouse.press(event.x, event.y, event.button)
#    elif event.type == '3':
#        mouse.release(event.x, event.y, event.button)
#    elif event.type == '4':
#        mouse.wheel(event.delta)
#    if event.type == '9':
#        keyboard.press_key(event.keycode)
#    elif event.type == '10':
#        keyboard.release_key(event.keycode)

if __name__ == '__main__':
    root = Tk()
    root.title('计时小界面')
    root.wm_attributes('-topmost', 1)
    root.config(bg='#add123')
    root.wm_attributes('-transparentcolor', '#add123')
    TestTime(root)
    root.overrideredirect(True)
    root.bind("<Escape>", close_window)
#    root.bind_all('<Button>', simulate_input)
#    root.bind_all('<Key>', simulate_input)
    root.mainloop()
