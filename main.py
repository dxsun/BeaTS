import sys
import rtmidi_python as rtmidi

sys.path.append('..')

from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.note import *

from kivy.core.image import Image
from common.gfxutil import *

from common.synth import *
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

def hp_label() :
    l = Label(text = "HP: 0", halign = 'right',valign='top', font_size='20sp',
              pos=(Window.width/2.5, Window.height * 0.43),
              text_size=(Window.width, Window.height))
    return l
def score_label() :
    l = Label(text = "Score: 0", halign = 'left',valign='top', font_size='20sp',
              pos=(Window.width/2, Window.height * 0.43),
              text_size=(Window.width, Window.height))
    return l

class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()

        self.MIDI_ENABLED = False 

        self.audio = Audio(2)
        self.synth = Synth("data/FluidR3_GM.sf2")
        self.audio.set_generator(self.synth)

        self.channel = 1
        self.synth.program(self.channel, 0, 0)

        if(self.MIDI_ENABLED is True):
            self.midi_in = rtmidi.MidiIn(b'in')
            self.midi_in.open_port(0)

        self.notes_down = [] # an array that keeps track of all notes that are currently being played on midi keyboard


        self.objects = AnimGroup()
        self.canvas.add(self.objects)

        # The particle effect
        self.ps = ParticleSystem('particle/particle.pex')
        self.ps.emitter_x = Window.width/10
        self.ps.emitter_y = Window.height/5
        self.add_widget(self.ps)

        # The display for the gems, now bar, and bar lines
        self.canvas.add(Color(1,1,1))
        rect = Rectangle(pos=(0,0), size=(Window.width, Window.height))

        self.canvas.add(rect)
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
        self.enemy_manager.spawn_enemy(5,"leader")
        self.enemy_manager.spawn_enemy(2,"minion")


    def generate_note(self, note):
        self.synth.noteon(self.channel, note, 60)
                
    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        button_idx = lookup(keycode[1], '12345678', (0,1,2,3,4,5,6,7))
        if button_idx != None:
            self.generate_note(60+button_idx)

    def on_key_up(self, keycode):
        button_idx = lookup(keycode[1], '12345678', (0,1,2,3,4,5,6,7))
        if button_idx != None:
            self.enemy_manager.kill_lane(button_idx)
            self.player.change_lane(button_idx)
            self.synth.noteoff(self.channel, 60+button_idx)

    def on_update(self) :
        self.lane_manager.on_update()
        self.player.on_update()
        self.enemy_manager.on_update()
        self.audio.on_update()


        if(self.MIDI_ENABLED is True):
            message, delta_time = self.midi_in.get_message()
            if (message):
                if (message[0] == 144): # keydown message, add note to notes_down
                    if (message[1] not in self.notes_down):
                        self.notes_down.append(message[1])
                else: #keyup, remove note from notes_down
                    self.synth.noteoff(self.channel, message[1])# stop playing the note if the key is up
                    self.notes_down.remove(message[1])
            # self.notes_down contains the notes that are currently being played
                print(self.notes_down)

                for note in self.notes_down:
                    self.generate_note(note)
            
        for key in chord_dict:
            value = chord_dict[key]
            if (is_chord(self.notes_down, value)):
                lane_number = chord_to_lane[key]
                self.enemy_manager.kill_lane(lane_number)
                self.player.change_lane(lane_number)

        # for chord_key in chord_dict:
        #     if (is_chord(self.notes_down, chord)):
        #         print(chord)

chord_dict = {
    'c_low' : [48, 52, 55],
    'd_low' : [50, 53, 57],
    'e_low' : [55, 59, 52],
    'f_low' : [53, 60, 57],
    'g_low' : [59, 62, 55],
    'a_low' : [60, 64, 57],
    'b_low' : [62, 65, 59],
    'c_high' : [64, 67, 60]
}

chord_to_lane = {
    'c_low' : 0,
    'd_low' : 1,
    'e_low' : 2,
    'f_low' : 3,
    'g_low' : 4,
    'a_low' : 5,
    'b_low' : 6,
    'c_high' : 7
}

def is_chord(array_of_notes_down, notes_desired):
    sorted_notes_down = sorted(array_of_notes_down)
    sorted_notes_desired = sorted(notes_desired)

    return sorted_notes_down == sorted_notes_desired

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
        hue = np.interp(self.get_lane_position(idx), (0,Window.height), (0, 0.5))
        c = Color(hsv=(0,0,0))
        c.a = 1
        #self.add(c)
        rect = Rectangle(pos=(0, self.get_lane_position(idx)), size=(Window.width, Window.height/8), texture=Image('assets/grass.png').texture)
        #rect = Rectangle(pos=(0, self.get_lane_position(idx)), size=(Window.width, Window.height/8))
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


    def spawn_enemy(self,idx,enemy_type):
        enemy = Enemy(idx,enemy_type)
        self.add(enemy)
        self.enemies.append(enemy)

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
        for dead_enemy in dead:
            self.enemies.remove(dead_enemy)

class Enemy(InstructionGroup):
    def __init__(self, idx, enemy_type):
        super(Enemy, self).__init__()
        self.hp = 100
        self.state = "idle"
        self.frames = {"idle":["idle.png","idle2.png"]}
        self.frame = 0
        self.lane = idx
        self.r = Window.height/16
        self.color = Color(1,1,1)
        self.add(self.color)
        segments = 40
        pos = self.get_enemy_pos_from_lane(idx)

        self.type = enemy_type 
        self.rect = Rectangle(pos = pos, size = (2*self.r, 2*self.r), texture=Image("assets/" + self.type + "_"+'idle.png').texture)
        if(self.type == "leader"):
            self.rect.size = (3*self.r,3*self.r)
        self.size_anim = None
        self.color_anim = None

        self.add(self.rect)
        self.speed = 2
        self.time = 0

    def get_enemy_pos_from_lane(self,idx):
        return (Window.width * 0.9, idx * Window.height/8)

    def on_update(self, dt):
        cur_pos = self.rect.pos
        if(self.time > 1):
            print(self.type + "_"+self.frames[self.state][self.frame])
            self.rect.texture = Image("assets/" + self.type + "_"+self.frames[self.state][self.frame]).texture
            self.frame += 1 
            if(self.frame > len(self.frames[self.state]) - 1):
                self.frame = 0
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

class Hero(InstructionGroup):
    def __init__(self, pos):
        super(Hero, self).__init__()
        self.origin = pos
        self.r = Window.height/16
        segments = 40
        self.frames = {"idle":["hero.png","hero2.png"]}
        self.frame = 0
        self.state = "idle"

        #animations on the gems
        self.size_anim = None
        self.color_anim = None
        self.time = 0
        # Create the shape itself
        self.color = Color(1,1,1)
        self.time = 0
        self.add(self.color)
        self.rect = Rectangle(pos = pos, size = (3*self.r, 3*self.r),texture=Image('assets/hero.png').texture)
        self.add(self.rect)
    def change_lane(self,lane):
        self.rect.pos = (Window.width/10,(lane * Window.height/8))

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self, dt):
        if(self.time > 1):
            self.rect.texture = Image("assets/" + self.frames[self.state][self.frame]).texture
            self.frame += 1 
            if(self.frame > len(self.frames[self.state]) - 1):
                self.frame = 0
            self.time = 0
        self.time += dt 
        
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

    def change_lane(self,lane):
        self.hero.change_lane(lane)

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.score_label.text = "Score: " + str(self.score)
        self.hp_label.text = "HP: " + str(self.hp)
        self.hero.on_update(0.1)

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
