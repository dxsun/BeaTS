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

from game.hero import Hero
from game.enemy import Enemy
from utils.mappings import chord_dict, chord_to_lane, lane_to_chord, lane_to_midi

HERO_UPDATE_TIME = 0.1
SPAWN_TIME = 2.5

# Handles game logic and keeps score.
# Controls the display
class Player(InstructionGroup):
    def __init__(self, score_label, hp_label, gem_times, gem_lanes, enemy_types, enemy_manager):
        super(Player, self).__init__()
        self.MAX_HEALTH = 100000
        self.score = 0
        self.hp = self.MAX_HEALTH
        self.state = "idle"
        self.lane = 0
        self.score_label = score_label
        self.hp_label = hp_label
        # The image asset has it so that the now bbbar is at 12.15% of the width
        self.nowbar_x = Window.width*0.1215
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

            if (enemy_type == "case"):
                # yay you hit all the notes in the chord, now we can kill the enemy!
                # self.notes_down needs to contain the chord (LEFT HAND OCTAVE) in the correct lane
                if (hit_all_notes):
                    self.enemy_manager.kill_enemy_at_index(temp_gem_index)
                    time_difference = self.elapsed_time - self.gem_times[temp_gem_index]
                    self.score += int(300 * (1-time_difference*2))

            elif enemy_type == "blue": # This is a single note for the right hand, we need to see if it matches the correct lane
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
            self.hero.on_update(HERO_UPDATE_TIME)
            self.elapsed_time += time.time() - self.prev_time

            # THIS PART HANDLES ENEMIES AT THE NOW BAR
            # checks all the enemies that are beyond 0.4 seconds of the now bar
            while (self.current_enemy_index < len(self.gem_times) and self.gem_times[self.current_enemy_index] + 0.4 < self.elapsed_time):
                current_enemy = self.enemy_manager.enemies[self.current_enemy_index]

                # this means an enemy has more than 0 HP and is past the now bar by 0.4 seconds
                if (not current_enemy.hp <= 0):
                    self.hp -= 10
                    self.hero.change_state("hurt")
                    # current_enemy.kill_subenemies([0,1]) # explode the enemy on a pass
                    current_enemy.on_kill(True)
                    if (self.hp == 0):
                        print("GAME OVER")

                self.current_enemy_index += 1

            # THIS PART SPAWNS ENEMIES
            if (self.enemy_spawn_index < len(self.gem_times)):
                next_enemy = self.gem_times[self.enemy_spawn_index]
                next_lane = self.gem_lanes[self.enemy_spawn_index]
                if self.elapsed_time > (next_enemy - SPAWN_TIME):
                    self.enemy_manager.spawn_enemy(next_lane,self.enemy_types[self.enemy_spawn_index],0)
                    self.enemy_spawn_index += 1
            # self.enemy_manager.on_update()
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
