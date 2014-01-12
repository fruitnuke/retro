'''Dukedom, a more complex game of resource management than Hammurabi, with elements of empire building.
'''


def dukedom():
    peasants = 100
    grain    = 4177 # Hectolitres
    year     = 1

    while True:
        print('\nYear {} Peasants {} Grain {}\n'.format(year, peasants, grain))

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
            print('But you don\'t have enough grain.\nYou have {}HL. of grain left.\n'.format(grain))

        year  += 1
        grain -= food

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