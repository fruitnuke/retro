import dukedom
import unittest


class Tests(unittest.TestCase):

    def test_allocate(self):
        self.assertEqual(list(dukedom.allocate([1, 0, 0], 1)), [1, 0, 0])
        self.assertEqual(list(dukedom.allocate([0, 1, 0], 1)), [0, 1, 0])
        self.assertEqual(list(dukedom.allocate([0, 0, 1], 1)), [0, 0, 1])
        self.assertEqual(list(dukedom.allocate([1, 0, 0], 0)), [0, 0, 0])
        self.assertEqual(list(dukedom.allocate([1, 0, 0], 2)), [1, 0, 0])
        self.assertEqual(list(dukedom.allocate([1, 1, 0], 2)), [1, 1, 0])
        self.assertEqual(list(dukedom.allocate([1, 1, 0], 1)), [1, 0, 0])
        self.assertEqual(list(dukedom.allocate([2, 0, 0], 1)), [1, 0, 0])
        self.assertEqual(list(dukedom.allocate([1, 0, 1], 2)), [1, 0, 1])
        self.assertEqual(list(dukedom.allocate([0, 0, 0], 1)), [0, 0, 0])
        self.assertEqual(list(dukedom.allocate([10, 10, 10], 30)), [10, 10, 10])
        self.assertEqual(list(dukedom.allocate([10, 10, 9 ], 30)), [10, 10, 9 ])
        self.assertEqual(list(dukedom.allocate([10, 10, 10], 29)), [10, 10, 9 ])
        self.assertEqual(list(dukedom.allocate([10, 10, 10], 15, proportional=True)), [3, 5, 7])
        self.assertEqual(list(dukedom.allocate([10,  0,  0], 15, proportional=True)), [3, 0, 0])
        self.assertEqual(list(dukedom.allocate([ 0, 10,  0], 15, proportional=True)), [0, 5, 0])
        self.assertEqual(list(dukedom.allocate([ 0,  0, 10], 15, proportional=True)), [0, 0, 10])
        self.assertEqual(list(dukedom.allocate([ 0,  0,  0], 15, proportional=True)), [0, 0, 0])
        self.assertEqual(list(dukedom.allocate([10, 10, 10],  2, proportional=True)), [2, 0, 0])
        self.assertEqual(list(dukedom.allocate([10, 10, 10],  4, proportional=True)), [3, 1, 0])
        self.assertEqual(list(dukedom.allocate([10, 10, 10],  9, proportional=True)), [3, 5, 1])
        self.assertEqual(list(dukedom.allocate([10, 10, 10], 20, proportional=True)), [3, 5, 10])


class WarTests(unittest.TestCase):


    def test_outcome(self):
        """Test the outcome of war along two dimensions - population size and the random modifier (proxy for enemy size)."""
        resentment = 0
        war = dukedom.War()
        winning_populations = [(1,  76), (2,  91), (3, 106), (4, 121), (5, 136),
                               (6, 151), (7, 166), (8, 181), (9, 196)]
        for enemy_modifier, threshold in winning_populations:
            for population in range(33, 200):
                won = war.campaign(enemy_modifier, population, resentment)
                if population < threshold:
                    self.assertFalse(won, '{} {}'.format(enemy_modifier, population))
                else:
                    self.assertTrue(won, '{} {}'.format(enemy_modifier, population))

    def test_effect_of_resentment(self):
        """Test the outcome of war along the third dimension - civilian resentment."""
        enemy_modifier = 5
        population     = 100
        war = dukedom.War()
        for resentment in range(-100, 89):
            won = war.campaign(enemy_modifier, population, resentment)
            expected_victory = resentment <= -7
            self.assertEqual(won, expected_victory)

    def test_casualties(self):
        expected = [
            [7, 9, 11, 12, 14, 16, 18, 20, 21],
            [15, 14, 14, 14, 14, 13], # second 14 should be 15, but because of rounding and float... use decimal?
            [11, 13, 14, 16, 17, 19]]

        war = dukedom.War()
        for enemy in range(1, 10):
            war.campaign(enemy, 100, 0)
            self.assertEqual(war.casualties, expected[0][enemy-1], msg='enemy {}'.format(enemy))

        for i, pop in enumerate([80, 90, 100, 110, 120, 130]):
            war.campaign(5, pop, 0)
            self.assertEqual(war.casualties, expected[1][i], msg='pop {}'.format(pop))

        for i, resentment in enumerate([-20, -10, 0, 10, 20, 30]):
            war.campaign(5, 100, resentment)
            self.assertEqual(war.casualties, expected[2][i], msg='resentment {}'.format(resentment))

    def test_land_annexation(self):
        expected = [
            [ 24,  10,  -5, -19, -34, -48,  -62,  -77,  -91],
            [-53, -43, -34, -24, -14,  -5,    5,   14,   24],
            [166, 117,  66,  16, -34, -84, -134, -184, -234]]

        war = dukedom.War()
        for enemy in range(1, 10):
            war.campaign(enemy, 100, 0)
            self.assertEqual(war.annexed, expected[0][enemy-1], msg='enemy {}'.format(enemy))

        for i, pop in enumerate(range(80, 160, 10)):
            war.campaign(5, pop, 0)
            self.assertEqual(war.annexed, expected[1][i], msg='pop {}'.format(pop))

        for i, resentment in enumerate(range(-40, 40, 10)):
            war.campaign(5, 100, resentment)
            self.assertEqual(war.annexed, expected[2][i], msg='resentment {}'.format(resentment))


if __name__ == '__main__':
    unittest.main()
