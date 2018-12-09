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
        self.rect = Rectangle(pos = pos, size = (2*self.r, 2*self.r), texture=Image("assets/" + self.type + "_" + self.state + str(self.frame) + ".png").texture)
        if(self.type == "leader"):
            self.rect.size = (3*self.r,3*self.r)
        self.size_anim = None
        self.color_anim = None

        self.add(self.rect)
        self.speed = 8
        self.time = 0
        self.delay = delay
        self.started = False

    def get_enemy_pos_from_lane(self,idx):
        return (Window.width, idx * Window.height/8)

    def change_state(self,state):
        self.state = state
        self.frame = 0

    def on_update(self, dt):
        cur_pos = self.rect.pos

        if(self.started is False and self.time > self.delay):
            self.started = True
            self.time = 0
        if(self.started is True):
            if(self.time > self.frames[self.state][1]):
                self.rect.texture = Image("assets/" + self.type + "_" + self.state + str(self.frame) + ".png").texture
                self.frame += 1
                if(self.frame > self.frames[self.state][0] - 1):
                    self.frame = 0
                    if(self.state == "attack"):
                        self.state = "idle"
                self.time = 0

            self.rect.pos = (cur_pos[0] - self.speed, cur_pos[1])
            if(self.size_anim is not None):
                size = self.size_anim.eval(self.time)
                color = self.color_anim.eval(self.time)

                self.color.a = color
                self.rect.size = (size,size)

                if(self.size_anim.is_active(self.time) is False):
                    self.speed = 0
        self.time += dt

    def on_damage(self, damage):
        self.hp -= damage
        if(self.hp <= 0):
            self.on_kill()

    def on_kill(self):
        self.size_anim = KFAnim((0,2*self.r),(.8,5*self.r))
        self.color_anim = KFAnim((0,0.8),(.3,1), (.5,0))
        self.time = 0
        # play death animation