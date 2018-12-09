"""
DEPRECATED: don't need arbitary chord detection, probably just need to be
able to check if the current chord is equal to what you're playing

"""
from utils.Chord import Chord

semitone_mapping = Chord.complicated_semitones_to_interval

chord135 = ["M1", "M3", "P5"]


"""
CHORD INTERVALS (for 135 chord)

For chords, they follow a specific pattern in the intervals between the notes.
For example, for a Major chord, it goes [root, root + 4, root + 7] to represent
the 135 chord. This means that a 135 Major chord is determined by a root,
a root + 4 semitones, and a root + 7 semitones all played at once
""" 
chord_intervals = {
	"major": [0, 4, 7],
	"minor": [0, 3, 7],
	"diminished": [0, 3, 6],
	"augmented": [0, 4, 8]
}

def is_chord(array_of_notes_down, notes_desired):
    sorted_notes_down = sorted(array_of_notes_down)
    sorted_notes_desired = sorted(notes_desired)

    return sorted_notes_down == sorted_notes_desired

# Detects 135 chords and corresponding inversions
def detect_chord(current_key, notes_played):

	differences = [semitone_mapping[note - current_key] for note in notes_played]
	if differences == chord135:
		print("this is a 135 chord!")




