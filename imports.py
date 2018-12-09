import sys
import rtmidi_python as rtmidi
import time
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