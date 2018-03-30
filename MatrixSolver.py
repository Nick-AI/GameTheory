import random
import copy
import json
import numpy as np
from operator import itemgetter
from tqdm import tqdm
from fractions import *
from decimal import *

def create_matrix():
    nb_rows = random.randint(2, 10)
    nb_cols = random.randint(2, 10)
    matrix = np.random.randint(low=-15, high=15, size=(nb_rows, nb_cols), dtype=int)
    return matrix, nb_rows, nb_cols


def solve_matrix(test_values=None, rows=None, cols=None, random=False):
    d = 1
    solved = False
    count = 0
    if random:
        s_matrix, rows, cols = create_matrix()
        intial_matr = copy.deepcopy(s_matrix)
    else:
        s_matrix, rows, cols = np.array(test_values), rows, cols

    # remove all zeros
    min = s_matrix[np.unravel_index(np.argmin(s_matrix, axis=None), s_matrix.shape)]
    # min idx = print(np.unravel_index(np.argmin(s_matrix, axis=None), s_matrix.shape))
    s_matrix = [num+abs(min) for num in [item for item in s_matrix]]

    # augment
    right = np.array([1]*rows)
    bot = np.array([-1]*cols)
    corner = 0
    blue_left = list(range(len(right)))
    red_top = list(range(len(bot)))
    blue_bot = [None] * len(bot)
    red_right = [None] * len(right)

    while not solved:
        # find pivot element
        mins = [(1000, 1000, 1000)]*cols
        for row_idx in range(rows):
            for col_idx, elem in enumerate(s_matrix[row_idx]):
                pot_piv = get_pivot_crit(elem, right[row_idx], bot[col_idx])
                if mins[col_idx][0] > pot_piv:
                    mins[col_idx] = (pot_piv, row_idx, col_idx) # set containing value and position of pivot
        pivot = max(mins)
        pivot = (s_matrix[pivot[1]][pivot[2]], pivot[1], pivot[2])

        # re-populate schema
        s_matrix[pivot[1]][pivot[2]] = d
        s_matrix, right, bot, corner = populator(pivot, s_matrix, d, right, bot, corner)
        d = pivot[0]

        # strategy augments
        temp = blue_left[pivot[1]]
        blue_bot[pivot[2]] = blue_left[pivot[1]]
        blue_left[pivot[1]] = temp
        temp = red_top[pivot[2]]
        red_right[pivot[1]] = red_top[pivot[2]]
        red_top[pivot[2]] = temp
        solved = True
        for item in bot:
            if item < 0:
                solved = False
        for item in right:
            if item < 0:
                solved = False
        count += 1
        if count > 5000:
            raise Exception


    v = Decimal(d/corner)
    v += min
    v = round(v, 3)
    v = str(Fraction(v))
    row_strats = set()
    col_strats = set()
    for i in range(len(bot)):
        if blue_bot[i] is not None:
            row_strats.add((int(blue_bot[i]), int(bot[i])))
    for i in range(len(right)):
        if red_right[i] is not None:
            col_strats.add((int(red_right[i]), int(right[i])))
    sorted(row_strats, key=itemgetter(0))
    sorted(col_strats, key=itemgetter(0))
    if random:
        return intial_matr, v, row_strats, col_strats
    else:
        return v, row_strats, col_strats


def get_pivot_crit(p, r, c):
    if p == 0:
        return 10000
    return -1*((c*r)/p)


def populator(p, matrix, d, right, bot, corner):
    temp = copy.deepcopy(matrix)
    temp_right = list(right)
    temp_bot = list(bot)

    #regular matrix
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if row == p[1] and col == p[2]:
                pass
            elif row == p[1]:
                pass
            elif col == p[2]:
                temp[row][col] = -1 * matrix[row][col]
            else:
                temp[row][col] = ((int(matrix[row][col]) * int(p[0])) - (int(matrix[p[1]][col]) *
                                                                         int(matrix[row][p[2]]))) / d

    #augments
    for i in range(len(right)):
        if i != p[1]:
            temp_right[i] = ((right[i] * p[0]) - (right[p[1]] * matrix[i][p[2]])) / d
    for i in range(len(bot)):
        if i != p[2]:
            temp_bot[i] = ((bot[i] * p[0]) - (matrix[p[1]][i] * bot[p[2]])) / d
        else:
            temp_bot[i] = -bot[i]
    corner = ((corner * p[0]) - (bot[p[2]] * right[p[1]])) / d
    return temp, temp_right, temp_bot, corner


if __name__.endswith('__main__'):
    while True:
        choice = input('If you want to solve a specific matrix, enter "y".\nIf you would rather generate a random '
                       'matrix with solution, type in "n"\n')
        if choice.lower() == 'y':
            dims = input('What are the dimensions of your matrix? Enter as rows x columns\n').strip().lower().split('x')
            print('Input your rows, one by one, separated by pressing enter, with the items separated by commas.')
            matr = []
            for i in range(int(dims[0])):
                elems = input('Enter row '+ str(i+1))
                matr.append([int(item) for item in elems.strip().split(',')])
            v, row_strats, col_strats = solve_matrix(test_values=matr, rows=int(dims[0]), cols=int(dims[1]))
            print("The game's value v=", v)
            print('The row player plays the following strategies with specified ratios')
            for item in row_strats:
                print('Strategy:', item[0]+1, 'Ratio:', item[1])
            print('The column player plays the following strategies with specified ratios')
            for item in col_strats:
                print('Strategy:', item[0]+1, 'Ratio:', item[1])
        elif choice.lower() == 'g':
            prog_bar = tqdm(total = 1000)
            counter = 0
            matrices = []
            v_s = []
            r_strats = []
            c_strats = []
            while counter < 1000:
                try:
                    gen_matrix, v, row_strats, col_strats = solve_matrix(random=True)
                    if gen_matrix.tolist() in matrices:
                        pass
                    else:
                        matrices.append(gen_matrix.tolist())
                        v_s.append(v)
                        r_strats.append(list(row_strats))
                        c_strats.append(list(col_strats))
                        prog_bar.update(1)
                        counter += 1
                except Exception as ex:
                    pass
            prog_bar.close()
            d_log = {}
            d_log['matrix'] = matrices
            d_log['row_strats'] = r_strats
            d_log['col_strats'] = c_strats
            d_log['v'] = v_s

            json_file = './data.json'
            with open(json_file, 'w') as log_file:
                json.dump(d_log, log_file, indent=4, sort_keys=True)
        else:
            sol_found = False
            while not sol_found:
                try:
                    gen_matrix, v, row_strats, col_strats = solve_matrix(random=True)
                    sol_found = True
                except:
                    pass
            print('The matrix generated was:\n', gen_matrix)
            print("The game's value v=", v)
            print('The row player plays the following strategies with specified ratios')
            for item in row_strats:
                print('Strategy:', item[0]+1, 'Ratio:', item[1])
            print('The column player plays the following strategies with specified ratios')
            for item in col_strats:
                print('Strategy:', item[0]+1, 'Ratio:', item[1])
        if input('If you wish to continue, enter "yes", otherwise enter "no".\n').lower()[0] == 'n':
            break



"""
y
2x3
1, -3, 2
3, -2, 4

y
3x3
6, 0, 3
8, -2, 3
4, 6, 5
"""
