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
from read_data import read_data
from Chord import Chord
from mappings import chord_dict, chord_to_lane, lane_to_chord, lane_to_midi

from kivy.core.text import Label as CoreLabel
from common.kivyparticle import ParticleSystem
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock

import random
import numpy as np
import bisect

interval_to_semitones = Chord.interval_to_semitones

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

        self.audio_controller = AudioController()
        self.audio_controller.toggle()

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
        rect = Rectangle(pos=(0,0), size=(Window.width, Window.height), texture=Image('assets/grassybg.png').texture)

        self.canvas.add(rect)
        self.lane_manager = LaneManager()
        #self.canvas.add(self.lane_manager)

        # Display the status of the game through the text labels
        self.canvas.add(Color(0,0,0))
        #rect = Rectangle(pos=(0,Window.height-Window.height/10), size=(Window.width, Window.height/10))
        #self.canvas.add(rect)
        self.score_label = score_label()
        self.add_widget(self.score_label)
        self.hp_label = hp_label()
        self.add_widget(self.hp_label)

        self.enemy_manager = EnemyManager()
        self.canvas.add(self.enemy_manager)
        # self.enemy_manager.spawn_enemy(5,"leader",0)
        # self.enemy_manager.spawn_enemy(5,"minion1",15)
        # self.enemy_manager.spawn_enemy(5,"minion2",30)
        # self.enemy_manager.spawn_enemy(2,"minion3",8)
        # self.enemy_manager.spawn_enemy(1,"minion4",12)
        # self.enemy_manager.spawn_enemy(4,"minion5",18)

        self.enemy_times = []
        self.enemy_lanes = []
        self.enemy_types = []

        read_data("songs/WIWYM_left_hand.txt", "songs/WIWYM_right_hand.txt", self.enemy_times, self.enemy_lanes, self.enemy_types)

        self.prev_time = time.time()
        self.elapsed_time = 0
        self.note_index = 0

        window_size = 4 # 4 seconds of notes are displayed
        x_scale = Window.width / window_size # pixels / sec

        # Create the player object which will store and control the state of the game
        self.player = Player(self.hp_label,self.score_label, self.enemy_times, self.enemy_lanes, self.enemy_types, self.enemy_manager)
        self.canvas.add(self.player)
        self.player.toggle()

        self.enemy_manager = EnemyManager()
        self.canvas.add(self.enemy_manager)

    def generate_note(self, note):
        self.audio_controller.generate_note(note)

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        if keycode[1] == 'p':
            self.audio_controller.toggle()
            self.player.toggle()

        else:
            button_idx = lookup(keycode[1], '12345678', (0,1,2,3,4,5,6,7))
            if button_idx != None:
                # self.audio_controller.generate_note(lane_to_midi[button_idx])

                chord = chord_dict[lane_to_chord[button_idx]]
                print("chord: ", chord)

                self.notes_down.extend(chord)
                for note in self.notes_down:
                    self.audio_controller.generate_note(note)

                self.player.on_notes_played()

    def on_key_up(self, keycode):
        button_idx = lookup(keycode[1], '12345678', (0,1,2,3,4,5,6,7))

        if button_idx != None:

            chord = chord_dict[lane_to_chord[button_idx]]

            for note in chord:
                self.audio_controller.note_off(note) # stop playing the note if the key is up
                self.notes_down.remove(note)

            self.enemy_manager.kill_lane(button_idx)
            self.player.change_lane(button_idx)
            # self.audio_controller.note_off(60+button_idx)
            self.audio_controller.note_off(lane_to_midi[button_idx])

    def on_update(self) :
        self.audio_controller.on_update()

        self.elapsed_time += time.time() - self.prev_time
        self.prev_time = time.time()

        if(self.audio_controller.MIDI_ENABLED is True):
            message, delta_time = self.audio_controller.midi_in.get_message()
            if (message):
                if (message[0] == 144): # keydown message, add note to notes_down
                    if (message[1] not in self.notes_down):
                        self.notes_down.append(message[1])
                        self.player.on_notes_played()
                        self.audio_controller.generate_note(message[1])
                else: #keyup, remove note from notes_down
                    if (message[1] in self.notes_down):
                        self.audio_controller.note_off(message[1]) # stop playing the note if the key is up
                        self.notes_down.remove(message[1])
            # self.notes_down contains the notes that are currently being played

        self.lane_manager.on_update()
        self.player.update_notes(self.notes_down)
        self.player.on_update()
        self.enemy_manager.on_update()

        # for key in chord_dict:
        #     value = chord_dict[key]
        #     if (is_chord(self.notes_down, value)):
        #         lane_number = chord_to_lane[key]
        #         self.enemy_manager.kill_first_enemy_in_lane(lane_number)
        #         self.player.change_lane(lane_number)




