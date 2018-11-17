

import sys
sys.path.append('..')

from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.note import *
from common.gfxutil import *
import time


from kivy.core.text import Label as CoreLabel
from common.kivyparticle import ParticleSystem
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock

import random
import numpy as np
import bisect

def score_label() :
    l = Label(text = "Score: 0", halign = 'right',valign='top', font_size='20sp',
              pos=(Window.width/2.5, Window.height * 0.43),
              text_size=(Window.width, Window.height))
    return l
def hp_label() :
    l = Label(text = "HP: 0", halign = 'left',valign='top', font_size='20sp',
              pos=(Window.width/2, Window.height * 0.43),
              text_size=(Window.width, Window.height))
    return l

class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()
        
          # Create the animations and graphics for this pset 
        self.objects = AnimGroup()
        self.canvas.add(self.objects)

        # The particle effect 
        self.ps = ParticleSystem('particle/particle.pex')
        self.ps.emitter_x = Window.width/10
        self.ps.emitter_y = Window.height/5
        self.add_widget(self.ps)

        # The display for the gems, now bar, and bar lines
        self.canvas.add(Color(1,1,1))
        self.lane_manager = LaneManager()
        self.canvas.add(self.lane_manager)


        # Display the status of the game through the text labels
        self.canvas.add(Color(0,0,0))
        #rect = Rectangle(pos=(0,Window.height-Window.height/10), size=(Window.width, Window.height/10))
        #self.canvas.add(rect)
        self.score_label = score_label()
        self.add_widget(self.score_label)
        self.hp_label = hp_label()
        self.add_widget(self.hp_label)
        
        # Create the player object which will store and control the state of the game 
        self.player = Player(self.hp_label,self.score_label)
        self.canvas.add(self.player)

        self.enemy_manager = EnemyManager() 
        self.canvas.add(self.enemy_manager)
        self.enemy_manager.spawn_enemy(5)
        self.enemy_manager.spawn_enemy(2)

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        pass

    def on_key_up(self, keycode):
        # button up
        # only play game if the game is not paused
        pass

    def on_update(self) :
        self.lane_manager.on_update()
        self.player.on_update()
        self.enemy_manager.on_update()

class LaneManager(InstructionGroup):
    def __init__(self):
        super(LaneManager, self).__init__()
        self.lanes = []
        for i in range(8):
            lane = Lane(i)
            self.add(lane)
            self.lanes.append(lane)
    
    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        for lane in self.lanes:
            lane.on_update()

class Lane(InstructionGroup):
    def __init__(self, idx):
        super(Lane, self).__init__()
        self.idx = idx
        hue = np.interp(self.get_lane_position(idx), (0,Window.height), (0, 1))
        c = Color(hsv=(hue,1,1))
        c.a = 0.5
        self.add(c)
        rect = Rectangle(pos=(0, self.get_lane_position(idx)), size=(Window.width, Window.height/8))
        self.add(rect)
    # return the location of the lane x position 
    def get_lane_position(self,lane):
        return lane * Window.height/8

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        pass
class EnemyManager(InstructionGroup):
    def __init__(self):
        super(EnemyManager, self).__init__()
        self.enemies = []


    def spawn_enemy(self,idx):
        enemy = Enemy(idx)
        self.add(enemy)
        self.enemies.append(enemy)

    def on_update(self):
        dead = []
        for enemy in self.enemies:
            if(enemy.speed == 0): 
                dead.append(enemy)
            else:
                enemy.on_update()
        for dead_enemy in dead:
            self.enemies.remove(dead_enemy)

class Enemy(InstructionGroup):
    def __init__(self, idx):
        super(Enemy, self).__init__()
        self.hp = 100
        self.state = "idle"
        self.lane = 0
        self.r = Window.height/16
        segments = 40
        pos = self.get_enemy_pos_from_lane(idx)
        self.circle = CEllipse(cpos = pos, csize = (2*self.r, 2*self.r), segments = segments) 
        self.add(self.circle)
        self.speed = 2

    def get_enemy_pos_from_lane(self,idx):
        return (Window.width * 0.9, idx * Window.height/8 + self.r)

    def on_update(self):
        cur_pos = self.circle.pos
        self.circle.pos = (cur_pos[0] - self.speed, cur_pos[1])
        
    def on_damage(self, damage):
        self.hp -= damage
        if(damage <= 0):
            self.on_kill()

    def on_kill(self):
        self.speed = 0
        # play death animation
    
class Hero(InstructionGroup):
    def __init__(self, pos):
        super(Hero, self).__init__()
        self.origin = pos 
        self.r = Window.height/16
        segments = 40

        #animations on the gems 
        self.size_anim = None
        self.color_anim = None
        self.time = 0 
        # Create the shape itself 
        self.circle = CEllipse(cpos = pos, csize = (2*self.r, 2*self.r), segments = segments) 
        self.add(self.circle)
    def change_lane(self,lane):
        self.circle.pos = (Window.width/10,(lane * Window.height/8))
   
    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        pass
# Handles game logic and keeps score.
# Controls the display and the audio
class Player(InstructionGroup):
    def __init__(self, score_label, hp_label):
        super(Player, self).__init__()
        self.MAX_HEALTH = 100
        self.score = 0
        self.hp = self.MAX_HEALTH
        self.state = "idle"
        self.lane = 0
        self.score_label = score_label
        self.hp_label = hp_label
        self.hero = Hero((0,0))
        self.hero.change_lane(1)
        self.add(self.hero) 
    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.score_label.text = "Score: " + str(self.score)
        self.hp_label.text = "HP: " + str(self.hp)

    def update_health(self,amt):
        self.hp = amt
        if(self.hp > self.MAX_HEALTH):
            self.hp = self.MAX_HEALTH
        if(self.hp <= 0):
            self.hp = 0
            self.on_kill()

    def on_kill(self):
        pass 
        

run(MainWidget)
