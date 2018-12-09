import rtmidi_python as rtmidi
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.note import *
from common.gfxutil import *
from common.synth import *

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

        self.bg_wave_file_gen = WaveGenerator(WaveFile("data/WhenIWasYourMan.wav"))
        self.bg_wave_file_gen.set_gain(0.5)
        self.mixer.add(self.bg_wave_file_gen)

        if(self.MIDI_ENABLED is True):
            self.midi_in = rtmidi.MidiIn(b'in')
            self.midi_in.open_port(0)

    # start / stop the song
    def toggle(self):
        self.bg_wave_file_gen.play_toggle()

    # play a sound-fx (miss sound)
    # def play_sfx(self):
    #     self.miss_note_gen = WaveGenerator(WaveFile("error.wav"))
    #     self.mixer.add(self.miss_note_gen)

    def turn_off(self):
        self.bg_wave_file_gen.pause()
        self.mixer.set_gain(0)

    def generate_note(self, note):
        self.synth.noteon(self.channel, note, 100)

    def note_off(self, note):
        self.synth.noteoff(self.channel, note)

    # needed to update audio
    def on_update(self):
        self.audio.on_update()
