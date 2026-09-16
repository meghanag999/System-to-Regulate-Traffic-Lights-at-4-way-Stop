import random
import time
import threading
import pygame
import sys



####### defining the constants
speed = {'person': 2.6,'car': 2.5}

## cars
directionNums = {0:'up', 1:'right', 2:'down', 3:'left'}
# starting car coordinates
x = {'up': 420, 'right': 1000, 'down': 540, 'left': 0}
y = {'up': 0, 'right': 420, 'down': 1000, 'left': 540}
stopLines = {'up': 280, 'right': 700, 'down': 690, 'left': 280}
turnLines = {'up': {'left': 410, 'right': 550},
             'right': {'up': 550, 'down': 410},
             'down': {'left': 410, 'right': 550},
             'left': {'up': 550, 'down': 410}}

## pedestrians
pedsDirections = {'northWest': {0: 'right', 1: 'down'},
                  'northEast': {0: 'left', 1: 'down'},
                  'southEast': {0: 'left', 1: 'up'},
                  'southWest': {0: 'right', 1: 'up'}}

pedStartPoints = {0: 'northWest', 1: 'northEast', 2: 'southEast', 3: 'southWest'}
pedStartCoords = {'northWest': (320, 340),
                  'northEast': (640, 320),
                  'southEast': (660, 620),
                  'southWest': (340, 640)}

## signals
signalPoints = [(200, 210), (670, 210), (670, 675), (200, 675)]
greenSignalTime = 12
yellowSignalTime = 2
redSignalTime = 14

####### global state
signals = []
currentGreen = 0  #north/south
nextGreen = 1  #west/east
stoppingGap = 25
yellowFlag = False
carTurned = {'up': [], 'right': [], 'down': [], 'left': []}
carNotTurned = {'up': [], 'right': [], 'down': [], 'left': []}

### initialize pygame
pygame.init()
simulateCars = pygame.sprite.Group()
simulatePeds = pygame.sprite.Group()

pedsInNCW = set()
pedsInECW = set()
pedsInSCW = set()
pedsInWCW = set()

#######################################

#defining helper methods
def northCWEmpty():
    return len( pedsInNCW ) == 0
def eastCWEmpty():
    return len( pedsInECW ) == 0
def southCWEmpty():
    return len( pedsInSCW ) == 0
def westCWEmpty():
    return len( pedsInWCW ) == 0

def isWEmpty(crosswalk_set):
    return len(crosswalk_set) == 0

class Pedestrian(pygame.sprite.Sprite):
    def __init__(self, startNum: int, id: int):
        pygame.sprite.Sprite.__init__(self)
        self.startingPoint = pedStartPoints[startNum]
        self.movingDirection = pedsDirections[ self.startingPoint ] [ random.randint ( 0, 1 ) ]
        self.points = pedStartCoords[self.startingPoint]
        self.x = self.points[0]
        self.y = self.points[1]
        self.image = pygame.transform.scale(pygame.image.load('images/peds.png'), (30, 30))
        self.speed = speed['person']
        self.id = id
        simulatePeds.add(self)

    def render(self, screen: pygame.surface.Surface):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        start_position = self.startingPoint
        start_x, start_y = pedStartCoords[ start_position ]

        if self.movingDirection == 'right' and (currentGreen == 1 or self.x > start_x):
            self.x += self.speed
            crosswalk_set = pedsInNCW
        elif self.movingDirection == 'left' and (currentGreen == 1 or self.x < start_x):
            self.x -= self.speed
            crosswalk_set = pedsInSCW
        elif self.movingDirection == 'down' and (currentGreen == 0 or self.y > start_y):
            self.y += self.speed
            crosswalk_set = pedsInWCW
        elif self.movingDirection == 'up' and (currentGreen == 0 or self.y < start_y):
            self.y -= self.speed
            crosswalk_set = pedsInECW
        else :
            return
        crosswalk_set.add(self.id)
        if (
                (self.movingDirection == 'right' and self.x > pedStartCoords['northEast'][0]) or
                (self.movingDirection == 'left' and self.x < pedStartCoords['southWest'][0]) or
                (self.movingDirection == 'down' and self.y > pedStartCoords['southWest'][1]) or
                (self.movingDirection == 'up' and self.y < pedStartCoords['northEast'][1])
        ):
            simulatePeds.remove(self)
            crosswalk_set.remove(self.id)


