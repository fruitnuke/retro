"""Hunt the Wumpus

http://www.atariarchives.org/morebasicgames/showpage.php?page=179
"""

import random

cave = {
    1:  (2,5,8),
    2:  (1,3,10),
    3:  (2,4,12),
    4:  (3,5,14),
    5:  (1,4,6),
    6:  (5,7,15),
    7:  (6,8,17),
    8:  (1,7,9),
    9:  (8,10,18),
    10: (2,9,11),
    11: (10,12,19),
    12: (3,11,13),
    13: (12,14,20),
    14: (4,13,15),
    15: (6,14,16),
    16: (15,17,20),
    17: (7,16,18),
    18: (9,17,19),
    19: (11,18,20),
    20: (13,16,19)}

# TODO: Not spawn things in the same location
# do not start in a location with something else in it
# handle invalid input


def hunt_the_wumpus():
    wumpus = random.randrange(0, 21)
    hunter = random.randrange(0, 21)
    bats   = [random.randrange(0, 21) for _ in range(2)]
    pits   = [random.randrange(0, 21) for _ in range(2)]
    arrows = 5

    while True:
        neighbouring_caves = cave[hunter]
        if wumpus in neighbouring_caves:
            print 'I smell a wumpus!'
        if any(bat in neighbouring_caves for bat in bats):
            print 'Bats nearby!'
        if any(pit in neighbouring_caves for pit in pits):
            print 'I feel a draught.'
        print 'You are in a room', hunter
        print 'Tunnels lead to {0}, {1}, {2}'.format(*neighbouring_caves)

        command = raw_input('Shoot or Move (s-m)? ').lower()

        if command == 'q':
            break

        if command == 'm':
            hunter = int(raw_input('Where to? '))
            if hunter in bats:
                print 'Zap -- super bat snatch! Elsewhereville for you!'
                hunter = random.randrange(0, 21)
            elif hunter in pits:
                print 'YYYIIIIEEEE... fell in pit'
                return
            elif hunter == wumpus:
                print 'Tsk, tsk, tsk - Wumpus got you!'
                return

        elif command.lower() == 's':
            n = int(raw_input('No. of rooms (1-5)? '))
            path = []
            while len(path) < n:
                room = int(raw_input('Room #? '))
                if (len(path) == 1 and room == hunter) or (len(path) > 1 and room == path[-2]):
                    print 'Arrows aren\'t that crooked - try another room'
                else:
                    path.append(room)
            curr = hunter
            for room in path:
                if room in cave[curr]:
                    if room == hunter:
                        print 'Ouch! Arrow got you!'
                        return
                    if room == wumpus:
                        print 'Aha! You got the wumpus!'
                        return
                    curr = room
                else:
                    curr = random.choice(cave[curr])

            arrows -= 1
            if not arrows:
                return

            wumpus_moves = random.random() > 0.75
            if wumpus_moves:
                wumpus = random.choice(cave[wumpus])
                if hunter == wumpus:
                    print 'Tsk, tsk, tsk - wumpus got you!'
                    return

        print

if __name__ == '__main__':
    hunt_the_wumpus()