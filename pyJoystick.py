#!/usr/bin/env python
# -*- coding: utf-8 -*-

#all info about setting up the Bluetooth are in runZX.sh

import pygame
from pygame.locals import *
from sense_hat import SenseHat
from time import sleep
from time import time
from collections import deque #optimized for pulling and pushing on both ends
from zx_sensor import ZxSensor
import random
from random import randint
import subprocess
import os 
from colour import Color
import math

import RPi.GPIO as GPIO
from gpiozero import Buzzer

# ------------------- Sounds ---------------------------

#making sure the output is 2.5# jack
subprocess.call('sudo amixer cset numid=3 1'.split(" ")) #no output

#volume to 100%
subprocess.call('amixer set PCM -- 100%'.split(" ")) #no output

# ------------------- Audio buzzer #1 ---------------------------
buzzer=19

#Disable warnings (optional)
GPIO.setwarnings(False)
#Select GPIO mode
GPIO.setmode(GPIO.BCM)
#Set buzzer - pin 19 as output

GPIO.setup(buzzer, GPIO.OUT)

p = GPIO.PWM(buzzer, 50)  # channel=12 frequency=50Hz
p.start(0)
try:
    for dc in range(0, 101, 5):
        p.ChangeDutyCycle(dc)
        sleep(0.1)
    for dc in range(100, -1, -5):
        p.ChangeDutyCycle(dc)
        sleep(0.1)
except KeyboardInterrupt:
    pass
p.stop()
GPIO.cleanup()

# ------------------- Audio buzzer #2 ----------------------------
##https://gist.github.com/mandyRae/459ae289cdfcf6d98a6b

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(buzzer, GPIO.OUT)

tone1 = GPIO.PWM(buzzer, 100)

#50 seems to be the all around best value for duty cycle for buzzers
tone1.start(50)

#Note frequencies, starting with a C
#speaker works good from 32hz to about 500hz, so the first four octaves here, fifth octave just for fun
#in case you're not familiar with musical notation, the 'b' after some of these indicates a flat so 'db' is 'd-flat'
c = [32, 65, 131, 262, 523]
db= [34, 69, 139, 277, 554]
d = [36, 73, 147, 294, 587]
eb= [37, 78, 156, 311, 622]
e = [41, 82, 165, 330, 659]
f = [43, 87, 175, 349, 698]
gb= [46, 92, 185, 370, 740]
g = [49, 98, 196, 392, 784]
ab= [52, 104, 208, 415, 831]
a = [55, 110, 220, 440, 880]
bb= [58, 117, 223, 466, 932]
b = [61, 123, 246, 492, 984]

#notes of two scales, feel free to add more
cmajor = [c, d, e, f, g, a, b]
aminor = [a, b, c, d, e, f, g]

def playScale(scale, pause):
    for i in range(0, 5):
        for note in scale:
            tone1.ChangeFrequency(note[i])
            time.sleep(pause)
    tone1.stop()
 
#call the playScale function   
#playScale(aminor, 0.5)

#Star Wars Theme -- Key of C
starwars_notes = [c[1], g[1], f[1], e[1], d[1], c[2], g[1], f[1], e[1], d[1], c[2], g[1], 
              f[1], e[1], f[1], d[1]]
starwars_beats = [4,4,1,1,1,4,4,1,1,1,4,4,1,1,1,4]

#London Bridges --Key of C
londonbridges_notes = [g[1], a[1], g[1], f[1], e[1], f[1], g[1], d[1], e[1], f[1],
                   e[1], f[1], g[1], g[1], a[1], g[1], f[1], e[1], f[1], g[1],
                   d[1], g[1], e[1], c[1]]
londonbridges_beats = [2, 0.5, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 2, 0.5, 1, 1, 1, 1,
                   2, 2, 2, 1,1]

def playSong(songnotes, songbeats, tempo):
    tone1.ChangeDutyCycle(50)
    for i in range(0, len(songnotes)):
        tone1.ChangeFrequency(songnotes[i])
        sleep(songbeats[i]*tempo)
    tone1.ChangeDutyCycle(0)

