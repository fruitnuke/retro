"""The classic game of Hammurabi.

TODO:
 - mortality rates and end-game
 - input error handling
 - plague
 - impeachment
"""

from random import randint, choice
import textwrap
import math

report = textwrap.dedent('''
    Hammurabi: I beg to report to you,
    in year {}, {} people starved, {} came to the city,
    population is now {}
    the city now owns {} acres.
    You harvested {} bushels per acre.
    Rats ate {} bushels.
    You now have {} bushels in store.
    ''')


class EndGame(RuntimeError):
    pass


def hammurabi():
    harvest = 3000
    grain   = 2800
    ratfood = 200
    _yield  = 3 # bushels per acre
    acres   = int(math.floor(harvest / _yield))
    pop     = 100
    born    = 5
    starved = 0

    print('Try your hand at governing ancient Sumeria\n'
          'for a ten-year term of office.')

    try:
        for year in range(1, 11):
            print(report.format(year, starved, born, pop, acres, _yield, ratfood, grain))

            price = randint(17, 26)
            print('Land is trading at {} bushels per acre.'.format(price))

            def prompt(msg, is_valid, fail_msg):
                while True:
                    amt = int(input(msg + ' '))
                    if amt < 0:
                        raise EndGame('Hammurabi: I cannot do what you wish.\nGet yourself another steward!!!')
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
                              lambda n: n < acres,
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
                    raise EndGame('foo')
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

            # next year
            _yield  = randint(1, 6)
            harvest = planted * _yield
            ratfood = int(grain / choice([2, 4, 6])) if bool(choice([0, 1])) else 0
            grain   = grain + harvest - ratfood
            born    = int(randint(1, 6) * (20 * acres + grain) / float(pop) / 100.0 + 1)
            fed     = int(feed / 20.0)
            starved = pop - fed
            pop     = pop - starved + born

            total_deaths += starved
            mortality_rate = ((year - 1) * mortality_rate + starved * 100 / pop) / year

    except EndGame as e:
        print(e)


if __name__ == '__main__':
    hammurabi()