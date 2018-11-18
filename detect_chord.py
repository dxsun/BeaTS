from Chord import Chord

semitone_mapping = Chord.complicated_semitones_to_interval

chord135 = ["M1", "M3", "P5"]

# only works for 3 note chords currently
# only works for non inversions
def detect_chord(current_key, notes_played):
	differences = [semitone_mapping[note - current_key] for note in notes_played]
	if differences == chord135:
		print("this is a 135 chord!")




