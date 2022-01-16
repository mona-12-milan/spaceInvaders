from pygame import *
import random
font.init()


wave_length = 5
WIDTH,HEIGHT = 700,700
FPS = 60
PLAYER_VEL = 3

Lost_Count = 0
Lost = False

#Creating Font

main_font = font.SysFont("comicsans",40)

#set the display

WIN = display.set_mode((WIDTH,HEIGHT))
display.set_caption("Space Invaders")

#Loading Images

BLUE_SPACE_SHIP = image.load("pixel_ship_blue_small.png")
GREEN_SPACE_SHIP = image.load("pixel_ship_green_small.png")
RED_SPACE_SHIP = image.load("pixel_ship_red_small.png")
YELLOW_SPACE_SHIP = image.load("pixel_ship_yellow.png")

BLUE_LASER = image.load("pixel_laser_blue.png")
GREEN_LASER = image.load("pixel_laser_green.png")
RED_LASER = image.load("pixel_laser_red.png")
YELLOW_LASER = image.load("pixel_laser_yellow.png")

BACKGROUND_IMAGE = image.load("background-black.png")
BACKGROUND = transform.scale(BACKGROUND_IMAGE,(WIDTH,HEIGHT))

def Collision(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y))!=None

#Laser Class

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y += vel

    def offscreen(self):
        return not(self.y<=HEIGHT and self.y>=0)

    def collison(self,obj):
        return Collision(self,obj)

#Abstract Class

class Ship():

    def __init__(self,x,y,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.Lasers = []
        self.cool_down_count = 0

    def cooldown(self):
        if self.cool_down_count >= 30:
            self.cool_down_count = 0
        elif self.cool_down_count>0:
            self.cool_down_count += 1



    def shoot(self,facing):

        if self.cool_down_count == 0:
            laser = Laser(self.x+int(facing*self.Get_width()//2),self.y,self.laser_img)
            self.Lasers.append(laser)
            self.cool_down_count = 1

    def Get_width(self):
        return self.ship_img.get_width()

    def Get_height(self):
        return self.ship_img.get_height()

    def draw(self,window):
        window.blit(self.ship_img,(self.x,self.y))
        for laser in self.Lasers:
            laser.draw(window)

#player Class

class Player(Ship):

    def __init__(self,x,y,health = 100):
        super().__init__(x,y,health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        #masking for proper pixel collision
        self.mask = mask.from_surface(YELLOW_SPACE_SHIP)

        self.max_health = health
    def move_laser(self,vel,objs):
        self.cooldown()
        for laser in self.Lasers:
            laser.move(vel)
            if laser.offscreen():
                self.Lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collison(obj):
                        self.Lasers.remove(laser)
                        objs.remove(obj)

    def draw(self,window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self,window):
        draw.rect(window,"red",(self.x,self.y+self.Get_height()+10,self.Get_width(),10))
        draw.rect(window, "green", (self.x, self.y + self.Get_height() + 10, self.Get_width()*(1-(self.max_health-self.health)/self.max_health), 10))



#Enemy Ship

class Enemy(Ship):

    Color_Map = {
        "red"     : (RED_SPACE_SHIP,RED_LASER),
        "blue"    : (BLUE_SPACE_SHIP,BLUE_LASER),
        "green"   : (GREEN_SPACE_SHIP,GREEN_LASER)
                }

    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.x = x
        self.y = y
        self.health = health
        self.color = color
        self.ship_img,self.laser_img = self.Color_Map[color]
        self.mask = mask.from_surface(self.ship_img)

    def move(self,vel):
        self.y = self.y+vel

    def move_laser(self,vel,obj):
        self.cooldown()
        for laser in self.Lasers:
            laser.move(vel)
            if laser.offscreen():
                self.Lasers.remove(laser)
            else:
                if laser.collison(obj):
                    self.Lasers.remove(laser)
                    obj.health -=10



def main():

    run = True
    clock = time.Clock()
    Level = 0
    Lives = 5

    Laser_vel = 3



    # creating players and enemies

    player = Player(300, HEIGHT - 120)
    Enemies = []

    wave_length = 5
    enemy_vel = 1

    global Lost
    global Lost_Count


    def redraw_window():
        WIN.blit(BACKGROUND,(0,0))
        #using fonts

        lives_lable = main_font.render("lives : " + str(Lives),1,("white"))
        level_lable = main_font.render("level : " + str(Level),1,("white"))

        WIN.blit(lives_lable,(10,10))
        WIN.blit(level_lable,(WIDTH-level_lable.get_width()-10,10))

        for enemy in Enemies:
            enemy.draw(WIN)

        if Lost:
            Lost_=main_font.render("YOU LOST!!",1,("white"))
            WIN.blit(Lost_,(WIDTH//2 - Lost_.get_width()//2,HEIGHT//2+Lost_.get_height()//2))

        player.draw(WIN)


        display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if player.health<=0:
            Lives -= 1
            player.health = 100

        if Lives<=0:
            Lost = True
            Lost_Count +=1

        if Lost:
            if Lost_Count> FPS*3:
                run = False
            else:
                continue



        if len(Enemies) == 0:
            Level += 1
            wave_length +=5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,WIDTH-50),random.randrange(-2000,-100),random.choice(["red","blue","green"]))
                Enemies.append(enemy)


        for events in event.get():
            if events.type == QUIT:
                run = False

        Keys = key.get_pressed()

        if Keys[K_RIGHT] and player.x < WIDTH-player.Get_width():
            player.x += PLAYER_VEL

        if Keys[K_LEFT] and player.x > 0:
            player.x -=PLAYER_VEL

        if Keys[K_SPACE] :
            player.shoot(0)


        for enemy in Enemies:
            enemy.move_laser(Laser_vel,player)
            if enemy.y>HEIGHT:
                Lives -=1
                Enemies.remove(enemy)
            if random.randrange(0,2*FPS) == 1:
                if enemy.color == "blue":
                    enemy.shoot(-1)
                else:
                    enemy.shoot(-0.45)
            else:
                enemy.move(enemy_vel)

        player.move_laser(-1*Laser_vel,Enemies)

        for enemy in Enemies:
            if Collision(enemy,player):
                player.health -=10
                Enemies.remove(enemy)


def main_menu():
    run = True
    while run:
        WIN.blit(BACKGROUND, (0,0))
        Main_Screen_Font = main_font.render("Click AnyWhere To Continue..",1,"white")
        WIN.blit(Main_Screen_Font,(WIDTH//2-Main_Screen_Font.get_width()//2,HEIGHT//2-Main_Screen_Font.get_height()//2))
        display.update()

        for events in event.get():
            if events.type == QUIT:
                run = False

            if events.type == MOUSEBUTTONDOWN:
                main()


    quit()

if __name__ == "__main__":
    main_menu()
