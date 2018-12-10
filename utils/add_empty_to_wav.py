import sys
sys.path.append('..')

# Takes all the times and adds the empty space that was added to the
# wave file
def add_empty_space(time, annotation_file):
	with open(annotation_file, 'r') as f:
		print(f.readlines())

file = '../song_annotations/WIWYM_left_hand.txt'
add_empty_space(5, file)