# ------------------- TODO ----------------------------

#Demonstrate boundary (maze)
# complement sound / vibration in 2D
# TF2 found position
# Treasure Hunt rename
#maze with treasure hunt
# 3 bips start position
# DIY vibration patter (intensity and frequency), victory,
# better field of view 



# ------------------- Parameters ----------------------------

useHandAsInput = True
lowWhite = 50
numberOfLastPositions = 8
HandX_max = 600
HandZ_max = 600
HandX_min = 0
HandZ_min = 0
mazeType = 2
deadbandX = 2
deadbandZ = 2
doTests = False
ZXMode = 0 ## 0 = Absolute,  1 = Relative
ZXdifferencialDividerX = 20 #more = slower maze movement
ZXdifferencialDividerZ = 20 #more = slower maze movement
ZXdifferencialoffsetX = -1 #more = more to left top
ZXdifferencialoffsetZ = -1 #more = more to left top

PerfectTime = 2.5
BadTime = 5

StartZoneSize = 3 # in number of LED
TargetZoneSize = 2 # in number of LED
NbrWalls = math.floor((8-StartZoneSize-TargetZoneSize-2)/2) + 2

# ------------------- David maze ----------------------------
X = [255, 0, 0]  # Red Start
Y = [0, 255, 0]  # Green destination
W = [255, 255, 255]  # White wall
O = [0, 0, 0]  # Black void

DavidMaze = [O] * (8*8)


#Add destination
DavidMaze[0:7*TargetZoneSize] = [Y] * (8*TargetZoneSize)

#Add start
DavidMaze[-7*StartZoneSize:] = [Y] * (8*StartZoneSize)

#Add start and destination walls
DavidMaze[7*TargetZoneSize+1:7*TargetZoneSize+1+8-1] = [W] * (8)
DavidMaze[-7*StartZoneSize-1-1-8+1:-7*StartZoneSize-1] = [W] * (8)

#add the other walls



# ------------------- Colors ----------------------------
blue    = Color("blue").get_rgb()
blue    = [int(blue[ii]*255) for ii in range(len(blue))]
yellow  = Color("yellow").get_rgb()
yellow  = [int(yellow[ii]*255) for ii in range(len(yellow))]
red     = Color("red").get_rgb()
red    = [int(red[ii]*255) for ii in range(len(red))]

lowWhite_Following = range(250, lowWhite, (lowWhite - 250) / numberOfLastPositions)

# ------------------- BLE ----------------------------
# Configure the BLE
print 'Preaparing BLE...'

try:
    subprocess.call('sudo service bluetooth restart'.split(" ")) #no output
    print subprocess.check_output('hciconfig')
    subprocess.call('sudo hciconfig hci0 up'.split(" ")) #no output
    print subprocess.check_output('hciconfig')
    print 'BLE is up and running'
except Exception:
    print 'Error while configuring BLE'

def BLESendEvent(eventType):
    if eventType == 0: #Start
        print "---> 3 Start beeps" # . . _
        pygame.mixer.music.load("Start.wav")
        pygame.mixer.music.play()
    elif eventType == 1: #Achievement (NOT victory)
        print "---> 1 ting" # . TF2 ting
        pygame.mixer.music.load("Achivement.wav")
        pygame.mixer.music.play()
    elif eventType == 2: #victory (NOT Achievement)
        print "---> 3 tings" # ... TF2 tings
        pygame.mixer.music.load("Victory.wav")
        pygame.mixer.music.play()
    elif eventType == 3: #wall bump 
        #print "---> 1 tongs" # . tongs
        pygame.mixer.music.load("WallHit.wav")
        pygame.mixer.music.play()
    elif eventType == 4: #fatality/end/general failure
        print "---> fail" # . . @@@
        pygame.mixer.music.load("Fatality.wav")
        pygame.mixer.music.play()
    elif eventType == 5: #waiting for input (why not?)
        print "---> 2 sharp spikes" #  | |
        pygame.mixer.music.load("Wait.wav")
        pygame.mixer.music.play()
    elif eventType == 6: #moving
        #print "---> smthg bip" # .
        pygame.mixer.music.load("Move.wav")
        pygame.mixer.music.play()
        
