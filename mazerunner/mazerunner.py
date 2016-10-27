#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import signal
import random
import curses
import time
import sys
import pdb
import os
import threading
import atexit
import locale
locale.setlocale(locale.LC_ALL,"") # necessary to get curses to work with unicode

grid = []
player_pos = {}
trolls = []
exit_pos = {}
screen = curses.initscr()
curses.start_color()
curses.use_default_colors()
curses.noecho()
curses.cbreak()

curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK) # trolls
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # walls
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) # player
curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_WHITE) # exit
curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK) # empty space

# characters to use when drawing
Troll = u'☃' # u'T'
Wall  = u'░' # u'#'
Exit  = u'⚙' # u'X'
Empty = u'∴' # u' '
Player = (u'◀', u'▲', u'▶', u'▼') #(u'<', u'^', u'>', u'v')
# indices into Player for different orientations
LEFT  = 0
UP    = 1
RIGHT = 2
DOWN  = 3

screen.keypad(1)
def doexit():
    from subprocess import call
    call(["stty", "sane"])
atexit.register(doexit)

def sig_handler(signal, frame):
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    sys.exit(0)

def getEmptySpace(width, height):
    """Returns a random empty spot in the maze."""
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if grid[y][x] == Empty:
            return x, y


def init():
    """Read maze from file and place player and troll in random spots."""
    # default maze file
    fname = "rakkar16.txt"
    argc = len(sys.argv)
    if argc > 1:
        # use the specified maze name
        fname = sys.argv[1]
    fname = "mazerunner/mazes/"+fname
    if not os.path.exists(fname):
        sys.exit("Maze file does not exist")
    # perhaps use a generated maze here
    with open(fname, "r") as f:
        for line in f:
            # replace markers in input for walls/etc with characters used for rendering
            row = list(line.strip().decode("utf-8").replace(u'#', Wall).replace(' ', Empty).replace('X', Exit))
            grid.append(row)

    width = len(grid[0])
    height = len(grid)

    for idx, row in enumerate(grid):
        if Exit in row:
            exit_pos['x'] = row.index(Exit)
            exit_pos['y'] = idx

    player_pos['x'], player_pos['y'] = getEmptySpace(width, height)
    grid[player_pos['y']][player_pos['x']] = Player[UP]

    for t in range(10):
        x, y = getEmptySpace(width, height)
        grid[y][x] = Troll 
        trolls.append({'x': x, 'y': y})


def isBorderBlock(x, y):
    """Checks if given x, y corresponds to a border block."""
    width = len(grid[0])
    height = len(grid)

    if x == 0 or x == width - 1:
        return True
    if y == 0 or y == height - 1:
        return True
    return False


def render():
    """Clear screen and redraw it."""
    screen.clear()

    temp = grid
    for row in temp:
        for idx, ch in enumerate(row):
            if ch == Wall:
                screen.addstr(ch.encode('utf8'), curses.color_pair(1))
            elif ch == Troll:
                screen.addstr(ch.encode('utf8'), curses.color_pair(4))
            elif ch in Player:
                screen.addstr(ch.encode('utf8'), curses.color_pair(2))
            elif ch == Exit:
                screen.addstr(ch.encode('utf8'), curses.color_pair(3))
            else:
                screen.addstr(ch.encode('utf8'), curses.color_pair(5) | curses.A_DIM)
            if idx == (len(row) - 1):
                screen.addstr('\n')
    screen.refresh()


