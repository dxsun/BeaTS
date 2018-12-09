"""
Chords that each enemy will represent
Pass in the root of the chord, the chord, and the inversion

root (string) - The root is the key that this chord is based on. E.g. if you have
C be the root, then it will be a C chord.

chord (string) - Chords come in form "135", where the number represents the tone of each
key to be pressed. "135" represents the root, the 3rd above the root, and 
the 5th above the root (note these are NOT semitones).

chord_type (string) (default "Major")- Major, Minor, Diminished, Augmented

inversion (int) (default 0) - Inversions are either 0, 1, 2, where a 0 represents no inversion,
1 represents the 1st inversion (the 6/3 inversion), 2 represents the 2nd inversion (6/4).
The 3rd inversion only exists for a 7th chord (i.e. you have 4 notes in the chord).

Important attributes:
	self.notes - access the actual semitones of the notes in the chord

EXAMPLE CHORD:
Chord(root="C", chord="135", chord_type="Major", inversion=0)

"""
class Chord():

	# Maps the key to the absolute MIDI semitone value
	semitone_mapping = {
		"C": 60,
		"D": 62,
		"E": 64,
		"F": 65,
		"G": 67,
		"A": 69,
		"B": 71,
	}	

	# Maps the interval (e.g. the Major 3 interval) to the amount of half steps (semitones)
	# requires to reach that interval from the root
	interval_to_semitones = {
		"1": 0,
		"2": 2,
		"3": 4,
		"4": 5,
		"5": 7,
		"6": 9,
		"7": 11,
		"8": 12
	}

	# Maps the amount of half steps to interval size
	semitones_to_interval = {value: key for key, value in interval_to_semitones.items()}

	complicated_semitones_to_interval = {
		0: "M1",
		1: "m2",
		2: "M2",
		3: "m3",
		4: "M3",
		5: "P4",
		6: "D5",
		7: "P5",
		8: "m6",
		9: "M6",
		10: "m7",
		11: "M7",
		12: "P8"
	}

	complicated_interval_to_semitones = {value: key for key, value in complicated_semitones_to_interval.items()}

	"""
	Valid inputs for each field:
	roots - "A", "B", "C", "D", "E", "F", "G". 
		  - Add "#" for sharp, "b" for flat, add "8" at end for higher octave (e.g. C#8)
	chords - any combination of 4 notes from 1 to 8, e.g. "135"
	chord types (only applicable if triad/dom7, i.e. "135") -
		3 notes: "Major", "Minor", "Diminished", "Augmented"
		4 notes: "Dominant"
	inversions - 0, 1, 2
	"""
	def __init__(self, root, chord, chord_type = "Major", inversion = 0):
		self.root = root
		self.chord = chord
		self.inversion = inversion

		self.num_notes = len(chord)

		root_note = semitone_mapping[root[0]]

		if '#' in root:
			root_note += 1
		elif 'b' in root:
			root_note -= '1'

		if '8' in root:
			root_note += interval_to_semitones['8']

		self.notes = [root_note + interval_to_semitones[value] for value in chord]

		# Changes note values based on chord type
		if len(chord) == 3:
			if chord_type == "Minor":
				self.notes[1] -= 1
			elif chord_type == "Diminished":
				self.notes[1] -= 1
				self.notes[2] -= 1
			elif chord_type == "Augmented":
				self.notes[2] += 1
		elif len(chord) == 4:
			if chord_type == "Dominant":
				self.notes[3] -= 1

		# ROUGH DRAFT - does inversions (have to think about what notes are valid)
		self.notes = self.notes[inversion:] + [note + 12 for note in self.notes[:inversion]]





