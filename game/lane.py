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