def moveTrolls():
    """Move trolls towards player."""
    while True:
        render()
        time.sleep(1)
        for troll in trolls:

            grid[troll['y']][troll['x']] = Empty

            trollDir = ''
            possibilities = []
            moved = False

            if troll['x'] == player_pos['x'] and troll['y'] == player_pos['y']:
                print('YOU WERE EATEN')
                sys.exit(0)

            if (troll['x'] - player_pos['x']) > 0:
                trollDir += 'l'
            elif (troll['x'] - player_pos['x']) < 0:
                trollDir += 'r'

            if (troll['y'] - player_pos['y']) > 0:
                trollDir += 'u'
            elif (troll['y'] - player_pos['y']) < 0:
                trollDir += 'd'

            for ch in trollDir:
                if ch == 'u':
                    possibilities.append((troll['x'], troll['y'] - 1))
                elif ch == 'd':
                    possibilities.append((troll['x'], troll['y'] + 1))
                elif ch == 'l':
                    possibilities.append((troll['x'] - 1, troll['y']))
                elif ch == 'r':
                    possibilities.append((troll['x'] + 1, troll['y']))

            for p in possibilities:
                if grid[p[1]][p[0]] in (Empty,) + Player:
                    troll['x'] = p[0]
                    troll['y'] = p[1]
                    grid[p[1]][p[0]] = Troll
                    moved = True
                    break

            if not moved:
                while True:
                    x = troll['x'] + [-1, 0, 1][random.randint(0, 2)]
                    y = troll['y'] + [-1, 0, 1][random.randint(0, 2)]

                    if grid[y][x] == Empty:
                        grid[troll['y']][troll['x']] = Empty
                        troll['x'] = x
                        troll['y'] = y
                        grid[y][x] = Troll
                        break


def pushBlock(x, y):
    """If given x, y is empty, place a block there."""
    if grid[y][x] == Empty:
        grid[y][x] = Wall
        return True
    elif grid[y][x] == Troll:
        for idx, troll in enumerate(trolls):
            if troll['x'] == x and troll['y'] == y:
                grid[y][x] = Wall
                del trolls[idx]
                return True
    return False


def updatePlayerPosition(direction):
    """Updates the grid depending on direction entered by user."""
    oldX = player_pos['x']
    oldY = player_pos['y']

    if grid[oldY][oldX] == Troll:
        print('YOU WERE EATEN')
        sys.exit(0)

    # turn player if they're changing direction
    if grid[oldY][oldX] != Player[direction]:
        grid[oldY][oldX] = Player[direction]
        return

    if direction == UP:
        if grid[oldY - 1][oldX] == Wall:
            if not isBorderBlock(oldX, oldY - 1):
                if not pushBlock(oldX, oldY - 2):
                    return
            else:
                return
        player_pos['y'] -= 1

    elif direction == DOWN:
        if grid[oldY + 1][oldX] == Wall:
            if not isBorderBlock(oldX, oldY + 1):
                if not pushBlock(oldX, oldY + 2):
                    return
            else:
                return
        player_pos['y'] += 1

    elif direction == LEFT:
        if grid[oldY][oldX - 1] == Wall:
            if not isBorderBlock(oldX - 1, oldY):
                if not pushBlock(oldX - 2, oldY):
                    return
            else:
                return
        player_pos['x'] -= 1

    else: # RIGHT
        if grid[oldY][oldX + 1] == Wall:
            if not isBorderBlock(oldX + 1, oldY):
                if not pushBlock(oldX + 2, oldY):
                    return
            else:
                return
        player_pos['x'] += 1

    grid[player_pos['y']][player_pos['x']] = grid[oldY][oldX]
    grid[oldY][oldX] = Empty

    for troll in trolls:
        if player_pos['y'] == troll['y'] and player_pos['x'] == troll['x']:
            grid[player_pos['y']][player_pos['x']] = Troll
            render()
            print('YOU WERE EATEN')
            sys.exit(0)

    if player_pos['y'] == exit_pos['y'] and player_pos['x'] == exit_pos['x']:
        print('VICTORY')
        sys.exit(0)


def gameLoop():
    """Main game loop; receives keypresses from user and handles them."""
    while True:
        ch = screen.getch()
        if ch == curses.KEY_UP:
            updatePlayerPosition(UP)
        elif ch == curses.KEY_DOWN:
            updatePlayerPosition(DOWN)
        elif ch == curses.KEY_LEFT:
            updatePlayerPosition(LEFT)
        elif ch == curses.KEY_RIGHT:
            updatePlayerPosition(RIGHT)
        elif ch == ord('q'):
            curses.nocbreak()
            screen.keypad(0)
            curses.echo()
            sys.exit(0)
        render()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sig_handler)
    init()
    troll_thread = threading.Thread(target=moveTrolls)
    troll_thread.daemon = True
    troll_thread.start()
    render()
    gameLoop()
