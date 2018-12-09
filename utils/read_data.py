WIWYM_maps = {
    'c':1,
    'd':2, 
    'e':3,
    'f':4,
    'g':5,
    'a':6, 
    'b':7
}

# Takes in the path for the left hand and the right hand, and adds
# the corresponding enemies by sorting them 
def read_data(left_path, right_path, enemy_times, enemy_lanes, enemy_types):
    # minion = 'leader' if hand == 'left' else 'minion1'
    left_file = open(left_path)
    right_file = open(right_path)

    left_lines = left_file.readlines()
    right_lines = right_file.readlines()

    intermediate_data = []

    for minion, lines in [('case', left_lines), ('blue', right_lines)]:
    # for minion, lines in [('leader', left_lines)]:
    # for minion, lines in [('minion1', right_lines)]:
        print(lines)
        for line in lines:
            line = line.rstrip()
            splitted = line.split('\t')
            start_time_seconds = float(splitted[0])
            lane_number = WIWYM_maps[splitted[1]]


            intermediate_data.append((float(splitted[0]), WIWYM_maps[splitted[1]] - 1, minion) )
            # enemy_times.append(start_time_seconds)
            # # -1 for offset so when we annotate with
            # # c = 1, d = 2, etc.
            # enemy_lanes.append(lane_number - 1)
            # enemy_types.append(minion)

    intermediate_data.sort(key= lambda x: x[0])

    for time, lane, minion in intermediate_data:
        enemy_times.append(time)
        enemy_lanes.append(lane)
        enemy_types.append(minion)

    left_file.close()
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