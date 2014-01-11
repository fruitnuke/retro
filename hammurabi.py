"""The classic game of Hammurabi.

BUGS:
 - Mortality calc rates seem wrong at end of game.
"""

from random import randint, choice, random
import textwrap
import math


class EndGame(RuntimeError):

    pass


class Impeached(EndGame):

    def __init__(self, starved):
        super().__init__('You starved {} people in one year!!!'.format(starved))


class Resigns(EndGame):

    def __init__(self):
        super().__init__('\nHammurabi: I cannot do what you wish.\nGet yourself another steward!!!')


def hammurabi():
    harvest = 3000
    grain   = 2800
    ratfood = 200
    _yield  = 3 # bushels per acre
    acres   = int(math.floor(harvest / _yield))
    pop     = 100
    born    = 5
    starved = 0

    impeached = False
    plague    = False

    total_deaths   = 0
    mortality_rate = 0

    print('Try your hand at governing ancient Sumeria\n'
          'for a ten-year term of office.')

    try:
        for year in range(1, 11):
            if plague:
                pop = int(pop / 2)
                plague_text = '\na horrible plague struck! Half the people died,'
            else:
                plague_text = ''

            print(textwrap.dedent('''
                Hammurabi: I beg to report to you,
                in year {}, {} people starved, {} came to the city,{}
                population is now {}
                the city now owns {} acres.
                You harvested {} bushels per acre.
                Rats ate {} bushels.
                You now have {} bushels in store.
                ''').format(year, starved, born, plague_text, pop, acres, _yield, ratfood, grain))

            price = randint(17, 26)
            print('Land is trading at {} bushels per acre.'.format(price))

            def prompt(msg, is_valid, fail_msg):
                while True:
                    try:
                        amt = int(input(msg + ' '))
                    except ValueError:
                        continue
                    if amt < 0:
                        raise Resigns()
                    if is_valid(amt):
                        return amt
                    print(fail_msg)

            buy = prompt('How many acres do you wish to buy?',
                         lambda n: n * price <= grain,
                         'Hammurabi: Think again. You have only {} bushels of grain. Now then,'.format(grain))

            if buy > 0:
                acres += buy
                grain -= price * buy
            elif buy == 0:
                sell = prompt('How many acres do you wish to sell?',
                              lambda n: n <= acres,
                              'Hammurabi: Think again. You own only {} acres. Now then,'.format(acres))
                if sell > 0:
                    acres -= sell
                    grain += (sell * price)

            feed = prompt('How many bushels do you wish to feed your people?',
                          lambda n: n <= grain,
                          'Hammurabi: Think again. You have only {} bushels of grain. Now then,'.format(grain))
            grain = grain - feed

            while True:
                planted = int(input('How many acres do you wish to plant? '))
                if planted < 0:
                    raise Resigns()
                if planted > acres:
                    print('Hammurabi: Think again. You own only {} acres. Now then,'.format(acres))
                    continue
                if (planted / 2) > grain: # 1 bushel plants 2 acres
                    print('Hammurabi: Think again. You have only {} bushels. Now then,'.format(grain))
                    continue
                if planted > (10 * pop): # 1 person can tend 10 acres
                    print('Hammurabi: But you have only {} people to tend the fields! Now then,'.format(pop))
                    continue
                break

            grain -= int(math.ceil(planted / 2))
            _yield  = randint(1, 6)
            harvest = planted * _yield
            ratfood = int(grain / choice([2, 4, 6])) if bool(choice([0, 1])) else 0
            grain   = grain + harvest - ratfood
            born    = int(randint(1, 6) * (20 * acres + grain) / float(pop) / 100.0 + 1)
            fed     = int(feed / 20.0)
            starved = pop - fed
            pop     = pop - starved + born
            plague  = random() < 0.15
            total_deaths += starved
            mortality_rate = ((year - 1) * mortality_rate + starved * 100 / pop) / year

            if starved > (pop * 0.45):
                raise Impeached(starved)

    except Impeached as e:
        print(e)
        impeached = True
    except Resigns as e:
        print(e)
        return

    acres_per_person = acres / pop

    print()
    print('In your {}-year term of office, {} percent of the\n'
          'population starved per year on the average, i.e. a total of\n'
          '{} people died!!\n'.format(year, int(round(mortality_rate)), total_deaths))

    if impeached or mortality_rate > 33 or acres_per_person < 7:
        print('Due to your extreme mismanagement you have not only\n'
              'been impeached and thrown out of office but you have\n'
              'also been declared national fink!!!!')
    elif mortality_rate > 10 or acres_per_person < 9:
        print('Your heavy-handed performance smacks of Nero and Ivan IV.\n'
              'The people (remaining) find you an unpleasant ruler, and,\n'
              'frankly, hate your guts!!')
    elif mortality_rate > 3 or acres_per_person < 10:
        haters = int(pop * random() * 0.8)
        print('Your performance could have been somewhat better, but\n'
              'really wasn\'t too bad at all. {} people\n'
              'dearly like to see you assassinated but we all have our\n'
              'trivial problems.'.format(haters))
    else:
        print('A fantastic performance!!! Charlemagne, Disraeli and\n'
              'Jefferson combined could not have done better!')

    print('\nSo long for now.')


if __name__ == '__main__':
    hammurabi()