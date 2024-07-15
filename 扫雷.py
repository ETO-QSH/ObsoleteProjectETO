
import random
from tkinter import *
from PIL import Image, ImageTk

boom = 50
sw = 30*20
sh = 30*20
root = Tk()
first = True
useful = set()
useless = set()
names = locals()
root.title('ETO')
root.resizable(False, False)
bg = ImageTk.PhotoImage(Image.open('.\\images\\bg.png'))
potato = ImageTk.PhotoImage(Image.open('.\\images\\potato.png'))
root.geometry(("%dx%d+%d+%d" % (sw, sh, ((root.winfo_screenwidth()-sw)/2), ((root.winfo_screenheight()-sh)/2))))

def maps(j, k):
    global boom, List
    List = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    for x in range(-1, 2):
        for y in range(-1, 2):
            List[k+x][j+y] = 9
    while boom > 0:
        x = random.randint(0, sw/30-1)
        y = random.randint(0, sh/30-1)
        if List[x][y] == 0:
            List[x][y] = 9
            boom -= 1
    for x in range(-1, 2):
        for y in range(-1, 2):
            List[k+x][j+y] = 0
    for x in range(len(List)):
        for y in range(len(List[x])):
            if List[x][y] >= 9:
                if y != 19:
                    List[x][y+1] += 1
                if x != 19:
                    List[x+1][y] += 1
                if x != 0:
                    List[x-1][y] += 1
                if y != 0:
                    List[x][y-1] += 1
                if ((x != 19 and y != 19)):
                    List[x+1][y+1] += 1
                if ((x != 0 and y != 19)):
                    List[x-1][y+1] += 1
                if ((x != 19 and y != 0)):
                    List[x+1][y-1] += 1
                if ((x != 0 and y != 0)):
                    List[x-1][y-1] += 1
    for x in range(len(List)):
        for y in range(len(List[x])):
            if List[x][y] >= 9:
                List[x][y] = 9
    for x in range(len(List)):
        print("\033[1;37m" + str(List[x]) + "\033[0m")

def ok(j, k):
    global first, useful, useless
    if first == True:
        first = False
        maps(j, k)
    if List[k][j] == 0:
        names['button_%s_%s' % (j, k)] = Button(root, relief='groove', text=str(List[k][j]), overrelief='ridge')
        names['button_%s_%s' % (j, k)].place(width=30, height=30, x=30*j, y=30*k)
        names['button_%s_%s' % (j, k)]['state'] = DISABLED
        useless.add((k, j))
        useful.add((k, j))
    elif List[k][j] == 9:
        names['button_%s_%s' % (j, k)] = Button(root, relief='groove', image=potato, text=str(List[k][j]), overrelief='ridge')
        names['button_%s_%s' % (j, k)].place(width=30, height=30, x=30*j, y=30*k)
        names['button_%s_%s' % (j, k)]['state'] = DISABLED
        print("\033[1;31mB O O M ！！！\033[0m")
    else:
        names['button_%s_%s' % (j, k)] = Button(root, relief='groove', text=str(List[k][j]), overrelief='ridge')
        names['button_%s_%s' % (j, k)].place(width=30, height=30, x=30*j, y=30*k)
        names['button_%s_%s' % (j, k)]['state'] = DISABLED
    while len(useful) > 0:
        use = list(useful)
        useful.clear()
        for o in range(len(use)):
            for p in range(-1, 2):
                for q in range(-1, 2):
                    if (p != 0 or q != 0) and -1 < use[o][0]+p < 20 and -1 < use[o][1]+q < 20 and (use[o][0]+p, use[o][1]+q) not in useless:
                        useful.add((use[o][0]+p, use[o][1]+q))
        useless = useful | useless
        use = list(useful)
        useful.clear()
        for i in range(len(use)):
            if List[use[i][0]][use[i][1]] == 0:
                useful.add(use[i])
    for i in range(len(useless)):
        p = list(useless)[i][0]
        q = list(useless)[i][1]
        if names['button_%s_%s' % (q, p)]['state'] == NORMAL:
            names['button_%s_%s' % (q, p)] = Button(root, relief='groove', text=str(List[p][q]), overrelief='ridge')
            names['button_%s_%s' % (q, p)].place(width=30, height=30, x=30*q, y=30*p)
            names['button_%s_%s' % (q, p)]['state'] = DISABLED

for j in range(0, int(sw / 30)):
    for k in range(0, int(sh / 30)):
        names['button_%s_%s' % (j, k)] = Button(root, relief='groove', overrelief='ridge', image=bg, command=lambda x=j, y=k: ok(x, y))
        names['button_%s_%s' % (j, k)].place(width=30, height=30, x=30*j, y=30*k)
root.mainloop()
