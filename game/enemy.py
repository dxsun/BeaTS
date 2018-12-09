from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.note import *
from common.gfxutil import *
from common.synth import *
from kivy.core.image import Image
from kivy.core.text import Label as CoreLabel
from common.kivyparticle import ParticleSystem
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock

class EnemyManager(InstructionGroup):
    def __init__(self):
        super(EnemyManager, self).__init__()
        self.enemies = []

    def spawn_enemy(self,idx,enemy_type,delay):
        enemy = Enemy(idx,enemy_type,delay)
        self.add(enemy)
        self.enemies.append(enemy)

    def kill_first_enemy_in_lane(self, idx):
        for enemy in self.enemies:
            if(enemy.lane == idx):
                enemy.on_damage(100)
                return

    def kill_enemy_at_index(self, idx):
        if(len(self.enemies) < idx):
            self.enemies[idx].on_damage(100)
        return

    def kill_lane(self,idx):
        for enemy in self.enemies:
            if(enemy.lane == idx):
                enemy.on_damage(100)

    def on_update(self):
        dead = []
        for enemy in self.enemies:
            if(enemy.speed == 0):
                dead.append(enemy)
            else:
                enemy.on_update(0.1)
        # for dead_enemy in dead:
        #     self.enemies.remove(dead_enemy)

class Enemy(InstructionGroup):

    def __init__(self, idx, enemy_type,delay):
        super(Enemy, self).__init__()
        self.hp = 100
        self.state = "idle"
        self.frames = {"idle":(2,1)}
        self.frame = 0
        self.lane = idx
        self.r = Window.height/16
        self.color = Color(1,1,1)
        self.add(self.color)
        segments = 40
        pos = self.get_enemy_pos_from_lane(idx)

        self.type = enemy_type
        ratio = 1.3
        self.inverstion_start = 1

        self.explosion_anim = None

        self.inversion_range = ["1","3","5"]
        self.image_texture = Rectangle(pos = pos, size = (self.r*1.5, self.r*1.5), texture=Image("assets/" + self.type + "_" + self.state + str(self.frame) + ".png").texture)
        self.add(self.image_texture)
        if(self.type == "case"):
            self.image_texture.pos = (self.image_texture.pos[0],self.image_texture.pos[1]/0.97)
            self.image_texture.size = (2*self.r,3*self.r)
            self.enemy_bottom = Rectangle(pos = pos, size = (self.r/ratio, self.r/ratio/1.3), texture=Image("assets/enemy_" + self.inversion_range[self.inverstion_start%len(self.inversion_range)] + "_highlight.png").texture)
            self.enemy_middle = Rectangle(pos = pos, size = (self.r/ratio, self.r/ratio/1.3), texture=Image("assets/enemy_" + self.inversion_range[(self.inverstion_start+1)%len(self.inversion_range)] + "_normal.png").texture)
            self.enemy_top = Rectangle(pos = pos, size = (self.r/ratio, self.r/ratio/1.3), texture=Image("assets/enemy_" + self.inversion_range[(self.inverstion_start+2)%len(self.inversion_range)] + "_normal.png").texture)
            self.add(self.enemy_top)
            self.add(self.enemy_middle)
            self.add(self.enemy_bottom)
            self.enemies = [self.enemy_bottom,self.enemy_middle,self.enemy_top]
        elif(self.type == "blue"):
            self.image_texture.pos = (self.image_texture.pos[0],self.image_texture.pos[1] + self.r/1.1)
        elif(self.type == "red"):
            self.image_texture.size = (self.r*2, self.r*2)
            self.image_texture.pos = (self.image_texture.pos[0],self.image_texture.pos[1] + self.r/2.5)
            
            
        self.size_anim = None
        self.color_anim = None
        self.speed = 8

        self.angry_anim = None
        
        self.explosion_idx = 0
        self.time = 0
        self.delay = delay
        self.is_pass = False
        self.started = False

    def kill_subenemies(self,enemies_kill):
        if(self.type == "case"):
            self.angry_anim = KFAnim((0,0.8),(.3,1), (0.8,0))
            
            for i in range(len(self.enemies)):
                self.make_subenemy_angry(i)
                for idx in enemies_kill:
                    self.enemies[idx].texture = Image("assets/enemy_" + self.inversion_range[self.inverstion_start%len(self.inversion_range)] + "_empty.png").texture

    def make_subenemy_angry(self,idx):
        if(self.type == "case"):
            self.enemies[idx].texture = Image("assets/enemy_" + self.inversion_range[self.inverstion_start%len(self.inversion_range)] + "_angry.png").texture

    def get_enemy_pos_from_lane(self,idx):
        return (Window.width, idx * Window.height/8)

    def change_state(self,state):
        self.state = state
        self.frame = 0

    def on_update(self, dt):
        cur_pos = self.image_texture.pos

        if(self.started is False and self.time > self.delay):
            self.started = True
            self.time = 0
        if(self.started is True):
            if(self.time > self.frames[self.state][1]):
                self.image_texture.texture = Image("assets/" + self.type + "_" + self.state + str(self.frame) + ".png").texture
                self.frame += 1
                if(self.frame > self.frames[self.state][0] - 1):
                    self.frame = 0
                    if(self.state == "attack"):
                        self.state = "idle"
                self.time = 0

            self.image_texture.pos = (cur_pos[0] - self.speed, cur_pos[1])
            if(self.type == "case"):
                self.enemy_bottom.pos = (cur_pos[0] + self.r/1.7, cur_pos[1]+self.r/1.2)
                self.enemy_middle.pos = (cur_pos[0] +self.r/1.7, cur_pos[1]+self.r/0.75)
                self.enemy_top.pos = (cur_pos[0] +self.r/1.7, cur_pos[1]+self.r/0.55)
            if(self.size_anim is not None):
                size_x,size_y = self.size_anim.eval(self.time)
                color = self.color_anim.eval(self.time)

                self.color.a = color
                self.image_texture.size = (size_x,size_y)
                
                if(self.size_anim.is_active(self.time) is False):
                    self.speed = 0
            if(self.angry_anim is not None):
                color = self.angry_anim.eval(self.time)
                self.color.a = color
            if(self.explosion_anim is not None):
                self.angry_anim = None
                if(self.is_pass):
                    self.explosion_anim.texture = Image("assets/explosion0" + str(int(self.explosion_idx/4)) +".png").texture
                else:
                    self.explosion_anim.texture = Image("assets/aura_test_1_32_" + str(int(self.explosion_idx*2)) +".png").texture
                self.explosion_idx += 1
                if(self.explosion_idx > 32):
                    self.explosion_anim = None
        self.time += dt

    def on_damage(self, damage):
        self.hp -= damage
        if(self.hp <= 0):
            self.on_kill()

    def on_kill(self,is_pass = False):
        #self.size_anim = KFAnim((0,2*self.r),(.8,5*self.r))
        self.is_pass = is_pass
        self.explosion_anim = Rectangle(pos = (self.image_texture.pos[0],self.image_texture.pos[1]), size = (self.image_texture.size[0],self.image_texture.size[1]), texture=Image("assets/explosion01.png").texture)
        self.add(self.explosion_anim)
        self.size_anim = KFAnim((0,self.image_texture.size[0],self.image_texture.size[1]),(0.9,self.image_texture.size[0],self.image_texture.size[1]))
        self.color_anim = KFAnim((0,0.8),(.3,1), (0.8,0))
        self.time = 0
        # play death animation