def BLESendTargetPolar(r, Theta):
##    print "--->#p," + str(Theta) + "," + str(r) + "\\r\\n"
    sleep(0)

def BLESendTargetCarthesianfromPolar(r, Theta):
    x = r * cos(Theta*math.pi/180)
    y = r * sin(Theta*math.pi/180)
##    print "--->#c," + str(x) + "," + str(y) + "\\r\\n"

def BLESendTargetPolarFromCarthesian(x, y):
    r = math.sqrt(math.pow((x),2) + math.pow((y),2))
    Theta = math.atan2(y,x)*180/math.pi
##    print "--->#p," + str(Theta) + "," + str(r) + "\\r\\n"   

def BLESendTargetCarthesian(x, y):
##    print "--->#c," + str(x) + "," + str(y) + "\\r\\n"
    sleep(0)

# ------------------- Maze 1 ----------------------------

if mazeType == 1:
    # Random Maze Generator using Depth-first Search
    # http://en.wikipedia.org/wiki/Maze_generation_algorithm
    # FB36 - 20130106

    mx = 8; my = 8 # width and height of the maze
    maze = [[0 for x in range(mx)] for y in range(my)]
    dx = [0, 1, 0, -1]; dy = [-1, 0, 1, 0] # 4 directions to move in the maze
    color = [(0, 0, 0), (255, 255, 255)] # RGB colors of the maze
    # start the maze from a random cell
    cx = random.randint(0, mx - 1); cy = random.randint(0, my - 1)
    maze[cy][cx] = 1; stack = [(cx, cy, 0)] # stack element: (x, y, direction)

    while len(stack) > 0:
        (cx, cy, cd) = stack[-1]
        # to prevent zigzags:
        # if changed direction in the last move then cannot change again
        if len(stack) > 2:
            if cd != stack[-2][2]: dirRange = [cd]
            else: dirRange = range(4)
        else: dirRange = range(4)

        # find a new cell to add
        nlst = [] # list of available neighbors
        for i in dirRange:
            nx = cx + dx[i]; ny = cy + dy[i]
            if nx >= 0 and nx < mx and ny >= 0 and ny < my:
                if maze[ny][nx] == 0:
                    ctr = 0 # of occupied neighbors must be 1
                    for j in range(4):
                        ex = nx + dx[j]; ey = ny + dy[j]
                        if ex >= 0 and ex < mx and ey >= 0 and ey < my:
                            if maze[ey][ex] == 1: ctr += 1
                    if ctr == 1: nlst.append(i)

        # if 1 or more neighbors available then randomly select one and move
        if len(nlst) > 0:
            ir = nlst[random.randint(0, len(nlst) - 1)]
            cx += dx[ir]; cy += dy[ir]; maze[cy][cx] = 1
            stack.append((cx, cy, ir))
        else: stack.pop()


