chord_dict = {
    'c_low' : [48, 52, 55],
    'd_low' : [50, 53, 57],
    'e_low' : [55, 59, 52],
    'f_low' : [53, 60, 57],
    'g_low' : [59, 62, 55],
    'a_low' : [60, 64, 57],
    'b_low' : [62, 65, 59],
    'c_high' : [64, 67, 60]
}

chord_to_lane = {
    'c_low' : 0,
    'd_low' : 1,
    'e_low' : 2,
    'f_low' : 3,
    'g_low' : 4,
    'a_low' : 5,
    'b_low' : 6,
    'c_high' : 7
}

lane_to_chord = {
    0: 'c_low',
    1: 'd_low',
    2: 'e_low',
    3: 'f_low',
    4: 'g_low',
    5: 'a_low',
    6: 'b_low',
    7: 'c_high'
}

lane_to_midi = {
    0: 60,
    1: 62,
    2: 64,
    3: 65,
    4: 67,
    5: 69,
    6: 71,
    7: 72
}
