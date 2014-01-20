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


class TestWar(unittest.TestCase):


    def test_outcome(self):
        war = dukedom.War()
        winning_populations = [(1,  76), (2,  91), (3, 106), (4, 121), (5, 136),
                               (6, 151), (7, 166), (8, 181), (9, 196)]
        for enemy_modifier, threshold in winning_populations:
            for population in range(33, 200):
                won = war.campaign(enemy_modifier, population)
                if population < threshold:
                    self.assertFalse(won, '{} {}'.format(enemy_modifier, population))
                else:
                    self.assertTrue(won, '{} {}'.format(enemy_modifier, population))

if __name__ == '__main__':
    unittest.main()