# ------------------- Maze 2 ----------------------------
if mazeType == 2:
    # Easy to read representation for each cardinal direction.
    N, S, W, E = ('n', 's', 'w', 'e')

    class Cell(object):
        """
        Class for each individual cell. Knows only its position and which walls are
        still standing.
        """
        def __init__(self, x, y, walls):
            self.x = x
            self.y = y
            self.walls = set(walls)

        def __repr__(self):
            # <15, 25 (es  )>
            return '<{}, {} ({:4})>'.format(self.x, self.y, ''.join(sorted(self.walls)))

        def __contains__(self, item):
            # N in cell
            return item in self.walls

        def is_full(self):
            """
            Returns True if all walls are still standing.
            """
            return len(self.walls) == 4

        def _wall_to(self, other):
            """
            Returns the direction to the given cell from the current one.
            Must be one cell away only.
            """
            assert abs(self.x - other.x) + abs(self.y - other.y) == 1, '{}, {}'.format(self, other)
            if other.y < self.y:
                return N
            elif other.y > self.y:
                return S
            elif other.x < self.x:
                return W
            elif other.x > self.x:
                return E
            else:
                assert False

        def connect(self, other):
            """
            Removes the wall between two adjacent cells.
            """
            other.walls.remove(other._wall_to(self))
            self.walls.remove(self._wall_to(other))

    class Maze(object):
        """
        Maze class containing full board and maze generation algorithms.
        """

        # Unicode character for a wall with other walls in the given directions.
        UNICODE_BY_CONNECTIONS = {'ensw': '┼',
                                  'ens': '├',
                                  'enw': '┴',
                                  'esw': '┬',
                                  'es': '┌',
                                  'en': '└',
                                  'ew': '─',
                                  'e': '╶',
                                  'nsw': '┤',
                                  'ns': '│',
                                  'nw': '┘',
                                  'sw': '┐',
                                  's': '╷',
                                  'n': '╵',
                                  'w': '╴'}

        def __init__(self, width=20, height=10):
            """
            Creates a new maze with the given sizes, with all walls standing.
            """
            self.width = width
            self.height = height
            self.cells = []
            for y in range(self.height):
                for x in range(self.width):
                    self.cells.append(Cell(x, y, [N, S, E, W]))

        def __getitem__(self, index):
            """
            Returns the cell at index = (x, y).
            """
            x, y = index
            if 0 <= x < self.width and 0 <= y < self.height:
                return self.cells[x + y * self.width]
            else:
                return None

        def neighbors(self, cell):
            """
            Returns the list of neighboring cells, not counting diagonals. Cells on
            borders or corners may have less than 4 neighbors.
            """
            x = cell.x
            y = cell.y
            for new_x, new_y in [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]:
                neighbor = self[new_x, new_y]
                if neighbor is not None:
                    yield neighbor

        def _to_str_matrix(self):
            """
            Returns a matrix with a pretty printed visual representation of this
            maze. Example 5x5:
            OOOOOOOOOOO
            O       O O
            OOO OOO O O
            O O   O   O
            O OOO OOO O
            O   O O   O
            OOO O O OOO
            O   O O O O
            O OOO O O O
            O     O   O
            OOOOOOOOOOO
            """
            str_matrix = [['O'] * (self.width * 2 + 1)
                          for i in range(self.height * 2 + 1)]

            for cell in self.cells:
                x = cell.x * 2 + 1
                y = cell.y * 2 + 1
                str_matrix[y][x] = ' '
                if N not in cell and y > 0:
                    str_matrix[y - 1][x + 0] = ' '
                if S not in cell and y + 1 < self.width:
                    str_matrix[y + 1][x + 0] = ' '
                if W not in cell and x > 0:
                    str_matrix[y][x - 1] = ' '
                if E not in cell and x + 1 < self.width:
                    str_matrix[y][x + 1] = ' '

            return str_matrix

        def __repr__(self):
            """
            Returns an Unicode representation of the maze. Size is doubled
            horizontally to avoid a stretched look. Example 5x5:
            ┌───┬───────┬───────┐
            │   │       │       │
            │   │   ╷   ╵   ╷   │
            │   │   │       │   │
            │   │   └───┬───┘   │
            │   │       │       │
            │   └───────┤   ┌───┤
            │           │   │   │
            │   ╷   ╶───┘   ╵   │
            │   │               │
            └───┴───────────────┘
            """
            # Starts with regular representation. Looks stretched because chars are
            # twice as high as they are wide (look at docs example in
            # `Maze._to_str_matrix`).
            skinny_matrix = self._to_str_matrix()

            # Simply duplicate each character in each line.
            double_wide_matrix = []
            for line in skinny_matrix:
                double_wide_matrix.append([])
                for char in line:
                    double_wide_matrix[-1].append(char)
                    double_wide_matrix[-1].append(char)

            # The last two chars of each line are walls, and we will need only one.
            # So we remove the last char of each line.
            matrix = [line[:-1] for line in double_wide_matrix]

            def g(x, y):
                """
                Returns True if there is a wall at (x, y). Values outside the valid
                range always return false.
                This is a temporary helper function.
                """
                if 0 <= x < len(matrix[0]) and 0 <= y < len(matrix):
                    return matrix[y][x] != ' '
                else:
                    return False

            # Fix double wide walls, finally giving the impression of a symmetric
            # maze.
            for y, line in enumerate(matrix):
                for x, char in enumerate(line):
                    if not g(x, y) and g(x - 1, y):
                        matrix[y][x - 1] = ' '

            # Right now the maze has the correct aspect ratio, but is still using
            # 'O' to represent walls.

            # Finally we replace the walls with Unicode characters depending on
            # their context.
            for y, line in enumerate(matrix):
                for x, char in enumerate(line):
                    if not g(x, y):
                        continue

                    connections = set((N, S, E, W))
                    if not g(x, y + 1): connections.remove(S)
                    if not g(x, y - 1): connections.remove(N)
                    if not g(x + 1, y): connections.remove(E)
                    if not g(x - 1, y): connections.remove(W)

                    str_connections = ''.join(sorted(connections))
                    # Note we are changing the matrix we are reading. We need to be
                    # careful as to not break the `g` function implementation.
                    matrix[y][x] = Maze.UNICODE_BY_CONNECTIONS[str_connections]

            # Simple double join to transform list of lists into string.
            return '\n'.join(''.join(line) for line in matrix) + '\n'

        def randomize(self):
            """
            Knocks down random walls to build a random perfect maze.
            Algorithm from http://mazeworks.com/mazegen/mazetut/index.htm
            """
            cell_stack = []
            cell = random.choice(self.cells)
            n_visited_cells = 1

            while n_visited_cells < len(self.cells):
                neighbors = [c for c in self.neighbors(cell) if c.is_full()]
                if len(neighbors):
                    neighbor = random.choice(neighbors)
                    cell.connect(neighbor)
                    cell_stack.append(cell)
                    cell = neighbor
                    n_visited_cells += 1
                else:
                    cell = cell_stack.pop()

        @staticmethod
        def generate(width=20, height=10):
            """
            Returns a new random perfect maze with the given sizes.
            """
            m = Maze(width, height)
            m.randomize()
            return m


    def rotate(matrix, degree):
        if abs(degree) not in [0, 90, 180, 270, 360]:
            # raise error or just return nothing or original
            print "Err"
        if degree == 0:
            return matrix
        elif degree > 0:
            return rotate(zip(*matrix[::-1]), degree-90)
        else:
            return rotate(zip(*matrix)[::-1], degree+90)
 

