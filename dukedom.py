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
    distributions = Gaussian()  # Talbot()

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

        crop_yld = distributions.random(2)
        print('Yield = {} HL/HA.'.format(crop_yld))

        # Advance a year
        year  += 1
        grain += crop_yld * farmed

        food_per_capita = int(food / peasants)
        if food_per_capita < 13:
            print('Some peasants have starved.')
            peasants -= peasants - int(food / 13)

        natural_deaths = int(0.3 - peasants / 22)


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


class Gaussian:

    def __init__(self):
        self.curves = [None] * 8
        self.curves[1] = (4, 13, int(round(random.gauss(6, 1))), 1.5)

    def random(self, curve):
        a, b, mean, dev = self.curves[curve - 1]
        return min(b, max(a, int(round(random.gauss(mean, dev)))))


class Talbot:

    """Implements the "PARTIALLY GAUSSIAN RANDOM #" generator used by Talbot in his BASIC version
    of Dukedom. We have a (much) better Gaussian random number generator in Python, but I wanted
    to keep the option to use this around and I wanted to understand how Talbot's random number
    generation worked. I'm not sure how Talbot came up with this scheme - it doesn't seem based
    on any of the Gaussian approximation algorithm's I've researched from around that period."""

    def __init__(self):
        self.table = [0] * 8
        self.init_table()
        self.adjustments = [0, 9, 0, 0, 0, 0, 0, 0]

    def random(self, curve):
        return self.fnx(curve - 1) + self.adjustments[curve - 1]

    def fnr(self, a, b):
        """This function uses rounding to produce a very loose approximation of a normal distribution.
        It will produce a pseudo-random real number in the range [a, b + 1) with uniform redistribution.
        As the number is rounded  to the nearest integer however, the lowest number a will only be rounded
        down to from a < x < (a + 0.5), and b will only be rounded up to from b > x > (b - 0.5), which is
        half the number range the other numbers can be rounded from, so the 2 end integers will be produced
        with half the probability of the other integers in the interval.

            >>> histogram = collections.Counter(fnr(4, 7) for _ in range(10000))
            >>> print('fnr pdf  ', sorted(histogram.most_common()))
            [(4, 1195), (5, 2497), (6, 2510), (7, 2553), (8, 1245)]

        Because this function produces integers in the interval [a, b+1), given that it 'approximates' a
        normal distribution we can see that the distibution has a mean of (a + b + 1) / 2. For example
        fnr(-2, 2) will produce a distribution with mean 0.5 (not 0); fnr(4, 7) will produce a distribution
        with mean 6 (not 5.5).
        """
        return int(round(random.random() * (1 + b - a) + a))

    def init_table(self):
        """Different stochastic properties within the game - births, crop yield, chance of disease, etc. - want
        to have different probability distributions. In this case while they all have the same standard deviation
        as the distribution fnr(-2, 2), we vary each curve at the start of the game by shifting its mean. TABLE
        is an array of the different mean transformation applied to each of the 8 probability curves used in the
        game. It's not the actual mean - that will actually be 0.5 higher (see fnr for explanation). An example
        initialization:

            [7, 8, 6, 4, 6, 4, 6, 2]

        The interesting part is that the mean shift itself for any given curve in any given game is produced
        with an approximately gaussian probability distribution:

            >>> histogram = collections.Counter()
            >>> for _ in range(10000):
                    init_table()
                    histogram.update([TABLE[0]])
            >>> print(sorted(histogram.most_common()))
            [(4, 943), (5, 1687), (6, 4667), (7, 1709), (8, 994)]

        where TABLE[0] is calculated with the interval (4, 7).

        Experimentally, initializing the table 10,000 times and taking a histogram of the values produced for
        each curve gives something like this:

            (4, 7): [(4, 983),  (5, 1710), (6, 4600), (7, 1765), (8, 942)]
            (4, 8): [(4, 636),  (5, 1206), (6, 3736), (7, 1756), (8, 2300), (9, 366)]
            (4, 6): [(4, 1547), (5, 2834), (6, 4650), (7, 969)]
            (3, 6): [(3, 865),  (4, 2924), (5, 2361), (6, 3017), (7, 833)]
            (5, 6): [(5, 1115), (6, 7800), (7, 1085)]
            (3, 6): [(3, 820),  (4, 3036), (5, 2353), (6, 2985), (7, 806)]
            (3, 8): [(3, 367),  (4, 1581), (5, 1372), (6, 3224), (7, 1373), (8, 1712), (9, 371)]
            (1, 8): [(1, 345),  (2, 1114), (3, 949),  (4, 1969), (5, 1256), (6, 1939), (7, 993), (8, 1054), (9, 381)]

        Notice how some of the distributions - (1, 8) and (3, 6) for example - have decidedly non-gaussian profiles
        with two peaks and a dip in between.
        """
        pairs = [(4, 7), (4, 8), (4, 6), (3, 6), (5, 6), (3, 6), (3, 8), (1, 8)]
        for i, (a, b) in enumerate(pairs):
            r1 = self.fnr(a, b)
            if self.fnr(a, b) > 5:
                self.table[i] = int(round((r1 + self.fnr(a, b)) / 2))
            else:
                self.table[i] = r1

    def fnx(self, a):
        """This function simply shifts the mean of the probability distribution produced by fnr(-2, 2) by the
        pre-calculated value in TABLE[a], and produces a random number from the resulting distribution.
        """
        return self.fnr(-2, 2) + self.table[a]


if __name__ == '__main__':
    main()
