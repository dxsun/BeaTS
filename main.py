import sys
import rtmidi_python as rtmidi
import time

sys.path.append('..')

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

from utils.read_data import read_data
from utils.mappings import chord_dict, chord_to_lane, lane_to_chord, lane_to_midi
from utils.Chord import Chord

from utils.detect_chord import is_chord
from game.audiocontroller import AudioController
from game.lane import LaneManager, Lane
from game.enemy import EnemyManager, Enemy
from game.hero import Hero
from game.player import Player

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
              pos=(Window.width/1.8, Window.height * 0.43),
              text_size=(Window.width, Window.height))
    return l

class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()

        self.state = "menu"

        self.audio_controller = AudioController("easy")
        self.audio_controller.toggle()

        self.objects = AnimGroup()
        self.canvas.add(self.objects)

        self.initialize_menu()

    def initialize_menu(self):
        self.canvas.clear()
        self.state = "menu"
        rect = Rectangle(pos=(0,0), size=(Window.width, Window.height), texture=Image('assets/menu.png').texture)
        self.canvas.add(rect)

    def initialize_dead(self):
        self.canvas.clear()
        self.state = "dead"
        rect = Rectangle(pos=(0,0), size=(Window.width, Window.height), texture=Image('assets/dead.png').texture)
        self.canvas.add(rect)
        self.audio_controller.turn_off()

    def initialize_game(self, difficulty):
        self.canvas.clear()
        self.state = "game"
        self.difficulty = difficulty

        self.audio_controller = AudioController(self.difficulty)
        self.audio_controller.toggle()

        self.notes_down = [] # an array that keeps track of all notes that are currently being played on midi keyboard

        # The display for the gems, now bar, and bar lines
        self.canvas.add(Color(1,1,1))
        rect = Rectangle(pos=(0,0), size=(Window.width, Window.height), texture=Image('assets/bg2.png').texture)

        self.canvas.add(rect)
        self.lane_manager = LaneManager()
        #self.canvas.add(self.lane_manager)

        # Display the status of the game through the text labels

        self.canvas.add(Color(1,1,1))
        self.hud = Rectangle(pos=(0,Window.height/1.12), size=(Window.width/4, Window.height/9), texture=Image('assets/tophub.png').texture)
        self.canvas.add(self.hud)
        #rect = Rectangle(pos=(0,Window.height-Window.height/10), size=(Window.width, Window.height/10))
        #self.canvas.add(rect)
        self.canvas.add(Color(1,1,1))
        self.hud_score = Rectangle(pos=(Window.width/1.26,Window.height/1.12), size=(Window.width/5, Window.height/9), texture=Image('assets/topscore.png').texture)
        self.canvas.add(self.hud_score)

        self.score_label = score_label()
        self.add_widget(self.score_label)
        self.hp_label = hp_label()
        self.add_widget(self.hp_label)

        self.enemy_times = []
        self.enemy_lanes = []
        self.enemy_types = []

        self.enemy_manager = EnemyManager()
        self.canvas.add(self.enemy_manager)

        if difficulty == "easy":
            read_data("song_annotations/hallelujah_left_hand.txt",
                "song_annotations/hallelujah_right_hand.txt", self.enemy_times, self.enemy_lanes, self.enemy_types)
        elif difficulty == "medium":
            read_data("song_annotations/epiphany_left_hand.txt",
                "song_annotations/epiphany_right_hand.txt", self.enemy_times, self.enemy_lanes, self.enemy_types)
        elif difficulty == "hard":
            read_data("song_annotations/WIWYM_left_hand.txt",
                "song_annotations/WIWYM_right_hand.txt", self.enemy_times, self.enemy_lanes, self.enemy_types)

        self.prev_time = time.time()
        self.elapsed_time = 0
        self.note_index = 0

        window_size = 4 # 4 seconds of notes are displayed
        x_scale = Window.width / window_size # pixels / sec

        # Create the player object which will store and control the state of the game
        self.player = Player(self.hp_label,self.score_label, self.enemy_times, self.enemy_lanes, self.enemy_types, self.enemy_manager)
        self.canvas.add(self.player)
        self.player.toggle()


    def generate_note(self, note):
        self.audio_controller.generate_note(note)

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        if self.state == "menu":
            if keycode[1] == '3':
                self.initialize_game()

        if self.state == "game":
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

    def on_touch_down(self, touch):
        p = touch.pos
        self.x = p[0]
        self.y = p[1]

        if self.state == "menu":
            if self.x > 575 and self.x < 1020 and self.y > 750 and self.y < 900:
                self.initialize_game("easy")
            elif self.x > 575 and self.x < 1020 and self.y > 500 and self.y < 645:
                self.initialize_game("medium")
            elif self.x > 575 and self.x < 1020 and self.y > 210 and self.y < 360:
                self.initialize_game("hard")

        if self.state == "dead":
            if self.x > 630 and self.x < 975 and self.y > 350 and self.y < 600:
                self.initialize_menu()

    def on_key_up(self, keycode):
        if self.state == "game":
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

        if self.state == "game":
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

            if self.player.hp <= 0:
                self.initialize_dead()

run(MainWidget)