# ------------------- Main ----------------------------

playSong(starwars_notes, starwars_beats, 0.2)

SensorIsPresent = False

try:
    # Initialise the ZxSensor device using the default address
    zx_sensor = ZxSensor(0x10)
    SensorIsPresent = True
    print "ZX sensor detected"
except Exception as e:
    print "No ZX sensor detected"
    #exception handling code



pygame.init()
pygame.display.set_mode((100, 100))
 
sense = SenseHat()
sense.clear()

TotalTravelledDistance = 0
 
running = True

X = [255, 0, 0]  # Red
O = [255, 255, 255]  # White

question_mark = [
O, O, O, X, X, O, O, O,
O, O, X, O, O, X, O, O,
O, O, O, O, O, X, O, O,
O, O, O, O, X, O, O, O,
O, O, O, X, O, O, O, O,
O, O, O, X, O, O, O, O,
O, O, O, O, O, O, O, O,
O, O, O, X, O, O, O, O
]


X = [0, 0, 0]  # dark
O = [lowWhite, lowWhite, lowWhite]  # low intensity white
x_Crosshead = [
O, X, X, X, X, X, X, O,
X, O, X, X, X, X, O, X,
X, X, O, X, X, O, X, X,
X, X, X, O, O, X, X, X,
X, X, X, O, O, X, X, X,
X, X, O, X, X, O, X, X,
X, O, X, X, X, X, O, X,
O, X, X, X, X, X, X, O
]

