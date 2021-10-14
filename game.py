from tkinter import *
import math
import random
# from tkSnack import *
root = Tk()
root.geometry("1920x1080")
root.title("Brick Breaker")
root.attributes("-fullscreen", True)
root.bind("<Escape>",exit)

# tkSnack.initializeSnack(root)
# snd = tkSnack.Sound()
# snd.read('b.mp3')

   
#################################################################           
class Ball:
    vx=None
    vy=None 
    def __init__(self, x,y,canvas):
        self.x=x 
        self.y=y
        self.shape=canvas.create_oval(x,y,x+50,y+50, width=0, fill='blue',outline='blue')
        self.canvas=canvas

    def mov(self):
        self.x+=self.vx
        self.y+=self.vy 
        self.canvas.move(self.shape,self.vx,self.vy)

    def destroy(self):
        self.canvas.delete(self.shape)
        
class Brick:
    h=120
    #120 for full height
    w=230
    #230 for full width
    def __init__(self,x,y,canvas,hp):
        self.x=x 
        self.y=y
        self.hp=hp
        self.canvas=canvas
        self.state=0
        self.shape=canvas.create_rectangle(x,y,x+self.w,y+self.h)
        self.fill=255
        self.percentfill = 255/hp
        self.canvas.itemconfig(self.shape,fill="#11{:02x}a0".format(128+math.floor(self.fill/2)))
        self.label=canvas.create_text(x+self.w/2,y+self.h/2,text="{0}".format(hp),fill="Black",font="Times 20 normal bold")
        
    def hit(self,hp):
        self.hp-=hp
        self.canvas.itemconfig(self.label, text="{0}".format(self.hp))
        self.fill-=self.percentfill
        self.canvas.itemconfig(self.shape,fill="#11{:02x}a0".format(128+math.floor(self.fill/2)))
        # snd.play(blocking=1)
        if(self.hp<=0):
            self.canvas.delete(self.shape)
            self.canvas.delete(self.label)
            return True
        return False

    def mov(self):
        if(self.state==8):
            return True
        self.y+=120
        self.canvas.move(self.shape,0,120)
        self.canvas.move(self.label,0,120)
        self.state+=1
        return False

    def destroy(self):
        self.canvas.delete(self.shape)
        self.canvas.delete(self.label)
     
