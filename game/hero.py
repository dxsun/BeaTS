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