if doTests:
    sense.show_message("Test", text_colour = blue, back_colour = yellow)
    sense.show_letter(chr(randint(97, 122)))
    sense.set_rotation(0)
    sleep(0.75)
    sense.set_rotation(90)
    sleep(0.75)
    sense.set_rotation(180)
    sleep(0.75)
    sense.set_rotation(270)
    sleep(0.75)
    sense.set_rotation(0)

    sense.clear(0, 0, 0)

    if mazeType == 1:
        for cnt_lin in range(0,8):
            for cnt_col in range(0,8):
                if maze[cnt_lin][cnt_col] == 1:
                    sense.set_pixel(cnt_col, cnt_lin, lowWhite, lowWhite, lowWhite)
    elif mazeType == 2:
        degreesList = range(0,360,90)
        a = Maze.generate(4,4)
        b  = a._to_str_matrix()
        myR = randint(0, len(degreesList)-1)
        print str(degreesList[myR])
        c = rotate(b, degreesList[myR])
        for cnt_lin in range(0,8):
            for cnt_col in range(0,8):
                #print str(b[cnt_lin][cnt_col])
                if c[cnt_lin][cnt_col] == 'O':
                    sense.set_pixel(cnt_col, cnt_lin, lowWhite, lowWhite, lowWhite)
            

    sleep(5)


    sense.set_pixels(question_mark)
    sleep(0.75)
    sense.clear()  # no arguments defaults to off
    sleep(0.25)
    sense.clear(red)  # passing in an RGB tuple
    sleep(0.25)


##sense.set_pixels(DavidMaze)
##sleep(5)


CursorPosx = randint(0, 7)
CursorPosy = randint(0, 7)

LastPositionsX = deque(numberOfLastPositions * [CursorPosx])
LastPositionsY = deque(numberOfLastPositions * [CursorPosy])
HandZ_prev = 0
HandX_prev = 0

# clear all drawings 
sense.clear(0, 0, 0)

# draw static crosshead (x)
sense.set_pixels(x_Crosshead)

# draw following crosshead (+)
for cnt_col in range(0,8):
    sense.set_pixel(CursorPosx, cnt_col, 0, 0, lowWhite)
for cnt_lin in range(0,8):
    sense.set_pixel(cnt_lin, CursorPosy, 0, 0, lowWhite)
# draw current pos    
sense.set_pixel(CursorPosx, CursorPosy, 255, 255, 255)

# draw target
TargetPosX = randint(0, 7)
TargetPosY = randint(0, 7)
while (TargetPosX == CursorPosx) and (TargetPosY == CursorPosy):
    TargetPosX = randint(0, 7)
    TargetPosY = randint(0, 7)
print "target position is " + str(TargetPosX) + "/" + str(TargetPosY)
sense.set_pixel(TargetPosX, TargetPosY, lowWhite, 0, 0)
sense.set_pixel(CursorPosx, CursorPosy, 255, 255, 255)


## Z+ == Up
## Z- == Down
## X+ == Left
## X- == Right

BLESendEvent(0)
sense.show_letter("3", text_colour = blue, back_colour = yellow)
sleep(1)
sense.show_letter("2", text_colour = blue, back_colour = yellow)
sleep(1)
sense.show_letter("1", text_colour = blue, back_colour = yellow)
sleep(1)
sense.show_message("Go", text_colour = blue, back_colour = yellow)
try :
    start_time = time()
    while running:
        if useHandAsInput:
            if (SensorIsPresent):
