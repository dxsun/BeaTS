# Takes all the times and adds the empty space that was added to the
# wave file
def add_empty_space(empty_delay, annotation_file):
	new_lines = []

	with open(annotation_file, 'r') as f:
		lines = f.readlines()

		for line in lines:
			if '\t' in line:
				time, note = line.split('\t')
			elif ' ' in line:
				time, note = line.split(' ')
			new_lines.append(str(empty_delay + float(time)) + ' ' + note)

	with open(annotation_file[:-4] + "_test.txt", 'w') as f:
		for line in new_lines:
			f.write(line)


file_left = '../song_annotations/WIWYM_left_hand.txt'
file_right = '../song_annotations/WIWYM_right_hand.txt'
add_empty_space(5, file_left)
add_empty_space(5, file_right)