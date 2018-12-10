from utils.Chord import Chord

WIWYM_maps = {
    'c':1,
    'd':2,
    'e':3,
    'f':4,
    'g':5,
    'a':6,
    'b':7,
    'c8': 8
}

reverse_WIWYMY_map = {v:k for k,v in WIWYM_maps.items()}

# Takes in the path for the left hand and the right hand, and adds
# the corresponding enemies by sorting them
def read_data(left_path, right_path, enemy_times, enemy_lanes, enemy_types, enemies, inversions=False):
    # minion = 'leader' if hand == 'left' else 'minion1'

    left_file = open(left_path) if left_path else None
    right_file = open(right_path) if right_path else None

    left_lines = left_file.readlines() if left_file else []
    right_lines = right_file.readlines() if right_file else []

    intermediate_data = []

    for minion, lines in [('case', left_lines), ('blue', right_lines)]:
    # for minion, lines in [('case', left_lines)]:
    # for minion, lines in [('minion1', right_lines)]:
        for line in lines:
            line = line.rstrip()
            if '\t' in line:
                splitted = line.split('\t')
            elif ' ' in line:
                splitted = line.split(' ')
            start_time_seconds = float(splitted[0])
            lane_number = WIWYM_maps[splitted[1]]

            data = (float(splitted[0]), WIWYM_maps[splitted[1]] - 1, minion)
            if inversions and len(splitted) > 2:
                data += (int(splitted[2]),)

            intermediate_data.append(data)
            # enemy_times.append(start_time_seconds)
            # # -1 for offset so when we annotate with
            # # c = 1, d = 2, etc.
            # enemy_lanes.append(lane_number - 1)
            # enemy_types.append(minion)

    intermediate_data.sort(key= lambda x: x[0])

    if inversions:
        for i in range(len(intermediate_data)):
            data = intermediate_data[i]
            if len(data) == 3:
                time, lane, minion = data
                
                enemy_times.append(time)
                enemy_lanes.append(lane)
                enemy_types.append(minion)
                enemies.append(Chord(reverse_WIWYMY_map[lane + 1].upper(), "135"))

            elif len(data) == 4:
                time, lane, minion, inversion = data
                
                enemy_times.append(time)
                enemy_lanes.append(lane)
                enemy_types.append(minion)
                enemies.append(Chord(reverse_WIWYMY_map[lane + 1].upper(), "135", inversion=inversion))

                print("inversion:", inversion)
    else:
        for time, lane, minion in intermediate_data:
            enemy_times.append(time)
            enemy_lanes.append(lane)
            enemy_types.append(minion)
            enemies.append(Chord(reverse_WIWYMY_map[lane + 1].upper(), "135"))

    if left_file:
        left_file.close()
    if right_file:
        right_file.close()

# def read_data(hand, filepath, enemy_times, enemy_lanes, enemy_types):
#     minion = 'leader' if hand == 'left' else 'minion1'
#     file = open(filepath)
#     lines = file.readlines()
#     for line in lines:
#         line = line.rstrip()
#         splitted = line.split('\t')
#         start_time_seconds = float(splitted[0])
#         lane_number = WIWYM_maps[splitted[1]]


#         enemy_times.append(start_time_seconds)
#         # -1 for offset so when we annotate with
#         # c = 1, d = 2, etc.
#         enemy_lanes.append(lane_number - 1)
#         enemy_types.append(minion)

    # file = open(filepath)
    # lines = file.readlines()
    # for line in lines:
    #     line = line.rstrip()
    #     splitted = line.split('\t')
    #     start_time_seconds = float(splitted[0])
    #     lane_number = int(splitted[1])
    #     enemy_type = str(splitted[2])

    #     enemy_times.append(start_time_seconds)
    #     # -1 for offset so when we annotate with
    #     # c = 1, d = 2, etc.
    #     enemy_lanes.append(lane_number - 1)
    #     enemy_types.append(enemy_type)
