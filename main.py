

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
        rect = Rectangle(pos=(0,Window.height-Window.height/10), size=(Window.width, Window.height/10))
        self.canvas.add(rect)
        self.score_label = score_label()
        self.add_widget(self.score_label)
        self.hp_label = hp_label()
        self.add_widget(self.hp_label)
        
        # Create the player object which will store and control the state of the game 
        self.player = Player(self.hp_label,self.score_label)
        self.canvas.add(self.player)

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

class LaneManager(InstructionGroup):
    def __init__(self):
        super(LaneManager, self).__init__()
        self.lanes = []
        for i in range(8):
            lane = Lane(i)
            self.lanes.append(lane)
    
    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        for lane in self.lanes:
            lane.on_update()

class Lane(InstructionGroup):
    def __init__(self, idx):
        super(Lane, self).__init__()
        self.idx = idx
    
    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        pass
# Handles game logic and keeps score.
# Controls the display and the audio
class Player(InstructionGroup):
    def __init__(self, score_label, hp_label):
        super(Player, self).__init__()
        self.score = 0
        self.hp = 0
        self.state = "idle"
        self.lane = 0
        self.score_label = score_label
        self.hp_label = hp_label

    
    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.score_label.text = "Score: " + str(self.score)
        self.hp_label.text = "HP: " + str(self.hp)
        

run(MainWidget)
