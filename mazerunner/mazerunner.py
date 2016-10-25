#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import random
import curses
import time
import sys
import pdb

grid = []
player_pos = {}
trolls = []
exit_pos = {}
screen = curses.initscr()
curses.start_color()
curses.use_default_colors()
curses.noecho()
curses.cbreak()

curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK) # trolls
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # walls
curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK) # player
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN) # exit

screen.keypad(1)


def getEmptySpace(width, height):
    """Returns a random empty spot in the maze."""
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if grid[y][x] == ' ':
            return x, y


def init():
    """Read maze from file and place player and troll in random spots."""
    with open("mazerunner/mazes/rakkar16.txt", "r") as f:
        for line in f:
            row = list(line.strip())
            grid.append(row)

    width = len(grid[0])
    height = len(grid)

    for idx, row in enumerate(grid):
        if 'X' in row:
            exit_pos['x'] = row.index('X')
            exit_pos['y'] = idx

    player_pos['x'], player_pos['y'] = getEmptySpace(width, height)
    grid[player_pos['y']][player_pos['x']] = '^'

    for t in range(10):
        x, y = getEmptySpace(width, height)
        grid[y][x] = 'T'
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
            if ch == '#':
                screen.addstr(ch, curses.color_pair(1))
            elif ch == 'T':
                screen.addstr(ch, curses.color_pair(4))
            elif ch in ('>', '<', 'v', '^'):
                screen.addstr(ch, curses.color_pair(2))
            elif ch == 'X':
                screen.addstr(ch, curses.color_pair(3))
            else:
                screen.addstr(ch)
            if idx == (len(row) - 1):
                screen.addstr('\n')
    screen.refresh()


def moveTrolls():
    """Move trolls towards player."""
    for troll in trolls:

        grid[troll['y']][troll['x']] = ' '

        trollDir = ''
        possibilities = []
        moved = False

        if troll['x'] == player_pos['x'] and troll['y'] == player_pos['y']:
            print 'YOU WERE EATEN'
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
            if grid[p[1]][p[0]] in (' ', 'v', '>', '<', '^'):
                troll['x'] = p[0]
                troll['y'] = p[1]
                grid[p[1]][p[0]] = 'T'
                moved = True
                break

        if not moved:
            while True:
                x = troll['x'] + [-1, 0, 1][random.randint(0, 2)]
                y = troll['y'] + [-1, 0, 1][random.randint(0, 2)]

                if grid[y][x] == ' ':
                    grid[troll['y']][troll['x']] = ' '
                    troll['x'] = x
                    troll['y'] = y
                    grid[y][x] = 'T'
                    break


def pushBlock(x, y):
    """If given x, y is empty, place a block there."""
    if grid[y][x] == ' ':
        grid[y][x] = '#'
        return True
    elif grid[y][x] == 'T':
        for idx, troll in enumerate(trolls):
            if troll['x'] == x and troll['y'] == y:
                grid[y][x] = '#'
                del trolls[idx]
                return True
    return False


def updatePlayerPosition(direction):
    """Updates the grid depending on direction entered by user."""
    oldX = player_pos['x']
    oldY = player_pos['y']

    if grid[oldY][oldX] == 'T':
        print 'YOU WERE EATEN'
        sys.exit(0)

    if direction == 'u':
        if grid[oldY][oldX] != '^':
            grid[oldY][oldX] = '^'
            return
        if grid[oldY - 1][oldX] == '#':
            if not isBorderBlock(oldX, oldY - 1):
                if not pushBlock(oldX, oldY - 2):
                    return
            else:
                return
        player_pos['y'] -= 1

    elif direction == 'd':
        if grid[oldY][oldX] != 'v':
            grid[oldY][oldX] = 'v'
            return
        if grid[oldY + 1][oldX] == '#':
            if not isBorderBlock(oldX, oldY + 1):
                if not pushBlock(oldX, oldY + 2):
                    return
            else:
                return
        player_pos['y'] += 1

    elif direction == 'l':
        if grid[oldY][oldX] != '<':
            grid[oldY][oldX] = '<'
            return
        if grid[oldY][oldX - 1] == '#':
            if not isBorderBlock(oldX - 1, oldY):
                if not pushBlock(oldX - 2, oldY):
                    return
            else:
                return
        player_pos['x'] -= 1

    else:
        if grid[oldY][oldX] != '>':
            grid[oldY][oldX] = '>'
            return
        if grid[oldY][oldX + 1] == '#':
            if not isBorderBlock(oldX + 1, oldY):
                if not pushBlock(oldX + 2, oldY):
                    return
            else:
                return
        player_pos['x'] += 1

    grid[player_pos['y']][player_pos['x']] = grid[oldY][oldX]
    grid[oldY][oldX] = ' '

    if player_pos['y'] == exit_pos['y'] and player_pos['x'] == exit_pos['x']:
        print 'VICTORY'
        sys.exit(0)


def gameLoop():
    """Main game loop; receives keypresses from user and handles them."""
    while True:
        ch = screen.getch()
        if ch == curses.KEY_UP:
            updatePlayerPosition('u')
        elif ch == curses.KEY_DOWN:
            updatePlayerPosition('d')
        elif ch == curses.KEY_LEFT:
            updatePlayerPosition('l')
        elif ch == curses.KEY_RIGHT:
            updatePlayerPosition('r')
        elif ch == ord('q'):
            curses.nocbreak()
            screen.keypad(0)
            curses.echo()
            sys.exit(0)
        moveTrolls()
        render()

if __name__ == "__main__":
    init()
    render()
    gameLoop()
