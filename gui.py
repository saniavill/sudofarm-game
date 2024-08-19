import pygame as pg
import time
import requests
from sudoku_solver import valid, solve

pg.font.init()
# Uploading images
images = {}
for i in range(10):
    images[i] = pg.image.load(f'{i}.png')
image_size = (50, 50)
for key in images:
    images[key] = pg.transform.scale(images[key], image_size)

# Creating the sudoku grid
class Grid:
    response = requests.get('https://sugoku.onrender.com/board?difficulty=medium')
    board = response.json()['board']


    def __init__(self, rows, cols, width, height, screen):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.screen = screen
        self.squares = [[Square(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.model = None
        self.selected = None
        self.update_model()

    def update_model(self):
        self.model = [[self.squares[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.squares[row][col].value == 0:
            self.squares[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row, col)) and self.solve():
                return True

            else:
                self.squares[row][col].set(0)
                self.squares[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.squares[row][col].set_temp(val)

    def draw(self):
        # Grid lines:
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                wdth = 4
            else:
                wdth = 1
            pg.draw.line(self.screen, (124, 70, 19), (0, i * gap), (self.width, i * gap), wdth)
            pg.draw.line(self.screen, (124, 70, 19), (i * gap, 0), (i * gap, self.height), wdth)
        # Draw cubes:
        for i in range(self.rows):
            for j in range(self.cols):
                self.squares[i][j].draw(self.screen)

    def draw_pics(self):
        for row in range(9):
            for col in range(9):
                num = self.squares[row][col]
                if num != 0:
                    self.screen.blit(images[num], (col * image_size[0], row * image_size[1]))

    def select(self, row, col):
        # Reset order
        for i in range(self.rows):
            for j in range(self.cols):
                self.squares[i][j].selected = False
        self.squares[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        row, col = self.selected
        if self.squares[row][col].value == 0:
            self.squares[row][col].set_temp(0)

    def click(self, pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.squares[i][j].value == 0:
                    return False
        return True

    def solve(self):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i

                if self.solve():
                    return True

                self.model[row][col] = 0
        return False

    def solve_gui(self):
        self.update_model()
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find
        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i
                self.squares[row][col].set(i)
                self.squares[row][col].draw_change(self.screen, True)
                self.update_model()
                pg.display.update()
                pg.time.delay(100)

                if self.solve_gui():
                    return True
                self.model[row][col] = 0
                self.squares[row][col].set(0)
                self.squares[row][col].draw_change(self.screen, False)
                pg.display.update()
                pg.time.delay(500)

        return False


class Square:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = None
        self.temp = 0

    def draw(self, screen):
        font1 = pg.font.SysFont("Grand9K Pixel", 30)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            # for the temporary value (note):
            txt = font1.render(str(self.temp), 1, (113, 113, 113))
            screen.blit(images[self.temp], (x + 5, y + 5))
        elif not(self.value == 0):
            # for values initiated in the game:
            #txt = font1.render(str(self.value), 1, (28, 28, 28)) would be used to display numbers instead of pixel art
            screen.blit(images[self.value], (x + (gap/2 - image_size[0]/2), y + (gap/2 - image_size[0]/2)))

        if self.selected:
            pg.draw.rect(screen, (255, 184, 43), (x, y, gap, gap), 3)



    def draw_change(self, screen, g=True):
        font1 = pg.font.SysFont("Grand9K Pixel", 40)

        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        pg.draw.rect(screen, (107, 131, 86), (x, y, gap, gap), 0)

        txt = font1.render(str(self.value), 1, (0, 0, 0))
        screen.blit(txt, (x + (gap / 2 - txt.get_width() / 2), y + (gap / 2 - txt.get_height() / 2)))

        if g:
            pg.draw.rect(screen, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pg.draw.rect(screen, (255, 0, 0), (x, y, gap, gap), 3)


    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def find_empty(brd):
    for i in range(len(brd)):
        for j in range(len(brd[0])):
            if brd[i][j] == 0:
                # Row, column:
                return (i, j)
    return None


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


def redraw_screen(screen, brd, time, strikes):
    screen.fill((107, 131, 86))
    font2 = pg.font.SysFont("Grand9K Pixel", 30)
    txt = font2.render("Time: " + format_time(time), 1, (124, 70, 19))
    screen.blit(txt, (480 - 110, 490))
    txt = font2.render("X " * strikes, 1, (124, 70, 19))
    screen.blit(txt, (10, 500))
    brd.draw()


def format_time(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute //60

    formatted = " " + str(minute) + ":" + str(sec)
    return formatted


def main():
    screen = pg.display.set_mode((480, 580))
    pg.display.set_caption("SUDOFARM")
    board = Grid(9, 9, 480, 480, screen)
    key = None
    istrue = True
    start = time.time()
    strikes = 0
    while istrue:

        play_time = round(time.time() - start)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                istrue = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    key = 1
                if event.key == pg.K_2:
                    key = 2
                if event.key == pg.K_3:
                    key = 3
                if event.key == pg.K_4:
                    key = 4
                if event.key == pg.K_5:
                    key = 5
                if event.key == pg.K_6:
                    key = 6
                if event.key == pg.K_7:
                    key = 7
                if event.key == pg.K_8:
                    key = 8
                if event.key == pg.K_9:
                    key = 9
                if event.key == pg.K_KP1:
                    key = 1
                if event.key == pg.K_KP2:
                    key = 2
                if event.key == pg.K_KP3:
                    key = 3
                if event.key == pg.K_KP4:
                    key = 4
                if event.key == pg.K_KP5:
                    key = 5
                if event.key == pg.K_KP6:
                    key = 6
                if event.key == pg.K_KP7:
                    key = 7
                if event.key == pg.K_KP8:
                    key = 8
                if event.key == pg.K_KP9:
                    key = 9
                if event.key == pg.K_DELETE:
                    board.clear()
                    key = None

                if event.key == pg.K_SPACE:
                    board.solve_gui()

                if event.key == pg.K_RETURN:
                    i, j = board.selected
                    if board.squares[i][j].temp != 0:
                        if board.place(board.squares[i][j].temp):
                            print('Success')
                        else:
                            print('Wrong')
                            strikes += 1
                        key = None
                        if board.is_finished():
                            print("Game over")
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None
        if board.selected and key != None:
            board.sketch(key)

        redraw_screen(screen, board, play_time, strikes)

        pg.display.update()


main()

pg.quit()

