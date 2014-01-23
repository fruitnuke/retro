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

    def _test(self, attr, expected):
        war = dukedom.War()
        for enemy in range(1, 10):
            war.campaign(enemy, 150, -10, 10)
            self.assertEqual(getattr(war, attr), expected[0][enemy-1], msg='enemy {}'.format(enemy))

        for i, pop in enumerate(range(80, 160, 10)):
            war.campaign(5, pop, -10, 15)
            self.assertEqual(getattr(war, attr), expected[1][i], msg='pop {}'.format(pop))

        for i, resentment in enumerate(range(-40, 40, 10)):
            war.campaign(5, 150, resentment, 0)
            self.assertEqual(getattr(war, attr), expected[2][i], msg='resentment {}'.format(resentment))

        for i, mercs in enumerate(range(0, 71, 10)):
            war.campaign(5, 100, 0, mercs)
            self.assertEqual(getattr(war, attr), expected[3][i], msg='mercenaries {}'.format(mercs))

    def test_outcome(self):
        """Test the outcome of war along the four dimensions."""
        expected = [
            [ True,  True,  True,  True,  True, False, False, False, False],
            [False, False, False, False, False,  True,  True,  True,  True],
            [ True,  True,  True, False, False, False, False, False, False],
            [False, False, False,  True,  True,  True,  True,  True]]
        self._test('won', expected)

    def test_casualties(self):
        expected = [
            [7, 11, 14, 18,  21, 25, 28, 32, 35],
            [22, 21, 21, 20, 20, 19, 19, 18, 18],
            [20, 22, 25, 27, 29, 32, 34, 36, 39],
            [31, 25, 19, 14,  8,  2,  0,  0]]
        self._test('casualties', expected)

    def test_land_annexation(self):
        expected = [
            [ 125,   97,  69,  41,   13,  -15,  -43,  -72, -100],
            [ -62,  -47, -33, -18,   -3,   11,   26,   41,   55],
            [ 182,  106,  32, -43, -118, -194, -269, -343, -418],
            [-166, -110, -54,   2,   58,  114,  170,  226]]
        self._test('annexed', expected)


if __name__ == '__main__':
    unittest.main()