class Game:
    def __init__(self): #coordinates, shapes
        try:
            f=open("hs.sav","r")
            self.highscore=int(f.readline())
            f.close()
        except Exception:
            self.highscore=0
        self.failure = 0
        self.canvas = Canvas(root)
        self.ball= Ball(935,1000,self.canvas)
        self.bricks = []
        self.level=0
        self.ground_hits=0
        self.canvas.pack(expand=YES, fill=BOTH)
        self.tik=False
        self.failed=False
        wall_l =self.canvas.create_rectangle(0,0,30,1080     ,fill="#fb0")
        wall_r =self.canvas.create_rectangle(1890,0,1920,1080,fill="#fb0")
        # roof   =self.canvas.create_rectangle(30,0,1890,30   ,fill="#fb0")
        ground =self.canvas.create_rectangle(30,1050,1890,1080,fill="red")
        self.failure = self.canvas.create_text(800,600,text=" ",fill="Black",font="Times 20 normal bold")
        self.hs = self.canvas.create_text(800,650,text=" ",fill="Black",font="Times 20 normal bold")
        self.canvas.bind("<Button-1>",self.start)
        root.bind("r",self.reset)
        self.create_next_round()

    def reset(self,event):
        self.failed = False
        self.pause()
        self.canvas.itemconfig(self.failure ,text=" ")
        self.canvas.itemconfig(self.hs,text=" ")
        for brick in self.bricks:
            brick.destroy()
        self.bricks = []
        self.ball.destroy()
        self.ball = Ball(935,1000,self.canvas)
        self.level=0
        self.ground_hits=0
        self.create_next_round()

    def create_next_round(self):
        for brick in self.bricks:
            if(brick.mov()):
                self.fail()
                return
        self.level+=1
        count = random.randint(2,4)
        off = 0
        deoff=6-count

        for x in range(count):
            pos = random.randint(off,deoff)
            self.bricks.append(Brick(270+pos*230,0,self.canvas,self.level))
            off = pos + 1
            deoff+=1

    def start(self,event):
        if(self.tik or self.failed):
            return
        self.tik=True
        x=event.x-(self.ball.x+25)
        y=event.y-(self.ball.y+25)
        v=3

        r=math.sqrt(x*x+y*y)
        self.ball.vx=x*v/r
        self.ball.vy=y*v/r 
        self.update()

    def pause(self):
        self.canvas.after_cancel(self.after)
        self.tik=False
        self.create_next_round()

    def update(self):
        self.ball.mov()
        self.touch()
        if(self.tik):
            self.after = self.canvas.after(6,self.update)

    def fail(self):
        if(self.level>self.highscore):
            self.highscore=self.level
            f = open("hs.sav","w")
            f.write("{0}".format(self.level))
            f.close()
        self.failed=True
        self.canvas.itemconfig(self.failure ,text="Score:{0}".format(self.level))
        self.canvas.itemconfig(self.hs,text="Highest Record:{0}".format(self.highscore))

    def touch(self):  
        for brick in self.bricks:    
            self.touchBrick(brick)
        if(self.ball.x + 50>=1890):
            self.ball.vx *= -1
        if(self.ball.y<=0):
            self.ball.vy *= -1
        if(self.ball.x<=30):
            self.ball.vx *= -1
        if(self.ball.y+50>=1050):
            if(self.ground_hits<2):
                self.ground_hits+=1
                self.ball.vy *= -1
            else:
                self.ground_hits=0
                self.pause()
    
    def cm(self,x,y):
        ax=x-self.ball.x-25
        ay=y-self.ball.y-25
        v=3

        r=math.sqrt(ax*ax+ay*ay)
        self.ball.vx=-ax*v/r
        self.ball.vy=-ay*v/r 

    def cc(self,x,y):
        return math.sqrt(math.pow(x-(self.ball.x+25),2)+math.pow(y-(self.ball.y+25),2))<=25

    def touchBrick(self,brick):
        if((self.ball.y+50 < brick.y or self.ball.y > brick.y+brick.h) or 
           (self.ball.x+50 < brick.x or self.ball.x > brick.x+brick.w) ):
            return

        if((self.ball.y + 50 >= brick.y or self.ball.y <= brick.y + brick.h)
         and self.ball.x + 25 > brick.x and self.ball.x + 25 < brick.x + brick.w):
            self.ball.vy *= -1
            if(brick.hit(self.level/2)):
                self.bricks.remove(brick)
        elif((self.ball.x + 50 >= brick.x or self.ball.x <= brick.x + brick.w)
         and self.ball.y + 25 > brick.y and self.ball.y + 25 < brick.y + brick.h):
            self.ball.vx *= -1  
            if(brick.hit(self.level/2)):
                self.bricks.remove(brick)
        elif(   self.cc(brick.x , brick.y)):
            self.cm(brick.x , brick.y)
            if(brick.hit(self.level/2)):
                self.bricks.remove(brick)
        elif( self.cc(brick.x + brick.w , brick.y)):
            self.cm(brick.x + brick.w , brick.y)
            if(brick.hit(self.level/2)):
                self.bricks.remove(brick)
        elif( self.cc(brick.x , brick.y + brick.h)):
            self.cm(brick.x , brick.y + brick.h)
            if(brick.hit(self.level/2)):
                self.bricks.remove(brick)
        elif( self.cc(brick.x + brick.w , brick.y + brick.h)):
            self.cm(brick.x + brick.w , brick.y + brick.h)
            if(brick.hit(self.level/2)):
                self.bricks.remove(brick)

################################################
game = Game()
root.mainloop()  