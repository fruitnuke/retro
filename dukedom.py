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
- I removed the 'peasants from end' stat, as it's always the same as 'peasants' which is printed each turn anyway.

TODO
----
- Check the land price probability distribution / calc, it's way off.
- Co-routines to separate UI and simulation logic?
'''

import collections
import random
import textwrap


def main():
    while True:
        dukedom()
        if prompt_key('Do you wish to play again?', 'yn') == 'n':
            break


class GameReport:

    def __init__(self):
        self._data = collections.OrderedDict([
            ('Peasants at start', 96  ),
            ('Starvations',       0   ),
            ('King\'s levy',      0   ),
            ('Disease victims',   0   ),
            ('Natural deaths',   -4   ),
            ('Births',            8   ),
            ('Land at start',     600 ),
            ('Bought/sold',       0   ),
            ('Grain at start',    5193),
            ('Used for food',    -1344),
            ('Land deals',        0   ),
            ('Seeding',          -768 ),
            ('Rat losses',        0   ),
            ('Crop yield',        1516),
            ('Castle expense',   -120 )])

    def record(self, stat, x):
        self._data[stat] = x

    ZERO_EACH_YEAR = ['Starvations', 'King\'s Levy', 'Disease victims', 'Bought/sold',
                      'Land deals', 'Rat losses', 'Castle expense']

    def reset(self):
        for x in self.ZERO_EACH_YEAR:
            self._data[x] = 0

    def __iter__(self):
        return iter(self._data.items())


class GameState:

    def __init__(self):
        self.peasants = 100
        self.grain    = 4177 # Hectolitres
        self.land     = 600  # Hectares
        self.year     = 0
        self.crop_yield    = 3.95
        self.cool_down = 0


def dukedom():
    print('')
    print('D U K E D O M')
    print('')

    show_report = prompt_key('Do you want to skip detailed reports?', 'yn') == 'n'

    distributions = Gaussian()  # Talbot()
    report = GameReport()
    game   = GameState()

    while True:
        print('\nYear {} Peasants {} Land {} Grain {}\n'.format(game.year, game.peasants, game.land, game.grain))
        if show_report:
            for label, x in report:
                if x != 0:
                    print('  {:<20}{}'.format(label, x))
            if game.year <= 0:
                print('  (Severe crop damage due to seven year locusts.)')
            print('')

        # Test for end game
        if game.peasants < 33:
            print('You have so few peasants left that\n'
                  'the High King has abolished your Ducal\n'
                  'right.\n')
            break
        if game.land <= 199:
            print('You have so little land left that\n'
                  'the peasants are tired of war and starvation.\n'
                  'You are deposed.\n')
            break


        # We start off in game year 0 for the first report. This is presumably to show continuity with
        # whoever was running the dukedom before, and add history to the game world.
        game.year = game.year + 1
        report.record('Peasants at start', game.peasants)
        report.record('Grain at start',    game.grain)
        report.record('Land at start',     game.land)
        report.reset()

        # Feed the peasants
        @validate_input
        def valid_food(x):
            if x > game.grain:
                raise NotEnoughGrain(game.grain)
        food = prompt_int('Grain for food = ', valid_food)
        game.grain -= food
        report.record('Used for food', -food)

        # Buy and sell land
        bid = round(2 * game.crop_yield + distributions.random(1) - 5)
        @validate_input
        def valid_buy(x):
            if (x * bid) > game.grain:
                raise NotEnoughGrain(game.grain)
        bought = prompt_int('Land to buy at {0} HL./HA. = '.format(bid), valid_buy)
        if bought == 0:
            offer = bid - 1
            @validate_input
            def valid_sell(x):
                if x > game.land:
                    raise NotEnoughLand(game.land)
                if (x * offer) > 4000:
                    # You cannot sell more than 4000 HL worth of land in any one year.
                    # That's all the grain available to pay you with.
                    raise Overfill()
            sold = prompt_int('Land to sell at {0} HL./HA. = '.format(offer), valid_sell)
            game.land  -= sold
            game.grain += offer * sold
            report.record('Bought/sold', -sold)
            report.record('Land deals', offer * sold)
        else:
            game.land  += bought
            game.grain -= bid * bought
            report.record('Bought/sold', bought)
            report.record('Land deals', -bid * bought)

        # Farm land
        @validate_input
        def valid_farmland(land_to_farm):
            if land_to_farm > game.land:
                raise NotEnoughLand(game.land)
            elif (land_to_farm * 2) > game.grain:
                raise NotEnoughGrain(game.grain, hint=True)
            elif land_to_farm > (game.peasants * 4):
                raise NotEnoughWorkers(game.peasants)
        farmed = prompt_int('Land to be planted = ', valid_farmland)
        seeding = -(farmed * 2)
        game.grain += seeding
        report.record('Seeding', seeding)

        # Harvest
        game.crop_yield = distributions.random(2) + 9
        if (game.year % 7) == 0:
            # Field grain is eaten by seven year locusts. They eat half of all your crop
            # in the years that they appear.
            print('Seven year locusts.')
            game.crop_yield = round(game.crop_yield * 0.65) # Hmm, not really half...
        print('Yield = {} HL/HA.'.format(game.crop_yield))

        harvest = game.crop_yield * farmed

        crop_hazards = distributions.random(3) + 3
        print(crop_hazards)
        if crop_hazards > 9:
            # Sometimes the rats get into the granary and eat up to 10% or so of your
            # reserve grain. Rats never eat field grain.
            eaten = round((crop_hazards * game.grain) / 83)
            print('Rats infest the grainery')
            game.grain -= eaten
            report.record('Rat losses', -eaten)

            if game.peasants > 66:
                levy = distributions.random(4)
                print(levy)
                if levy < (game.peasants / 30):
                    # Occasionally rats will eat so much of the High King's grain that some of his
                    # workers starve to death. When this happens, the King will require some
                    # peasants from each of his Dukes as replacements. You may supply them as
                    # requested or pay an alternate amount of grain.
                    or_grain    = levy * 100
                    msg = textwrap.dedent('''
                        The king requires {} peasants for
                        his estate and mines. Will you supply
                        them? (Y)es or pay {} HL. of
                        grain instead (N)o?''').format(levy, or_grain).lstrip()
                    if prompt_key(msg, 'yn') == 'n':
                        game.grain -= or_grain
                        report.record('Castle expense', -or_grain)
                    else:
                        game.peasants -= levy
                        report.record('King\'s levy', -levy)

        game.grain += harvest
        report.record('Crop yield', harvest)

        # population mechanics
        starved = 0
        if int(food / game.peasants) < 13:
            print('Some peasants have starved.')
            starved = -round(game.peasants - food / 13)
            game.peasants += starved
        report.record('Starvations', starved)

        deaths = 0
        chance_of_outbreak = distributions.random(8) + 1
        game.cool_down -= 1
        if chance_of_outbreak == 1 and game.cool_down == 0:
            print('The BLACK PLAGUE has struck the area')
            game.cool_down = 13
            deaths = -round(game.peasants / 3)
        elif chance_of_outbreak < 4:
            print('A POX EPIDEMIC has broken out')
            deaths = -round(game.peasants / (chance_of_outbreak * 5))
        game.peasants += deaths
        report.record('Disease victims', deaths)

        natural = int(0.3 - game.peasants / 22)
        report.record('Natural deaths', natural)
        deaths += natural

        births = int(round(game.peasants / (distributions.random(8) + 4)))
        report.record('Births', births)
        game.peasants += births + deaths



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
        val = input(msg+' ').lower()
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

class Overfill(InvalidInput):

    def __init__(self):
        super().__init__('No buyers have that much grain, try less')


class Gaussian:

    def __init__(self):
        self.means = [None] * 8
        self.means[0] = self._gauss(6.0, 1.0, 4, 8)
        self.means[1] = self._gauss(6.5, 1.1, 4, 9)
        self.means[2] = self._gauss(5.5, 0.9, 4, 7) # Chance of crop_hazards
        self.means[3] = self._gauss(5.0, 1.1, 3, 7) # Chance of king's levy
        self.means[7] = self._gauss(5.0, 2.0, 1, 9) # Births

    def _gauss(self, mean, dev, a, b):
        return min(b, max(a, int(round(random.gauss(mean, dev)))))

    def random(self, curve):
        return self._gauss(0.5, 1.5, -3, 2) + self.means[curve-1]


class Talbot:

    """Implements the "PARTIALLY GAUSSIAN RANDOM #" generator used by Talbot in his BASIC version
    of Dukedom. We have a (much) better Gaussian random number generator in Python, but I wanted
    to keep the option to use this around and I wanted to understand how Talbot's random number
    generation worked. I'm not sure how Talbot came up with this scheme - it doesn't seem based
    on any of the Gaussian approximation algorithm's I've researched from around that period."""

    def __init__(self):
        self.table = [0] * 8
        self.init_table()

    def random(self, curve):
        return self.fnx(curve - 1)

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
