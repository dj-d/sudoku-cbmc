import os
import argparse


def init_sudoku(sudoku_to_solve):
    sudoku = []

    file = open(sudoku_to_solve, 'r')
    for row in file:
        sudoku.append([int(x) for x in row.split()])
    file.close

    return sudoku


def init_model(sudoku, counter):
    sudoku_str = str(sudoku).replace('[', '{').replace(']', '}')

    # Read C stub
    file = open('model.stub', 'r')
    c_code = file.read()
    file.close()

    c_code = c_code.replace('__TO_REPLACE__', sudoku_str)

    # Create C model
    file = open(f'model_{counter}.c', 'w')
    file.write(c_code)
    file.close()


def run(counter):
    os.system(f'cd ../cbmc-5.42.0 && ./cbmc ../part_II/model_{counter}.c --trace > ../part_II/file_{counter}.log')


def is_solution(counter):
    try:
        file = open(f'file_{counter}.log', 'r')
        lines = file.read().split('\n')
        file.close()

        if lines[-2] == 'VERIFICATION FAILED':
            return True
        else:
            return False

    except IOError:
        return False


def get_sudoku_solution(sudoku, counter):
    solution = []
    assume = ''

    file = open(f'file_{counter}.log', 'r')
    lines = file.read().split('\n')
    file.close()

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

                sudoku[x][y] = value

                solution.append(f'sudoku[{x}][{y}] == {value}')
                assume = '__VERIFIER_assume(!(' + ' && '.join(solution) + '));'
    
    # print(f'Counter: {counter}')
    # print_sudoku(sudoku)

    return sudoku, assume


def create_model_with_assume(counter, assume):
    file = open(f'model_{counter}.c', 'r')
    model = file.read()
    file.close()

    model = model.replace('//SUDOKU_ASSUME', assume + '\n\t//SUDOKU_ASSUME')

    file = open(f'model_{counter + 1}.c', 'w')
    file.write(model)
    file.close()


def print_sudoku(sudoku):
    for line in sudoku:
            print(' '.join(map(str, line)))


def clean_file():
    os.system('rm file_*.log model_*.c')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '--sudoku', '-s',
        dest='sudoku_to_solve',
        required=False,
        type=str,
        help=''
    )

    parser.add_argument(
        '--silent',
        dest='silent',
        required=False,
        action="store_true",
        help=''
    )

    args = parser.parse_args()

    counter = 0

    sudoku = init_sudoku(args.sudoku_to_solve)

    init_model(sudoku, counter)

    while True:
        run(counter)

        _sudoku, _assume = get_sudoku_solution(sudoku, counter)

        if not is_solution(counter):
            break

        if not args.silent:
            print(f"Solution #{counter + 1}: ")
            print_sudoku(_sudoku)
            print('\n')

        create_model_with_assume(counter, _assume)

        counter += 1

    if counter > 0:
        print(f'NUMBER OF SOLUTIONS: {counter}')
    else:
        print('UNSOLVABLE')

    clean_file()