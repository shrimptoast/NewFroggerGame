__author__ = 'annadecker'   # test

# Import library
import pygame, random
from pygame.locals import *

# RGB colors
#            R    G    B
GRAY     = (100, 100, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
YELLOW   = (255, 204,   0)

# Initialize the game constants
SCREENWIDTH, SCREENHEIGHT = 1000, 800
NUMLANES = 5
LANEWIDTH = 100
CARWIDTH = 50
LINEWIDTH = 5
LINECOLOR = YELLOW
ROADCOLOR = GRAY
GRASSWIDTH = 100


pygame.init()
pygame.mixer.init()

splat = pygame.mixer.Sound("resources/audio/splat.wav")
frog = pygame.mixer.Sound("resources/audio/frog02.wav")
beep = pygame.mixer.Sound("resources/audio/beep.wav")
buzz = pygame.mixer.Sound("resources/audio/buzz02.wav")
yippie = pygame.mixer.Sound("resources/audio/yippie.wav")
slurp = pygame.mixer.Sound("resources/audio/slurp.wav")

splat.set_volume(0.50)
frog.set_volume(0.25)
beep.set_volume(0.50)
buzz.set_volume(0.50)
yippie.set_volume(0.50)
slurp.set_volume(0.50)

# Load images
imgCurrentFrog = pygame.image.load('resources/images/frogSitting.png')
imgGrass = pygame.image.load('resources/images/grass2.png')
imgDeadFrog = pygame.image.load('resources/images/deadFrog.png')
imgCar = pygame.image.load('resources/images/purpleCar.png')
imgJumpingFrog = pygame.image.load('resources/images/frogJumping.png')
imgYummyBug = pygame.image.load('resources/images/yummyBug.png')
imgFrogStriking = pygame.image.load('resources/images/frogStriking.png')

# Initialize game variables
frogStartPosition = [100,GRASSWIDTH-50]
currentFrogPos = frogStartPosition

lanes = []
cars = []
deadFrogs = []
yummyBugs = []
carStartPositions = []

yummyBugScore = 0

DISPLAYSURF = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Frogger Game')


 # Determine where to draw road and yellow lines
topOfLane = GRASSWIDTH
roadWidth = NUMLANES * (LANEWIDTH + LINEWIDTH)
road = pygame.Rect(0, GRASSWIDTH, SCREENWIDTH, roadWidth)

txtWhat = ''

# Create array of car start positions, one for each lane
for carPos in range(NUMLANES):
    carStartPositions.append(topOfLane + ((LANEWIDTH-CARWIDTH)/2))
    topOfLane += (LANEWIDTH+LINEWIDTH)

# Some debugging text
font = pygame.font.Font(None, 44)
debugText = font.render(txtWhat, 0, WHITE, RED)
textRect = debugText.get_rect()
textRect.topright=[SCREENWIDTH-5,5]

# Some more variables
exitCode = 0
collision = False
gotTheBug = False
frogJumpTimer = 0
frogDirection = 'S'
carTimer = 40
bugTimer = 30
frogStrikeTimer = 0

# Main game loop
while exitCode == 0:
    # Increment the timers
    carTimer -= 1
    bugTimer -= 1
    frogJumpTimer -= 1
    frogStrikeTimer -= 1

    # Clear screen before drawing again
    DISPLAYSURF.fill(0)

    # Draw grass background
    for x in range(SCREENWIDTH/imgGrass.get_width()+1):
        for y in range(SCREENHEIGHT/imgGrass.get_height()+1):
            DISPLAYSURF.blit(imgGrass,(x*imgGrass.get_width(),y*imgGrass.get_width()))

    # Draw Road
    pygame.draw.rect(DISPLAYSURF, ROADCOLOR, road)

    # Draw yellow lines on road
    topOfLane = GRASSWIDTH # Reset
    for l in range(NUMLANES-1):
        pygame.draw.rect(DISPLAYSURF, LINECOLOR, (0, (GRASSWIDTH+(l+1)*(LANEWIDTH+LINEWIDTH)), SCREENWIDTH, LINEWIDTH))
        topOfLane += (LANEWIDTH+LINEWIDTH)


    # Release a new car?
    if carTimer == 0:
        carTimer = random.randint(100,100)
        myRandomNum = random.randint(0,NUMLANES-1)
        cars.append([1000,carStartPositions[myRandomNum]])
        beep.play()

    # Get the frog's current coordinates in the form of a rectangle
    frogRect = pygame.Rect(imgCurrentFrog.get_rect())
    frogRect.left = currentFrogPos[0]
    frogRect.top = currentFrogPos[1]

    # Check for collisions between frog and cars
    for car in cars:
        carRect = pygame.Rect(imgCar.get_rect())
        carRect.left = car[0]
        carRect.top =car[1]
        if frogRect.colliderect(carRect):
            deadFrogs.append((currentFrogPos[0],currentFrogPos[1]))
            splat.play()
            collision = True

    # Release a new bug?
    if bugTimer == 0:
        buzz.play()
        bugTimer = random.randint(10,50)
        bugStartX = random.randint(0,SCREENWIDTH)
        bugStartY = random.randint(0,SCREENHEIGHT)
        bugFlightTimer = random.randint(30,90)
        yummyBugs.append([bugStartX,bugStartY,bugFlightTimer,False])

    # Move all flying bugs, land them if their timer is expired
    bugIndex = 0
    for bug in yummyBugs:
        # Increment the bug's timer
        bug[2] -= 1

        # Check whether bug is landed
        if not bug[3]: # The bug is in flight
            # Get some random numbers to determine flight path x and y
            bugRandX = random.randint(-20,20)
            bugRandY = random.randint(-20,20)
            bug[0] += bugRandX
            bug[1] += bugRandY
            if bug[2] == 0:
                bug[3] = True
                bug[2] = random.randint(30,90)
        else: # The bug is landed
            # Make the bug fly again if its timer is expired
            if bug[2] == 0:  # Bug timer expired, time to fly again
                bug[3] = False
                # Reset the timer
                bug[2] = random.randint(30,90)

        # Check whether the bug has left the building
        if bug[0] < 0 or bug[0] > SCREENWIDTH or bug[1] < 0 or bug[1] > SCREENHEIGHT:
            yummyBugs.pop(bugIndex)

        # Check for collisions between frog and landed bugs
        if bug[3] == True: # Frog can only eat landed bugs
            bugRect = pygame.Rect(imgYummyBug.get_rect())
            bugRect.left = bug[0]
            bugRect.top =bug[1]
            if frogRect.colliderect(bugRect):
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                       if event.key == K_SPACE: # Frog is striking
                            gotTheBug = True
                            yippie.play()
                            yummyBugs.pop(bugIndex)  # Erase the evidence

        # Increment the bug index
        bugIndex += 1

    # Draw dead frogs
    if len(deadFrogs) > 0:
        for dead in deadFrogs:
            DISPLAYSURF.blit(imgDeadFrog, dead)

     # Draw cars
    index=0
    for car in cars:
        # If car has gone off screen, delete it
        if car[0]<-50:
            cars.pop(index)
        car[0]-=5
        index+=1
    for car in cars:
        DISPLAYSURF.blit(imgCar, car)


    # Draw bugs
    if len(yummyBugs) > 0:
        for bug in yummyBugs:
            DISPLAYSURF.blit(imgYummyBug, (bug[0],bug[1]))

    # Point frog in the correct direction
    frogAngle = 0
    if frogDirection == 'N':
        frogAngle = 180
    elif frogDirection == 'E':
        frogAngle = 90
    elif frogDirection == 'W':
        frogAngle = 270

    # Move frog back to start if collision!
    if collision:
        currentFrogPos[1] = GRASSWIDTH-50
        frogDirection = 'S'
        frogJumpTimer = 0
        collision = False


    # Check frogJumpTimer
    if frogJumpTimer <= 0 and frogStrikeTimer <= 0:
        imgCurrentFrog = pygame.image.load('resources/images/frogSitting.png')

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit(0)
        # Check whether the down arrow was clicked... if so, advance the current frog
        if event.type == pygame.KEYDOWN:
            frogMove = False
            if event.key==K_DOWN:
                currentFrogPos[1] += 200
                frogDirection = 'S'
                frogMove = True
            if event.key==K_UP:
                currentFrogPos[1] -= 200
                frogDirection = 'N'
                frogMove = True
            if event.key==K_LEFT:
                currentFrogPos[0] -= 200
                frogDirection = 'W'
                frogMove = True
            if event.key==K_RIGHT:
                currentFrogPos[0] += 200
                frogDirection = 'E'
                frogMove = True
            if event.key==K_SPACE:
                slurp.play()
                frogStrikeTimer = 3
                imgCurrentFrog = pygame.image.load('resources/images/frogStriking.png')

            if frogMove:
                frog.play()  # ribbet!
                frogJumpTimer = 3
                imgCurrentFrog = pygame.image.load('resources/images/frogJumping.png')

    # Draw the current frog facing the correct direction
    frogSurf = pygame.transform.rotate(imgCurrentFrog, frogAngle)
    DISPLAYSURF.blit(frogSurf, currentFrogPos)
    DISPLAYSURF.blit(debugText, textRect)

    # Update the screen
    pygame.display.flip()