##                sense.set_pixel(CursorPosx, CursorPosy,
##                                    0, 0, 0)  # Black 0,0,0 means OFF
                # wait until position is available
                WallHit = 0
                while not (zx_sensor.position_available()):
                    sleep(0.1)
                tempX = zx_sensor.read_x()
                tempZ = zx_sensor.read_z()
                #print str(tempX) + "   /   " +str(tempZ)


                #Update LastPositions
                LastPositionsX.rotate(1) #right shift w/ permutation
                LastPositionsX[0] = CursorPosx
                LastPositionsY.rotate(1) #right shift w/ permutation
                LastPositionsY[0] = CursorPosy

                
                #limit the pos
                HandZ = tempZ
                HandX = tempX
                HandZ = min([tempZ, HandZ_max])
                HandX = min([tempX, HandX_max])
                HandZ = max([tempZ, HandZ_min])
                HandX = max([tempX, HandX_min])
                
                #print "Hand pos " + str(HandX) + "/" + str(HandZ)

                if ZXMode == 1: ## 0 = Absolute,  1 = Relative
                    if (abs(HandZ - HandZ_prev) > deadbandZ) and (abs(HandX - HandX_prev) > deadbandX):
                        #print "Z difference " + str(HandZ - HandZ_prev) + " // X difference " + str(HandX - HandX_prev)
                        if HandZ - HandZ_prev > 0 and CursorPosy < 7:
                            CursorPosy = CursorPosy + 1
                        elif HandZ - HandZ_prev < 0 and CursorPosy > 0:
                            CursorPosy = CursorPosy - 1
                        if HandX - HandX_prev > 0 and CursorPosx < 7:
                            CursorPosx = CursorPosx + 1
                        elif HandX - HandX_prev < 0 and CursorPosx > 0:
                            CursorPosx = CursorPosx - 1
                        TotalTravelledDistance += 1

                elif ZXMode == 0: ## 0 = Absolute,  1 = Relative
                    tempZ = 7-(int(HandZ / ZXdifferencialDividerZ) + ZXdifferencialoffsetZ) #inverted axis
                    tempX = 7-(int(HandX / ZXdifferencialDividerX) + ZXdifferencialoffsetX) #inverted axis

                    if tempZ > 7 or tempZ < 0 or tempX > 7 or tempX < 0:# outside boundaries
                        WallHit = 1
                    else:
                        TotalTravelledDistance += math.sqrt(math.pow(tempZ - CursorPosy,2) + math.pow(tempX - CursorPosx,2) )
                        #BLESendEvent(6)

                    if tempZ <= 7 and tempZ >= 0:
                        CursorPosy = tempZ
                    if tempX <= 7 and tempX >= 0:
                        CursorPosx = tempX
                    
                    
                            
                HandZ_prev = HandZ
                HandX_prev = HandX
                
                # display static crosshead (x)
                sense.set_pixels(x_Crosshead)

                # display following crosshead (+)
                for cnt_col in range(0,8):
                    sense.set_pixel(CursorPosx, cnt_col, 0, 0, lowWhite)
                for cnt_lin in range(0,8):
                    sense.set_pixel(cnt_lin, CursorPosy, 0, 0, lowWhite) 

                # draw LastPositions
                for cnt in range(0,numberOfLastPositions):
                    sense.set_pixel(LastPositionsX[cnt], LastPositionsY[cnt],
                                0, lowWhite_Following[cnt], 0)

                
                #draw target
                sense.set_pixel(TargetPosX, TargetPosY, lowWhite, 0, 0)
                #draw current pos    
                sense.set_pixel(CursorPosx, CursorPosy, 255, 255, 255)

                BLESendTargetCarthesian(CursorPosx, CursorPosy)


                if (CursorPosx == TargetPosX) and (CursorPosy == TargetPosY):
                    EllapsedTime = time() - start_time
                    if EllapsedTime <= PerfectTime:
                        BLESendEvent(2)
                        sense.set_pixel(TargetPosX, TargetPosY, lowWhite, lowWhite, 0)
                    elif EllapsedTime >  BadTime:
                        BLESendEvent(4)
                        for iii in range(0,1):
                            sense.set_pixel(TargetPosX, TargetPosY, 0, 0, 0)
                            sleep(0.25)
                            sense.set_pixel(TargetPosX, TargetPosY, lowWhite, 0, 0)
                            sleep(0.25)
                    else:
                        BLESendEvent(1)
                    print "You are on the target: ellasped time " + str(EllapsedTime) + "s"
                    print "TotalTravelledDistance: " + str(TotalTravelledDistance)
                    TargetPosX = randint(0, 7)
                    TargetPosY = randint(0, 7)
                    while (TargetPosX == CursorPosx) and (TargetPosY == CursorPosy):
                        TargetPosX = randint(0, 7)
                        TargetPosY = randint(0, 7)
                    #draw target
                    sense.set_pixel(TargetPosX, TargetPosY, lowWhite, 0, 0)
                    start_time = time()
                elif WallHit == 1:
                    BLESendEvent(3)



                #sleep(0.1)
            else:
                print "No sensor detected"
                
        else: # use cursor as input
            for event in pygame.event.get():
                if event.type == KEYDOWN:

                    sense.set_pixel(CursorPosx, CursorPosy,
                                    0, 0, 0)  # Black 0,0,0 means OFF

                    # display static crosshead (x)
                    sense.set_pixels(x_Crosshead)

                    #Update LastPositions
                    LastPositionsX.rotate(1) #right shift w/ permutation
                    LastPositionsX[0] = CursorPosx
                    LastPositionsY.rotate(1) #right shift w/ permutation
                    LastPositionsY[0] = CursorPosy
         
                    if event.key == K_DOWN and CursorPosy < 7:
                        CursorPosy = CursorPosy + 1
                        TotalTravelledDistance += 1
                    elif event.key == K_UP and CursorPosy > 0:
                        CursorPosy = CursorPosy - 1
                        TotalTravelledDistance += 1
                    elif event.key == K_RIGHT and CursorPosx < 7:
                        CursorPosx = CursorPosx + 1
                        TotalTravelledDistance += 1
                    elif event.key == K_LEFT and CursorPosx > 0:
                        CursorPosx = CursorPosx - 1
                        TotalTravelledDistance += 1

                    # display following crosshead (+)
                    for cnt_col in range(0,8):
                        sense.set_pixel(CursorPosx, cnt_col,
                                    0, 0, lowWhite)
                    for cnt_lin in range(0,8):
                        sense.set_pixel(cnt_lin, CursorPosy,
                                    0, 0, lowWhite)    

                    #draw LastPositions
                    for cnt in range(0,numberOfLastPositions):
                        sense.set_pixel(LastPositionsX[cnt], LastPositionsY[cnt],
                                    0, lowWhite_Following[cnt], 0)

         
                    #draw target
                    sense.set_pixel(TargetPosX, TargetPosY, lowWhite, 0, 0)
                    #draw current pos    
                    sense.set_pixel(CursorPosx, CursorPosy, 255, 255, 255)

                    if (CursorPosx == TargetPosX) and (CursorPosy == TargetPosY):
                        print "You are on the target"
                        print "TotalTravelledDistance: " + str(TotalTravelledDistance)
                        TargetPosX = randint(0, 7)
                        TargetPosY = randint(0, 7)
                        while (TargetPosX == CursorPosx) and (TargetPosY == CursorPosy):
                            TargetPosX = randint(0, 7)
                            TargetPosY = randint(0, 7)
                        #draw target
                        sense.set_pixel(TargetPosX, TargetPosY, lowWhite, 0, 0)
                
                if event.type == QUIT:
                    running = False
                    print "TotalTravelledDistance: " + str(TotalTravelledDistance)
                    print("BYE")

except KeyboardInterrupt:
    print('Interrupted')
except Exception as e:
    print "Error"
    pygame.display.quit()
    pygame.quit()
    sense.clear(0,0,0)
    raise e

try:
    print subprocess.check_output('hciconfig')
    subprocess.call('sudo hciconfig hci0 down'.split(" ")) #no output
    print subprocess.check_output('hciconfig')
    print 'BLE is down'
except Exception:
    print 'Error while configuring BLE'

pygame.display.quit()
pygame.quit()
sense.clear(0,0,0)
