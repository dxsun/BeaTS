# Takes all the times and adds the empty space that was added to the
# wave file
def add_empty_space(empty_delay, annotation_file):
	new_lines = []

	with open(annotation_file, 'r') as f:
		lines = f.readlines()

		for line in lines:
			print(line)
			if len(line.split(' ')) == 3:
				time, note, inv = line.split(' ')
				new_lines.append(str(empty_delay + float(time)) + ' ' + note + ' ' + inv)
			else:
				if '\t' in line:
					time, note = line.split('\t')
				elif ' ' in line:
					time, note = line.split(' ')
				new_lines.append(str(empty_delay + float(time)) + ' ' + note)

			

	with open(annotation_file[:-4] + "_test.txt", 'w') as f:
		for line in new_lines:
			f.write(line)


file_left = '../song_annotations/falling_left_hand_test.txt'
file_right = '../song_annotations/falling_right_hand_test.txt'
add_empty_space(5, file_left)
add_empty_space(5, file_right)