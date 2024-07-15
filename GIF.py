import pgzrun
TITLE = "ETO"
WIDTH = 500
HEIGHT = 500
frame = 0
gif = False
cookie1 = Actor(r"C:\PY\我的项目\images\relax (1)")
cookie2 = Actor(r"C:\PY\我的项目\images\relax (2)")
cookie3 = Actor(r"C:\PY\我的项目\images\relax (3)")
cookie4 = Actor(r"C:\PY\我的项目\images\relax (4)")
cookie5 = Actor(r"C:\PY\我的项目\images\relax (5)")
cookie6 = Actor(r"C:\PY\我的项目\images\relax (6)")
cookie7 = Actor(r"C:\PY\我的项目\images\relax (7)")
cookie8 = Actor(r"C:\PY\我的项目\images\relax (8)")
cookie9 = Actor(r"C:\PY\我的项目\images\relax (9)")
cookies = [cookie1, 
           cookie2, 
           cookie3, 
           cookie4, 
           cookie5, 
           cookie6, 
           cookie7, 
           cookie8, 
           cookie9]
def update():
    global frame
    if frame < 8:
        frame += 1
    else:
        frame = 0
    screen.clear()
    cookie = cookies[frame]
    cookie.x = 250
    cookie.y = 150
    cookie.draw()
    if gif == False:
        clock.schedule_unique(update, 0.167)
pgzrun.go()
