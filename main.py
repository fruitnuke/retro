"""Hunt the Wumpus

http://www.atariarchives.org/morebasicgames/showpage.php?page=179

- Bugs (in the original game also):
  - You can repeatedly put the same room for the arrow
  - No range checking on the input for rooms for the arrow
"""

from copy import deepcopy
import random
import textwrap


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


instructions = textwrap.dedent("""
    Welcome to 'Hunt the Wumpus'.

    The wumpus lives in a cave of 20 rooms. Each room has 3 tunnels
    leading to other rooms. (Look at a dodecahedron to see how this works
    - if you don't know what a dodecahedron is, ask someone).

    Hazards:
       Bottomless Pits - two rooms have bottomless pits in them. If you go
          there, you fall into the pit (and lose!)

       Super Bats - two other rooms have super bats. If you go there, a
          bat grabs you and takes you to some other room at random (which
          might be troublesome).

    Wumpus:
       The wumpus is not bothered by the hazards (he has sucker feet and
       is too big for a bat to lift).  Usually he is asleep. Two things
       wake him up: your entering his room or your shooting an arrow.

       If the wumpus wakes, he moves (p=.75) one room or stays still
       (p=.25). After that, if he is where you are, he eats you up (and you
       lose!)

    You:
       Each turn you may move or shoot a crooked arrow.

       Moving: you can go one room (through one tunnel).

       Arrows: you have 5 arrows. you lose when you run out.  Each arrow
          can go from 1 to 5 rooms.  You aim by telling the computer the
          room #s you want the arrow to go to.  If the arrow can't go that
          way (ie no tunnel) it moves at random to the next room.  If the
          arrow hits the wumpus, you win.  If the arrow hits you, you
          lose.

    Warnings:
       When you are one room away from the wumpus or a hazard, the computer
       says:

       Wumpus - 'I smell a wumpus'
       Bat    - 'Bats nearby'
       Pit    - 'I feel a draft'""")


class GameState:

    def __init__(self):
        rooms = range(1, 21)
        random.shuffle(rooms)
        spawn = iter(rooms)
        self.wumpus = spawn.next()
        self.hunter = spawn.next()
        self.bats   = [spawn.next() for _ in range(2)]
        self.pits   = [spawn.next() for _ in range(2)]
        self.arrows  = 5
        self.playing = True
        self.won     = False


def prompt(msg, keys=None):
    """Prompt the player for char input, optionally restricted to a set of chars."""
    if keys:
        msg += ' ({0})'.format('-'.join(c for c in keys))
    while True:
        val = raw_input(msg + '? ').lower()
        if val in keys or not keys:
            return val


def prompt_int(msg, rng=None):
    """Prompt the player for numeric input, optionally between a given [min, max] range (inclusive)."""
    if rng:
        msg += ' ({0}-{1})'.format(*rng)
    while True:
        try:
            val = int(raw_input(msg + '? '))
            if (rng and rng[0] <= val <= rng[1]) or not rng:
                return val
        except ValueError:
            pass


def move_wumpus(game):
    if random.random() > 0.25:
        game.wumpus = random.choice(cave[game.wumpus])


def hunt_the_wumpus():
    quitting  = False
    last_game = None
    reset     = True

    if prompt('Instructions', 'yn') == 'y':
        print instructions

    while not quitting:
        if reset:
            game = GameState()
            last_game = deepcopy(game)
        else:
            game = deepcopy(last_game)

        playing = True
        won     = False

        print
        print 'Hunt the Wumpus'
        print

        while playing:
            neighbouring_caves = cave[game.hunter]
            if game.wumpus in neighbouring_caves:
                print 'I smell a wumpus!'
            if any(bat in neighbouring_caves for bat in game.bats):
                print 'Bats nearby!'
            if any(pit in neighbouring_caves for pit in game.pits):
                print 'I feel a draught.'
            print 'You are in room', game.hunter
            print 'Tunnels lead to {0}, {1}, {2}'.format(*neighbouring_caves)

            command = prompt('Shoot, Move or Quit', 'smq')

            if command == 'q':
                playing = False
                quitting = True

            if command == 'm':
                while True:
                    to = prompt_int('Where to')
                    if to in neighbouring_caves:
                        game.hunter = to
                        break
                    else:
                        print 'Not possible -'

                if game.hunter in game.bats:
                    print 'Zap -- super bat snatch! Elsewhereville for you!'
                    game.hunter = random.randrange(0, 21)
                elif game.hunter in game.pits:
                    print 'YYYIIIIEEEE... fell in pit'
                    playing = False
                elif game.hunter == game.wumpus:
                    print '... oops! Bumped a wumpus'
                    move_wumpus(game)
                    if game.hunter == game.wumpus:
                        print 'Tsk, tsk, tsk - Wumpus got you!'
                        playing = False

                print

            elif command.lower() == 's':
                n = prompt_int('No. of rooms', [1, 5])
                path = []
                while len(path) < n:
                    room = prompt_int('Room')
                    if (len(path) == 1 and room == game.hunter) or (len(path) > 1 and room == path[-2]):
                        print 'Arrows aren\'t that crooked - try another room'
                    else:
                        path.append(room)

                curr = game.hunter
                for room in path:
                    if room in cave[curr]:
                        if room == game.hunter:
                            print 'Ouch! Arrow got you!'
                            playing = False
                            break
                        elif room == game.wumpus:
                            print 'Aha! You got the wumpus!'
                            playing = False
                            won = True
                            break
                        curr = room
                    else:
                        curr = random.choice(cave[curr])
                else:
                    print 'Missed'

                if not won:
                    game.arrows -= 1
                    if not game.arrows:
                        playing = False

                    move_wumpus(game)
                    if game.hunter == game.wumpus:
                        print 'Tsk, tsk, tsk - wumpus got you!'
                        playing = False

                print

        if not quitting:
            if won:
                print 'Hee hee hee - the Wumpus\'ll getcha next time!!'
            else:
                print 'Ha ha ha - you lose!'

            reset = prompt('Same set-up', 'yn') == 'n'
            print


if __name__ == '__main__':
    hunt_the_wumpus()
