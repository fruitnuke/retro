'''Dukedom, a more complex game of resource management than Hammurabi, with elements of empire building.

Credits
-------
Original concept by Vince Talbot in 1976, this implementation is based on the BASIC version that appears
in Big Computer Games (1984).

Instructions
------------
- Each peasant requires 13 hectolitres (HL) of grain per year to not starve.
- It takes 2 HL of grain to plant 1 hectare (HA) of land.
- If at the end of the year enough of your peasants have died that your population is reduced to a third
  of what it was at the start of the game, the High King will step in and take away your dukedom due to
  your mismanagement.

Differences from the original
-----------------------------
- Although the instructions in Big Computer Games states that a peasant can care for no more than 4
  hectares of land (when it comes to planting seed), this mechanic does not actually appear to be implmented
  in the BASIC version.
- The BASIC version includes a "partially Gaussian random #" generator, which uses a uniform random number
  generator to produce numbers with a probability density function that (seems to very loosely) approximate
  that of a normal function. Python has a (couple of) random number generator(s) with normal distribution built
  in so I just use that. Then it's just working out the mean and standard deviation for each bell curve that Talbot
  intended.
'''

import random


def dukedom():
    peasants = 100
    grain    = 4177 # Hectolitres
    land     = 600  # Hectares
    year     = 1

    while True:
        print('\nYear {} Peasants {} Land {} Grain {}\n'.format(year, peasants, land, grain))

        # Test for end game
        if peasants < 33:
            print('You have so few peasants left that\n'
                  'the High King has abolished your Ducal\n'
                  'right.\n')
            break

        # Food for peasants
        while True:
            food = prompt_int('Grain for food = ')
            if food <= grain:
                break
            print('But you don\'t have enough grain.\nYou only have {}HL. of grain left.\n'.format(grain))
        grain -= food

        # Farm the land
        while True:
            farmed = prompt_int('Land to be planted = ')
            if farmed > land:
                print('But you don\'t have enough land.\nYou only have {}HA. of land left.\n'.format(land))
            elif (farmed * 2) > grain:
                print('But you don\'t have enough grain.\n'
                      'You only have {}HL. of grain left.\n'
                      'Enough to plant {}HA. of land\n'.format(grain, int(grain / 2)))
            elif (peasants * 4) > land:
                print('But you don\'t have enough peasants to farm that land.\n'
                      'You only have enough to farm {} HA. of land.'.format(int(peasants / 4)))
            else:
                break
        grain -= (farmed * 2)

        crop_yld = min(13, max(4, int(round(random.gauss(8.5, 1.5)))))
        print('Yield = {} HL/HA.'.format(crop_yld))

        year  += 1
        grain += crop_yld * farmed

        food_per_capita = int(food / peasants)
        if food_per_capita < 13:
            print('Some peasants have starved.')
            peasants -= peasants - int(food / 13)


def prompt_int(msg):
    while True:
        try:
            val = int(input(msg))
        except ValueError:
            continue
        if val >= 0:
            return val


def prompt_key(msg, keys):
    while True:
        val = input(msg).lower()
        if val in keys:
            return val


if __name__ == '__main__':
    while True:
        dukedom()
        if prompt_key('Do you wish to play again? ', 'yn') == 'n':
            break