# creates the Audio driver
# creates a song and loads it with solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
    def __init__(self):
        super(AudioController, self).__init__()

        self.MIDI_ENABLED = True

        self.audio = Audio(2)
        self.synth = Synth("data/FluidR3_GM.sf2")

        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        self.mixer.add(self.synth)

        self.channel = 1
        self.synth.program(self.channel, 0, 0)

        self.bg_wave_file_gen = WaveGenerator(WaveFile("WhenIWasYourMan.wav"))
        self.bg_wave_file_gen.set_gain(0.5)
        self.mixer.add(self.bg_wave_file_gen)

        if(self.MIDI_ENABLED is True):
            self.midi_in = rtmidi.MidiIn(b'in')
            self.midi_in.open_port(0)

    # start / stop the song
    def toggle(self):
        self.bg_wave_file_gen.play_toggle()
    # # mute / unmute the solo track
    # def set_mute(self, mute):
    #     if (mute):
    #         self.solo_wave_file_gen.set_gain(0)
    #     else:
    #         self.solo_wave_file_gen.set_gain(1)

    # play a sound-fx (miss sound)
    # def play_sfx(self):
    #     self.miss_note_gen = WaveGenerator(WaveFile("error.wav"))
    #     self.mixer.add(self.miss_note_gen)

    def generate_note(self, note):
        self.synth.noteon(self.channel, note, 100)

    def note_off(self, note):
        self.synth.noteoff(self.channel, note)

    # needed to update audio
    def on_update(self):
        self.audio.on_update()

def is_chord(array_of_notes_down, notes_desired):
    sorted_notes_down = sorted(array_of_notes_down)
    sorted_notes_desired = sorted(notes_desired)

    return sorted_notes_down == sorted_notes_desired

class LaneManager(InstructionGroup):
    def __init__(self):
        super(LaneManager, self).__init__()
        self.lanes = []
        self.num_lanes = 8
        for i in range(self.num_lanes):
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
        self.speed = 4
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

class Hero(InstructionGroup):
    def __init__(self, pos):
        super(Hero, self).__init__()
        self.origin = pos
        self.r = Window.height/16
        segments = 40
        self.frames = {"idle":(2,1),"attack":(3,0.5)}
        self.frame = 0
        self.type = "hero"
        self.state = "idle"

        #animations on the gems
        self.size_anim = None
        self.color_anim = None
        self.time = 0
        # Create the shape itself
        self.color = Color(1,1,1)
        self.time = 0
        self.add(self.color)
        self.rect = Rectangle(pos = pos, size = (3*self.r, 3*self.r),texture=Image("assets/" + self.type + "_" + self.state + str(self.frame) + ".png").texture)
        self.add(self.rect)

    def change_state(self,state):
        self.state = state
        self.frame = 0

    def change_lane(self,lane):
        self.rect.pos = (Window.width/10,(lane * Window.height/8))
        self.change_state("attack")

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self, dt):
        if(self.time > self.frames[self.state][1]):
            self.rect.texture = Image("assets/" + self.type + "_" + self.state + str(self.frame) + ".png").texture
            self.frame += 1
            if(self.frame > self.frames[self.state][0] - 1):
                self.frame = 0
                if(self.state == "attack"):
                    self.state = "idle"
            self.time = 0
        self.time += dt

