'''Dukedom, a more complex game of resource management than Hammurabi, with elements of empire building.

Credits
-------
Original concept by Vince Talbot in 1976, my implementation is based on the BASIC version that appears
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


def main():
    while True:
        dukedom()
        if prompt_key('Do you wish to play again? ', 'yn') == 'n':
            break


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

        @validate_input
        def valid_food(x):
            if x > grain:
                raise NotEnoughGrain(grain)

        food = prompt_int('Grain for food = ', valid_food)
        grain -= food

        @validate_input
        def valid_farmland(land_to_farm):
            if land_to_farm > land:
                raise NotEnoughLand(land)
            elif (land_to_farm * 2) > grain:
                raise NotEnoughGrain(grain, hint=True)
            elif land_to_farm > (peasants * 4):
                raise NotEnoughWorkers(peasants)

        farmed = prompt_int('Land to be planted = ', valid_farmland)
        grain -= (farmed * 2)

        crop_yld = min(13, max(4, int(round(random.gauss(8.5, 1.5)))))
        print('Yield = {} HL/HA.'.format(crop_yld))

        # Advance a year
        year  += 1
        grain += crop_yld * farmed

        food_per_capita = int(food / peasants)
        if food_per_capita < 13:
            print('Some peasants have starved.')
            peasants -= peasants - int(food / 13)


def validate_input(validf):
    def wrapper(x):
        if x < 0:
            raise ValueError()
        validf(x)
        return x
    return wrapper


def prompt_int(msg, valid):
    while True:
        try:
            return valid(int(input(msg)))
        except InvalidInput as e:
            print(e)
        except ValueError:
            pass


def prompt_key(msg, keys):
    while True:
        val = input(msg).lower()
        if val in keys:
            return val


class InvalidInput(ValueError):

    pass


class NotEnoughGrain(InvalidInput):

    def __init__(self, grain, hint=False):
        msg = 'But you don\'t have enough grain.\nYou only have {} HL. of grain left.'.format(grain)
        if hint:
            msg += '\nEnough to plant {} HA. of land'.format(int(grain / 2))
        super().__init__(msg)


class NotEnoughLand(InvalidInput):

    def __init__(self, land):
        super().__init__('But you don\'t have enough land.\nYou only have {} HA. of land left.'.format(land))


class NotEnoughWorkers(InvalidInput):

    def __init__(self, workers):
        super().__init__('But you don\'t have enough peasants to farm that land.\n'
                         'You only have enough to farm {} HA. of land.'.format(int(workers * 4)))


if __name__ == '__main__':
    main()
