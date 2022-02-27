import os
import argparse

sudoku = []


def print_sudoku():
    for line in sudoku:
        print(' '.join(map(str, line)))


def fill_sudoku():
    file = open('file.log', 'r')
    lines = file.read().split('\n')

    if lines[-2] == 'VERIFICATION FAILED':
        for line in lines:
            if 'sudoku[' in line:
                line = line.replace('l', '')
                line = line.replace(' ', '')
                
                if '=0' in line: 
                    line = line[:-48]
                else:
                    line = line[:-34]

                if len(line) > 0:
                    x = int(line[7])
                    y = int(line[10])
                    value = int(line[13])

                    # print(f'[{x}][{y}] : {value}')

                    sudoku[x][y] = value
        
        print_sudoku()        
    else:
        print('UNSOLVABLE')


def create_model(sudoku_matrix):
    file = open(sudoku_matrix, 'r')
    for row in file:
        sudoku.append([int(x) for x in row.split()])
    file.close

    sudoku_str = str(sudoku).replace('[', '{').replace(']', '}')

    file = open('model.stub', 'r')
    code = file.read()
    file.close()

    code = code.replace('__TO_REPLACE__', sudoku_str)

    file = open('model.c', 'w')
    file.write(code)
    file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '--sudoku', '-s',
        dest='sudoku_matrix',
        required=True,
        type=str,
        help=''
    )

    args = parser.parse_args()

    create_model(args.sudoku_matrix)

    os.system('cd ../cbmc-5.42.0 && ./cbmc ../part_I/model.c --trace > ../part_I/file.log')

    fill_sudoku()

    os.system('rm file.log model.c')