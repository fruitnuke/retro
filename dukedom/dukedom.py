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
  in the BASIC version (it has the text, but not the check).

- As 'Fruits of war' appears in both the land and grain detailed reports, I've replaced the land entry with
  'Annexed land' and the grain entry with 'Captured grain'.

- The BASIC version includes a "partially Gaussian random #" generator, which uses a uniform random number
  generator to produce numbers with a probability density function that (seems to very loosely) approximate
  that of a normal function. Python has a (couple of) random number generator(s) with normal distribution built
  in so I just use that. Then it's just working out the mean and standard deviation for each bell curve that Talbot
  intended.

- Instructions for original claim 'yield for fallow land is calculated each year at random (variances in the weather)
  and ranges from 4 to 13 hectoliters for each hectare planted.' In fact the code shows that it uses a pdf with a mean
  between 4 and 9, and range of -2 to 3, giving a potential random number range of 2 to 12. The game then adds 9 to that
  number giving a yield range of 11 to 21 for fallow land! [C=FNX%(2)+9]

- Instructions claim seven year locusts eat half the field grain, but in the BASIC code it's actually 35%. [C=INT(C*.65)]

- Instructions claim 'A mercenary is worth about 8 peasants in fighting power', but from the code it actually seems
  to be worth 7.


TODO
----
- Check the land price probability distribution / calc, it's way off.
- Co-routines to separate UI and simulation logic?
'''

import collections
from   itertools import chain
import random
import textwrap


def main():
    print('')
    print('D U K E D O M')
    print('')
    show_report = prompt_key('Do you want to skip detailed reports?', 'yn') == 'n'
    while True:
        try:
            dukedom(show_report)
        except EndGame as e:
            print(e)
        if prompt_key('Do you wish to play again?', 'yn') == 'n':
            break


class GameReport:

    def __init__(self):
        self._data = collections.OrderedDict([
            ('Peasants at start',    96  ),
            ('Starvations',          0   ),
            ('King\'s levy',         0   ),
            ('War casualties',       0   ),
            ('Looting victims',      0   ),
            ('Disease victims',      0   ),
            ('Natural deaths',      -4   ),
            ('Births',               8   ),
            ('Peasants at end',      100 ),

            ('Land at start',        600 ),
            ('Bought/sold',          0   ),
            ('Annexed land',         0   ),
            ('Land at end of year',  600 ),

            ('Grain at start',       5193),
            ('Used for food',       -1344),
            ('Land deals',           0   ),
            ('Seeding',             -768 ),
            ('Rat losses',           0   ),
            ('Mercenary hire',       0   ),
            ('Captured grain',       0   ),
            ('Crop yield',           1516),
            ('Castle expense',      -120 ),
            ('Grain at end of year', 4177)])

    def record(self, stat, x):
        self._data[stat] = x

    ZERO_EACH_YEAR = ['Starvations', 'King\'s Levy', 'Disease victims', 'Bought/sold',
                      'Land deals', 'Rat losses', 'Castle expense', 'War casualties',
                      'Looting victims', 'Annexed land', 'Captured grain']

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
        self.crop_yield = 3.95
        self.cool_down  = 0
        self.resentment = 0 # long_term resentment trend
        self.buckets = [216, 200, 184, 0, 0, 0] # 100%, 80%, 60%, 40%, 20% and depleted land.


def dukedom(show_report):
    distributions = Gaussian()  # Talbot()
    report = GameReport()
    game   = GameState()
    resentment = 0

    while True:
        report.record('Peasants at end',      game.peasants)
        report.record('Land at end of year',  game.land)
        report.record('Grain at end of year', game.grain)

        print('\nYear {} Peasants {} Land {} Grain {}\n'.format(game.year, game.peasants, game.land, game.grain))
        if show_report:
            def group(it, n):
                for _ in range(n):
                    label, x = next(it)
                    if x:
                        print('  {:<22}{}'.format(label, x))
                print('')
            stats = iter(report)
            group(stats, 9)
            group(stats, 4)
            print('  100%  80%  60%  40%  20%  Depl')
            print(('  ' + '{:>5}'*6).format(*game.buckets), '\n')
            group(stats, 10)
            if game.year <= 0:
                print('(Severe crop damage due to seven year locusts.)\n')

        # Test for end game
        if game.peasants < 33:
            raise EndGame('pop loss')
        if game.land < 200:
            raise EndGame('land loss')
        if resentment > 88 or game.resentment > 99 or game.grain < 429:
            raise EndGame('deposed')
        if game.year > 45:
            raise EndGame('retirement')

        # We start off in game year 0 for the first report. This is presumably to show continuity with
        # whoever was running the dukedom before, and add history to the game world.
        game.year  = game.year + 1
        resentment = 0
        report.record('Peasants at start', game.peasants)
        report.record('Grain at start',    game.grain)
        report.record('Land at start',     game.land)
        report.reset()

        # Feed the peasants
        @validate_input
        def valid_food(x):
            if x > 100:
                if x > game.grain:
                    raise NotEnoughGrain(game.grain)
            elif (x * game.peasants) > game.grain:
                raise NotEnoughGrain(game.grain)

        food = prompt_int('Grain for food = ', valid_food)

        # User can enter a number under 100 which represents food per peasant to give,
        # or a number over 100 which represents the total amount of food to give.
        if food > 100:
            food_per_capita = int(food / game.peasants)
        else:
            food_per_capita = food
            food = food * game.peasants

        game.grain -= food
        report.record('Used for food', -food)

        starved = 0
        overfed = 0
        if food_per_capita < 13:
            starved = game.peasants - int(food / 13)
            game.peasants  -= starved
            print('Some peasants have starved')
            report.record('Starvations', -starved)
        overfed = min(4, food_per_capita - 14)
        resentment += (3 * starved) - (2 * overfed)

        if resentment > 88:
            raise EndGame('deposed')
        elif game.peasants < 33:
            raise EndGame('pop loss')

        # Buy and sell land
        bid = round(2 * game.crop_yield + distributions.random(1) - 5)

        @validate_input
        def valid_buy(x):
            if (x * bid) > game.grain:
                raise NotEnoughGrain(game.grain)

        bought = prompt_int('Land to buy at {0} HL./HA. = '.format(bid), valid_buy)

        if bought == 0:
            offer    = bid - 1
            sellable = sum(game.buckets[:3])

            @validate_input
            def valid_sell(x):
                if x > sellable:
                    raise NotEnoughGoodLand(sellable)
                if (x * offer) > 4000:
                    # You cannot sell more than 4000 HL worth of land in any one year.
                    # That's all the grain available to pay you with.
                    raise Overfill('No buyers have that much grain, try less')

            sold = prompt_int('Land to sell at {0} HL./HA. = '.format(offer), valid_sell)
            if sold:
                game.land  -= sold

                # allocate sold land from good land starting at 60% and working up to 100% land
                x = list(reversed(game.buckets[:3]))
                sold_buckets = list(reversed(list(allocate(x, sold))))
                game.buckets = [a - b for a, b in zip(game.buckets, chain(sold_buckets, [0, 0, 0]))]

                game.grain += offer * sold
                report.record('Bought/sold', -sold)
                report.record('Land deals', offer * sold)
        else:
            game.land     += bought
            game.buckets[2] += bought
            game.grain    -= bid * bought
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

        # Crop gains
        yld = distributions.random(2) + 9
        if (game.year % 7) == 0:
            # Field grain is eaten by seven year locusts. They eat half of all your crop
            # in the years that they appear.
            print('Seven year locusts.')
            yld = round(yld * 0.65) # Hmm, not really half...

        sown     = list(allocate(game.buckets, farmed))
        fallow   = [a - b for a, b in zip(game.buckets, sown)]
        weighted = sum(area * (1.0 - (0.2 * i)) for i, area in enumerate(sown[:5]))
        if farmed > 0:
            game.crop_yield = round(yld * (weighted / farmed) * 100) / 100
        else: # avoid division by zero
            game.crop_yield = 0

        print('Yield = {} HL/HA.'.format(game.crop_yield))

        depletion  = [0] + sown[:4] + [sum(sown[4:])]
        nutrition  = [sum(fallow[:3])] + fallow[3:] + [0, 0]
        game.buckets = [a + b for a, b in zip(depletion, nutrition)]

        # Crop losses
        crop_hazards = distributions.random(3) + 3
        if crop_hazards > 9:
            # Sometimes the rats get into the granary and eat up to 10% or so of your
            # reserve grain. Rats never eat field grain.
            eaten = round((crop_hazards * game.grain) / 83)
            print('Rats infest the grainery')
            game.grain -= eaten
            report.record('Rat losses', -eaten)

            if game.peasants > 66:
                levy = distributions.random(4)
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

        harvest = round(game.crop_yield * farmed)

        # war
        desperation = max(2, round(11 - 1.5 * game.crop_yield)) # How badly neighbouring duchies are driven to attack
        if distributions.random(5) < desperation:
            print('A nearby Duke threatens war.')
            mod = distributions.random(6)

            @validate_input
            def validate_mercs(x):
                if x > 75:
                    raise Overfill('There are only 75 available for hire.')
            mercs = prompt_int('How many mercenaries will you hire at 40HL. each = ', validate_mercs)

            war = War()
            won = war.campaign(mod, game.peasants, resentment, mercs)

            if won:
                if war.annexed > 399:
                    print('You have overrun the enemy and annexed\n'
                          'his entire dukedom.')
                    crop_from_annexed_land = round(war.annexed * 0.55)
                    captured_grain = 3513

                    # We actually gain peasants from the population of the dukedom we've annexed.
                    war.casualties = -47

                else:
                    print('You have won the war.')

                    # The crop you gain at the end of the year from land gained from the duchy that attacked you
                    # is set at 0.67, presumably because the optimal way to farm land is to farm two-thirds of it
                    # and to leave one-third fallow to gain nutrition; so we can assume that's what other duchies
                    # are doing.
                    crop_from_annexed_land = round(war.annexed * 0.67 * game.crop_yield)

                    # Grain captured immediately from annexed land (not from harvest at the end of the year. This
                    # can be used to pay mercenaries (unlike the harvest) and is the only form of credit in the game.
                    captured_grain = round(war.annexed * 1.7)

                # Allocate annexed land equally between the three buckets of 'good' land.
                annexed = war.annexed
                res = []
                for i in range(0, 3):
                    x = round(annexed / (3 - i))
                    res.append(x)
                    annexed -= x
                assert(annexed == 0)
                game.buckets = [a+b for a, b in zip(game.buckets, res + [0, 0, 0])]

                game.grain += captured_grain
                report.record('Captured grain', captured_grain)

            else:
                if war.annexed < -round(game.land * 0.67):
                    raise EndGame('overrun')

                else:
                    print('You have lost the war.')
                    annexed_by_bucket = list(allocate(game.buckets[:3], abs(war.annexed), proportional=True))
                    game.buckets = [a-b for a, b in zip(game.buckets, annexed_by_bucket + [0, 0, 0])]

                    # The amount of annexed land is a negative value here.
                    crop_from_annexed_land = round(war.annexed * (farmed / game.land) * game.crop_yield)

            game.peasants -= war.casualties
            game.land += war.annexed
            resentment += 2 * war.casualties

            harvest += crop_from_annexed_land

            report.record('War casualties', -war.casualties)
            report.record('Annexed land',    war.annexed)

        # demographics
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
        natural = round(0.3 - game.peasants / 22)
        report.record('Natural deaths', natural)
        deaths += natural
        births = round(game.peasants / (distributions.random(8) + 4))

        # end of year
        game.peasants += births + deaths
        game.grain    += harvest
        game.resentment = round(game.resentment * 0.85) + resentment

        report.record('Births',     births)
        report.record('Crop yield', harvest)


class War:

    def __init__(self):
        self.casualties = 0
        self.annexed = 0
        self.won = False

    def campaign(self, enemy_modifier, population, resentment, mercs):
        """Fight the war.

        Params:

            - enemy_modifier: a random integer in the range [1, 9], is a proxy for enemy strength / size.
            - population: The number of peasants in your duchy.
            - resentment: an integer that gives the level of resentment against you by your peasants.
            - mercs: a positive integer representing the number of mercenaries hired.

        Returns True if the campaign was won, False otherwise. Sets self.casualties with the total number
        of casualties since the war started.
        """
        fighting_spirit = 1.2 - (resentment / 16.0)
        away            = round((enemy_modifier * 18 + 85) * 1.95)
        home            = round(population * fighting_spirit) + (mercs * 7) + 13
        casualties      = round((away - (mercs * 4) - round(home * 0.25)) / 10)
        self.casualties = max(0, casualties)
        self.annexed    = round((home - away) * 0.8)
        self.won        = home > away
        return self.won


def allocate(buckets, amount, proportional=False):
    n = len(buckets)
    for i, bucket in enumerate(buckets):
        if proportional:
            limit = round(bucket / (n - i))
        else:
            limit = bucket
        x = min(amount, limit)
        amount = max(amount - x, 0)
        yield x


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


class EndGame(RuntimeError):

    def __init__(self, reason):
        msg = {
            'pop loss':   'You have so few peasants left that\n'
                          'the High King has abolished your Ducal\n'
                          'right.\n',
            'deposed':    'The peasants are tired of war and starvation.\n'
                          'You are deposed.\n',
            'land loss':  'You have so little land left that\n'
                          'the peasants are tired of war and starvation.\n'
                          'You are deposed.\n',
            'retirement': 'You have reached the age of retirement.\n',
            'overrun'   : 'You have been overrun and and have lost\n'
                          'your entire Dukedom. Your head is placed\n'
                          'atop of the castle gate.\n',
            }[reason]
        super().__init__(msg)


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


class NotEnoughGoodLand(InvalidInput):

    def __init__(self, good_land):
        super().__init__('But you only have {} HA. of good land.'.format(good_land))


class NotEnoughWorkers(InvalidInput):

    def __init__(self, workers):
        super().__init__('But you don\'t have enough peasants to farm that land.\n'
                         'You only have enough to farm {} HA. of land.'.format(int(workers * 4)))

class Overfill(InvalidInput):

    def __init__(self, msg):
        super().__init__(msg)


class Gaussian:

    def __init__(self):
        self.means = [None] * 8
        self.means[0] = self._gauss(6.0, 1.0,  4, 8)
        self.means[1] = self._gauss(6.5, 1.1,  4, 9)
        self.means[2] = self._gauss(5.5, 0.9,  4, 7) # Chance of crop hazards
        self.means[3] = self._gauss(5.0, 1.1,  3, 7) # Chance of king's levy
        self.means[4] = self._gauss(6.0, 0.41, 5, 7) # Chance of war
        self.means[5] = self._gauss(5.0, 1.1,  3, 7) # Attacker's strength
        self.means[7] = self._gauss(5.0, 2.0,  1, 9) # Births

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
