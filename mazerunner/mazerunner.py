import random
import curses
import time
import sys


grid = []
player_pos = {}
exit_pos = {}
screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(1)

def init():
    """Read maze from file and place the player in a random spot."""
    with open("./mazes/rakkar16.txt", "r") as f:
        for line in f:
            row = list(line.strip())
            grid.append(row)

    width = len(grid[0])
    height = len(grid)

    for idx, row in enumerate(grid):
        if 'X' in row:
            exit_pos['x'] = row.index('X')
            exit_pos['y'] = idx

    while(True):
        x = random.randint(0, width)
        y = random.randint(0, height)

        if grid[y][x] == ' ':
            grid[y][x] = '^'
            player_pos['x'] = x
            player_pos['y'] = y
            break


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
    for row in grid:
        screen.addstr(''.join(row) + '\n')
    screen.refresh()


def pushBlock(x, y):
    """If given x, y is empty, place a block there."""
    if grid[y][x] == ' ':
        grid[y][x] = '#'
        return True
    return False

def updatePlayerPosition(direction):
    """Updates the grid depending on direction entered by user."""
    oldX = player_pos['x']
    oldY = player_pos['y']

    if direction == 'u':
        if grid[oldY][oldX] != '^':
            grid[oldY][oldX] = '^'
            return
        if grid[oldY-1][oldX] == '#':
            if not isBorderBlock(oldX, oldY-1):
                if not pushBlock(oldX, oldY-2):
                    return
            else:
                return
        player_pos['y'] -= 1

    elif direction == 'd':
        if grid[oldY][oldX] != 'v':
            grid[oldY][oldX] = 'v'
            return
        if grid[oldY+1][oldX] == '#':
            if not isBorderBlock(oldX, oldY+1):
                if not pushBlock(oldX, oldY+2):
                    return
            else:
                return
        player_pos['y'] += 1

    elif direction == 'l':
        if grid[oldY][oldX] != '<':
            grid[oldY][oldX] = '<'
            return
        if grid[oldY][oldX-1] == '#':
            if not isBorderBlock(oldX-1, oldY):
                if not pushBlock(oldX-2, oldY):
                    return
            else:
                return
        player_pos['x'] -= 1

    else:
        if grid[oldY][oldX] != '>':
            grid[oldY][oldX] = '>'
            return
        if grid[oldY][oldX+1] == '#':
            if not isBorderBlock(oldX+1, oldY):
                if not pushBlock(oldX+2, oldY):
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
        render()

if __name__ == "__main__":
    init()
    render()
    gameLoop()
