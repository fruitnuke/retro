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
        for enemy in range(1, 10):
            war = dukedom.War(enemy, 150, -10)
            war.campaign(10, 0)
            self.assertEqual(getattr(war, attr), expected[0][enemy-1], msg='enemy {}'.format(enemy))

        for i, pop in enumerate(range(80, 160, 10)):
            war = dukedom.War(5, pop, -10)
            war.campaign(15, 0)
            self.assertEqual(getattr(war, attr), expected[1][i], msg='pop {}'.format(pop))

        for i, resentment in enumerate(range(-40, 40, 10)):
            war = dukedom.War(5, 150, resentment)
            war.campaign(0, 0)
            self.assertEqual(getattr(war, attr), expected[2][i], msg='resentment {}'.format(resentment))

        for i, mercs in enumerate(range(0, 71, 10)):
            war = dukedom.War(5, 100, 0)
            war.campaign(mercs, 0)
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

        population = 30
        war = dukedom.War(9, population, 50)
        war.campaign(0, 0)
        self.assertEqual(war.casualties, population)

    def test_land_annexation(self):
        expected = [
            [ 125,   97,  69,  41,   13,  -15,  -43,  -72, -100],
            [ -62,  -47, -33, -18,   -3,   11,   26,   41,   55],
            [ 182,  106,  32, -43, -118, -194, -269, -343, -418],
            [-166, -110, -54,   2,   58,  114,  170,  226]]
        self._test('annexed', expected)

    def test_mercenary_pay(self):
        war = dukedom.War(5, 100, 0)
        for mercs in range(0, 71, 10):
            war.campaign(mercs, 10000)
            self.assertEqual(war.mercenary_pay, 40 * mercs)

    def test_looting_victims(self):
        vals = [(41, 0), (40, 0), (39, 1), (37, 1), (36, 2), (30, 2), (29, 3)]
        for grain, expected in vals:
            war = dukedom.War(5, 100, 0)
            war.campaign(1, grain)
            self.assertEqual(war.looting_victims, expected)

    def test_captured_grain_pays_mercenaries(self):
        """Test that grain captured from the enemy during victory can be used to pay mercenaries."""
        vals = [(160, 25, 0), (160, 23, 1), (160, 20, 2)]
        # In this war we win by just enough to capture 15 HL. of grain from the enemy.
        for pop, grain, looted in vals:
            war = dukedom.War(1, pop, 0)
            war.campaign(1, grain)
            self.assertEqual(war.looting_victims, looted)

    def test_captured_grain(self):
        """Test that victory results in grain captured immediately from annexed land."""
        expected = [
            [212, 165, 117,  70,   22,   0,   0,   0,  0],
            [  0,   0,   0,   0,    0,  19,  44,  70, 94],
            [309, 180,  54,   0,    0,   0,   0,   0,  0],
            [  0,   0,   0,   3,   99, 194, 289, 384]]
        self._test('captured_grain', expected)

    def test_landslide_victory(self):
        war = dukedom.War(1, 200, -20)
        war.campaign(50, 10000)
        self.assertTrue(war.landslide)
        self.assertEqual(war.casualties,    -47)
        self.assertEqual(war.captured_grain, 3513)
        self.assertEqual(war.looting_victims, 0)

    def test_successful_first_strike(self):
        """Test the outcome of a successful first strike, and the casualties and resentment it produces."""
        values = [(2, 3, 6), (6, 7, 14), (11, 12, 24)]
        for desperation, casualties, resentment in values:
            war = dukedom.War(1, 200, -20)
            war.first_strike(desperation, 3)
            self.assertTrue(war.ceasefire)
            self.assertEqual(war.casualties, casualties)
            self.assertEqual(war.resentment, resentment)

    def test_failed_first_strike_outcome(self):
        war = dukedom.War(9, 100, 20)
        war.first_strike(2, 3)
        self.assertFalse(war.ceasefire)

    def test_failed_first_strike_casualties(self):
        """Test the outcome of a failed first strike and the casualties it produces.
        We don't test the resentment produced as this will be calculated after the war, which is now
        inevitable. However the level of failure of the first strike does affect that resentment, but
        there is a seperate test for that connection.
        """
        values = [(2, 7), (6, 11), (11, 16)]
        for desperation, casualties in values:
            war = dukedom.War(9, 100, 20)
            war.first_strike(desperation, 3)
            self.assertEqual(war.casualties, casualties)

        values = [(3, 7), (6, 10), (9, 13)]
        for roll, casualties in values:
            war = dukedom.War(9, 100, 20)
            war.first_strike(2, roll)
            self.assertEqual(war.casualties, casualties)

    def test_failed_first_strike_increases_enemy_strength(self):
        values = [(2, 3, 268), (11, 9, 313)]
        for desperation, roll, enemy_strength in values:
            war = dukedom.War(9, 100, 20)
            before = war.away
            war.first_strike(desperation, roll)
            self.assertGreater(war.away,  before)
            self.assertEqual(war.away, enemy_strength)

    def test_failed_first_strike_accounted_for_in_campaign_accounting(self):
        war = dukedom.War(5, 100, 0)
        war.first_strike(2, 3)
        war.campaign(0, 0)
        self.assertEqual(war.casualties, 42)

if __name__ == '__main__':
    unittest.main()
#     unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromName('test_dukedom.WarTests.test_captured_grain_pays_mercenaries'))