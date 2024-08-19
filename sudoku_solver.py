import requests


response = requests.get('https://sugoku.onrender.com/board?difficulty=medium')
board = response.json()['board']



def solve(brd):

    find = find_empty(brd)
    if not find:
        return True
    else:
        row, column = find

    for i in range(1, 10):
        if valid(brd, i, (row, column)):
            brd[row][column] = i

            if solve(brd):
                return True

            brd[row][column] = 0
    return False


def valid(brd, number, position):

    # Row
    for i in range(len(brd[0])):
        if brd[position[0]][i] == number and position[1] != i:
            return False

    # Column
    for i in range(len(brd)):
        if brd[i][position[1]] == number and position[0] != i:
            return False

    # Square box
    square_x = position[1] // 3
    square_y = position[0] // 3

    for i in range(square_y * 3, square_y * 3 + 3):
        for j in range(square_x * 3, square_x * 3 + 3):
            if brd[i][j] == number and (i, j) != position:
                return False

    return True


def print_board(brd):

    for i in range(len(brd)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - -")

        for j in range(len(brd[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")

            if j == 8:
                print(brd[i][j])
            else:
                print(str(brd[i][j]) + " ", end="")


def find_empty(brd):
    for i in range(len(brd)):
        for j in range(len(brd[0])):
            if brd[i][j] == 0:
                return (i, j)
    return None


print('Sudoku:')
print_board(board)
solve(board)
print("____________________________")
print('Answer:')
print_board(board)