def generatePedestrians(max_pedestrians=100):
    count = 1
    while count <= max_pedestrians:
        Pedestrian(random.randint(0, 3), count)
        count += 1
        time.sleep(3)


###### Traffic Signal Class
class TrafficSignal:
    def __init__(self, redDuration: int, yellowDuration: int, greenDuration: int):
        self.redDuration = redDuration
        self.yellowDuration = yellowDuration
        self.greenDuration = greenDuration
        self.text = ''





###### Car Class
class Car(pygame.sprite.Sprite):
    def __init__(self, startingDirNum: int):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed['car']
        self.startingLoc = directionNums[startingDirNum ]
        validIndices = [i for i in range(len(directionNums)) if i != startingDirNum]
        self.destinationDirection = directionNums[validIndices[random.randint(0, 2)]]
        self.x = x[self.startingLoc ]
        self.y = y[self.startingLoc ]
        self.image = pygame.transform.scale(pygame.image.load('images/cars.png'), (40, 40))
        self.speed = speed['car']
        simulateCars.add(self)

    def render(self, screen: pygame.surface.Surface):
            screen.blit(self.image, (self.x, self.y))

    def check_collision ( self ) :
        colliding_sprites = pygame.sprite.spritecollide (self, simulateCars, False )
        return len ( colliding_sprites ) > 1


    ##car moving helper methods
    def move_down_from_up(instance):
        if (currentGreen == 0 or ((yellowFlag or currentGreen != 0) and instance.y < stopLines['up'])
                or instance.y > stopLines['up']):
            if ((instance.y == stopLines['up'] and not northCWEmpty()) or (
                    instance.y < stopLines['down'] - 100 and not southCWEmpty())):
                pass
            else:
                instance.y += instance.speed


    def move_left_from_up(instance):
        if (instance.x < stopLines['left'] + 100 and instance.y == turnLines['up']['left']):
            instance.x -= instance.speed
        elif (instance.y == turnLines['up']['left']):
            if (instance.x > stopLines['left'] + 100 or (
                    instance.x == stopLines['left'] + 100 and westCWEmpty())):
                instance.x -= instance.speed
        elif ((currentGreen == 0 and instance.y < turnLines['up']['left'])
              or ((yellowFlag or currentGreen != 0) and instance.y < stopLines['up'])
              or (instance.y > stopLines['up'] and instance.y < turnLines['up']['left'])):
            if (instance.y == stopLines['up'] and not northCWEmpty()):
                pass
            else:
                instance.y += instance.speed

    def move_right_from_up(instance):
        if (instance.x > stopLines['right'] - 100 and instance.y == turnLines['up']['right']):
            instance.x += instance.speed
        elif (instance.y == turnLines['up']['right']):
            if (instance.x < stopLines['right'] - 100 or (
                    instance.x == stopLines['right'] - 100 and eastCWEmpty())):
                instance.x += instance.speed
        elif ((currentGreen == 0 and instance.y < turnLines['up']['right'])
              or ((yellowFlag or currentGreen != 0) and instance.y < stopLines['up'])
              or (instance.y > stopLines['up'] and instance.y < turnLines['up']['right'])):
            if (instance.y == stopLines['up'] and not northCWEmpty()):
                pass
            else:
                instance.y += instance.speed

    def move_up_from_down(instance):
        if (currentGreen == 0
                or ((yellowFlag or currentGreen != 0) and instance.y > stopLines['down'])
                or instance.y < stopLines['down']):
            if ((instance.y == stopLines['down'] and not southCWEmpty()) or (
                    instance.y > stopLines['up'] + 100 and not northCWEmpty())):
                pass
            else:
                instance.y -= instance.speed

    def move_left_from_down(instance):
        if (instance.x < stopLines['left'] + 100 and instance.y == turnLines['up']['left']):
            instance.x -= instance.speed
        elif (instance.y == turnLines['up']['left']):
            if (instance.x > stopLines['left'] + 100 or (instance.x == stopLines['left'] + 100 and westCWEmpty())):
                instance.x -= instance.speed
        elif ((currentGreen == 0 and instance.y > turnLines['down']['left'])
              or ((yellowFlag or currentGreen != 0) and instance.y > stopLines['down'])
              or (instance.y < stopLines['down'] and instance.y > turnLines['down']['left'])):
            if (instance.y == stopLines['down'] and not southCWEmpty()):
                pass
            else:
                instance.y -= instance.speed

    def move_right_from_down(instance):
        if (instance.x > stopLines['right'] - 100 and instance.y == turnLines['up']['right']):
            instance.x += instance.speed
        elif (instance.y == turnLines['up']['right']):
            if (instance.x < stopLines['right'] - 100 or (
                    instance.x == stopLines['right'] - 100 and eastCWEmpty())):
                instance.x += instance.speed
        elif ((currentGreen == 0 and instance.y > turnLines['down']['right'])
              or ((yellowFlag or currentGreen != 0) and instance.y > stopLines['down'])
              or (instance.y < stopLines['down'] and instance.y > turnLines['down']['right'])):
            if (instance.y == stopLines['down'] and not southCWEmpty()):
                pass
            else:
                instance.y -= instance.speed

    def move_right_from_left(instance):
        if (currentGreen == 1
                or ((yellowFlag or currentGreen != 1) and instance.x < stopLines['left'])
                or instance.x > stopLines['left']):
            if ((instance.x == stopLines['left'] and not westCWEmpty()) or (
                    instance.x < stopLines['right'] - 100 and not eastCWEmpty())):
                pass
            else:
                instance.x += instance.speed

    def move_up_from_left(instance):
        if (instance.y < stopLines['up'] + 100 and instance.x == turnLines['left']['up']):
            instance.y -= instance.speed
        elif (instance.x == turnLines['left']['up']):
            if (instance.y > stopLines['up'] + 100 or (instance.y == stopLines['up'] + 100 and northCWEmpty())):
                instance.y -= instance.speed
        elif ((currentGreen == 1 and instance.x < turnLines['left']['up'])
              or ((yellowFlag or currentGreen != 1) and instance.x < stopLines['left'])
              or (instance.x > stopLines['left'] and instance.x < turnLines['left']['up'])):
            if (instance.x == stopLines['left'] and not westCWEmpty()):
                pass
            else:
                instance.x += instance.speed

    def move_down_from_left(instance):
        if (instance.y > stopLines['down'] - 100 and instance.x == turnLines['left']['down']):
            instance.y += instance.speed
        elif (instance.x == turnLines['left']['down']):
            if (instance.y < stopLines['down'] - 100 or (instance.y == stopLines['down'] - 100 and southCWEmpty())):
                instance.y += instance.speed
        elif ((currentGreen == 1 and instance.x < turnLines['left']['down'])
              or ((yellowFlag or currentGreen != 1) and instance.x < stopLines['left'])
              or (instance.x > stopLines['left'] and instance.x < turnLines['left']['down'])):
            if (instance.x == stopLines['left'] and not westCWEmpty()):
                pass
            else:
                instance.x += instance.speed

    def move_left_from_right(instance):
        if (currentGreen == 1
                or ((yellowFlag or currentGreen != 1) and instance.x > stopLines['right'])
                or instance.x < stopLines['right']):
            if ((instance.x == stopLines['right'] and not eastCWEmpty()) or (
                    instance.x > stopLines['left'] + 100 and not westCWEmpty())):
                pass
            else:
                instance.x -= instance.speed

    def move_up_from_right(instance):
        if (instance.y < stopLines['up'] + 100 and instance.x == turnLines['left']['up']):
            instance.y -= instance.speed
        elif (instance.x == turnLines['left']['up']):
            if (instance.y > stopLines['up'] + 100 or (instance.y == stopLines['up'] + 100 and northCWEmpty())):
                instance.y -= instance.speed
        elif ((currentGreen == 1 and instance.x > turnLines['right']['up'])
              or ((yellowFlag or currentGreen != 1) and instance.x > stopLines['right'])
              or (instance.x < stopLines['right'] and instance.x > turnLines['right']['up'])):
            if (instance.x == stopLines['right'] and not eastCWEmpty()):
                pass
            else:
                instance.x -= instance.speed

    def move_down_from_right(instance):
        if (instance.y > stopLines['down'] - 100 and instance.x == turnLines['left']['down']):
            instance.y += instance.speed
        elif (instance.x == turnLines['left']['down']):
            if (instance.y < stopLines['down'] - 100 or (instance.y == stopLines['down'] - 100 and southCWEmpty())):
                instance.y += instance.speed
        elif ((currentGreen == 1 and instance.x > turnLines['right']['down'])
              or ((yellowFlag or currentGreen != 1) and instance.x > stopLines['right'])
              or (instance.x < stopLines['right'] and instance.x > turnLines['right']['down'])):
            if (instance.x == stopLines['right'] and not eastCWEmpty()):
                pass
            else:
                instance.x -= instance.speed

    def move_up(instance):
        if (instance.destinationDirection == 'down'):
            instance.move_down_from_up()
        elif (instance.destinationDirection == 'right'):
            instance.move_right_from_up()
        else:  # dest is left
            instance.move_left_from_up()

    def move_down(instance):
        if (instance.destinationDirection == 'up'):
            instance.move_up_from_down()
        elif (instance.destinationDirection == 'right'):
            instance.move_right_from_down()
        else:  # dest is left
            instance.move_left_from_down()

    def move_left(instance):
        if (instance.destinationDirection == 'right'):
            instance.move_right_from_left()
        elif (instance.destinationDirection == 'up'):
            instance.move_up_from_left()
        else:  # dest is down
            instance.move_down_from_left()

    def move_right(instance):
        if (instance.destinationDirection == 'left'):
            instance.move_left_from_right()
        elif (instance.destinationDirection == 'up'):
            instance.move_up_from_right()
        else:  # dest is down
            instance.move_down_from_right()
    def move(self):
        if self.startingLoc == 'up':
            self.move_up()
        elif self.startingLoc == 'right':
            self.move_right()
        elif self.startingLoc == 'down':
            self.move_down()
        else:  # moves left
            self.move_left()