# Handles game logic and keeps score.
# Controls the display
class Player(InstructionGroup):
    def __init__(self, score_label, hp_label, gem_times, gem_lanes, enemy_types, enemy_manager):
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

        self.gem_times = gem_times
        self.gem_lanes = gem_lanes
        self.enemy_types = enemy_types

        self.elapsed_time = 0
        self.prev_time = time.time()
        self.playing = True

        self.enemy_manager = enemy_manager
        self.current_enemy_index = 0
        self.enemy_spawn_index = 0

        self.notes_down = []

    def update_notes(self, notes):
        self.notes_down = notes

    def on_notes_played(self):
        # called when a chord is played by MainWidget.
        # Checks all of the gems nearby and hits enemies in the chord lane that
        # are close enough to the now bar. Also changes the lane of the hero.

        temp_gem_index = self.current_enemy_index

        # iterates through all gems that are within 0.1 of the current chord
        while(temp_gem_index != len(self.gem_times) and self.gem_times[temp_gem_index] <= self.elapsed_time + 0.4):

            enemy_lane = self.gem_lanes[temp_gem_index]
            enemy_type = self.enemy_types[temp_gem_index]

            desired_chord_name = lane_to_chord[enemy_lane]
            chord_list = chord_dict[desired_chord_name]

            hit_all_notes = True
            for note in chord_list:
                if note not in self.notes_down:
                    hit_all_notes = False

            if hit_all_notes:
                # change lanes bc you played a chord
                self.change_lane(enemy_lane)

            if (enemy_type == "leader"):
                # yay you hit all the notes in the chord, now we can kill the enemy!
                # self.notes_down needs to contain the chord (LEFT HAND OCTAVE) in the correct lane
                if (hit_all_notes):
                    self.enemy_manager.kill_enemy_at_index(temp_gem_index)
                    time_difference = self.elapsed_time - self.gem_times[temp_gem_index]
                    self.score += int(300 * (1-time_difference*2))

            else: # This is a single note for the right hand, we need to see if it matches the correct lane
                note_to_match = lane_to_midi[enemy_lane]
                print("note to match:",note_to_match)
                print("notes down:",self.notes_down)
                if (note_to_match in self.notes_down):
                    self.enemy_manager.kill_enemy_at_index(temp_gem_index)
                    time_difference = self.elapsed_time - self.gem_times[temp_gem_index]
                    self.score += int(300 * (1-time_difference*2))

            temp_gem_index += 1

    def change_lane(self,lane):
        self.hero.change_lane(lane)

    def toggle(self):
        self.playing = not self.playing

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.score_label.text = "Score: " + str(self.score)
        self.hp_label.text = "HP: " + str(self.hp)

        if (self.playing):
            self.hero.on_update(0.1)
            self.elapsed_time += time.time() - self.prev_time

            # THIS PART HANDLES ENEMIES AT THE NOW BAR
            # checks all the enemies that are beyond 0.4 seconds of the now bar
            while (self.current_enemy_index < len(self.gem_times) and self.gem_times[self.current_enemy_index] + 0.4 < self.elapsed_time):
                current_enemy = self.enemy_manager.enemies[self.current_enemy_index]

                # this means an enemy has more than 0 HP and is past the now bar by 0.4 seconds
                if (not current_enemy.hp <= 0):
                    self.hp -= 10

                    if (self.hp == 0):
                        print("GAME OVER")

                self.current_enemy_index += 1

            # THIS PART SPAWNS ENEMIES
            if (self.enemy_spawn_index < len(self.gem_times)):
                next_enemy = self.gem_times[self.enemy_spawn_index]
                next_lane = self.gem_lanes[self.enemy_spawn_index]
                if self.elapsed_time > (next_enemy - 5):
                    self.enemy_manager.spawn_enemy(next_lane,self.enemy_types[self.enemy_spawn_index],0)
                    self.enemy_spawn_index += 1
            self.enemy_manager.on_update()
        self.prev_time = time.time()

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