def generateCars():
    while (True):
        Car(random.randint(0, 3))
        time.sleep(3)


def initializeSignals():
    signal = TrafficSignal(redSignalTime, yellowSignalTime, greenSignalTime)
    global signals
    signals = [signal, signal, signal, signal]
    simulate()


def simulate():
    global currentGreen, yellowFlag, nextGreen
    while (signals[currentGreen].greenDuration > 0):
        updateSignals()
        time.sleep(1)

    yellowFlag = True

    while (signals[currentGreen].yellowDuration > 0):
        updateSignals()
        time.sleep(1)

    yellowFlag = False
    signals[currentGreen].greenDuration = greenSignalTime
    signals[currentGreen].yellowDuration = yellowSignalTime
    signals[currentGreen].redDuration = redSignalTime
    temp = currentGreen
    currentGreen = nextGreen
    nextGreen = temp
    simulate()


def updateSignals():
    for i in range(0, 2):
        if (i == currentGreen):
            if (not yellowFlag):
                signals[i].greenDuration -= 1
            else:
                signals[i].yellowDuration -= 1
        else:
            signals[i].redDuration -= 1


def main():
    background = pygame.image.load('images/intersection5.png')
    screenSize = (1000, 1000)
    screen = pygame.display.set_mode(size=screenSize)

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    signalThread = threading.Thread(name="init", target=initializeSignals, args=())
    signalThread.daemon = True
    signalThread.start()

    # generate cars
    carThread = threading.Thread(name="generateCars", target=generateCars, args=())
    carThread.daemon = True
    carThread.start()

    # generate pedestrians
    pedestrianThread = threading.Thread(name="generatePedestrians", target=generatePedestrians, args=())
    pedestrianThread.daemon = True
    pedestrianThread.start()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        font = pygame.font.Font(None, 30)
        screen.blit(background, (0, 0))  # display background in simulation

        for i in range(0, 2):
            # display signal
            if (i == currentGreen):
                if (yellowFlag):
                    signals[i].text = signals[i].yellowDuration
                    signals[i + 2].text = signals[i + 2].yellowDuration
                    screen.blit(yellowSignal, signalPoints[i ])
                    screen.blit(yellowSignal, signalPoints[ i + 2 ])
                else:
                    signals[i].text = signals[i].greenDuration
                    signals[i + 2].text = signals[i + 2].greenDuration
                    screen.blit(greenSignal, signalPoints[i ])
                    screen.blit(greenSignal, signalPoints[ i + 2 ])
            else:
                signals[i].text = signals[i].redDuration
                signals[i + 2].text = signals[i + 2].redDuration
                screen.blit(redSignal, signalPoints[i ])
                screen.blit(redSignal, signalPoints[ i + 2 ])



        # display cars
        for car in simulateCars:
            car.render(screen)
            car.move()

        # display pedestrians
        for pedestrian in simulatePeds:
            pedestrian.render(screen)
            pedestrian.move()

        pygame.display.update()
        clock.tick(60)


main()
pygame.quit()
sys.exit()