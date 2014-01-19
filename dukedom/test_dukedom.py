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

    def test_war_enemy_strength(self):
        self.assertEqual(dukedom.war(2, False, 1, 100, 0)['outcome'], 'peace')
        self.assertEqual(dukedom.war(2, False, 2, 100, 0)['outcome'], 'peace')
        self.assertEqual(dukedom.war(2, False, 3, 100, 0)['outcome'], 'war')
        self.assertEqual(dukedom.war(2, False, 9, 100, 0)['outcome'], 'war')

    def test_war_population(self):
        self.assertEqual(dukedom.war(2, False, 5, 33,  0)['outcome'], 'war')
        self.assertEqual(dukedom.war(2, False, 5, 135, 0)['outcome'], 'war')
        self.assertEqual(dukedom.war(2, False, 5, 136, 0)['outcome'], 'peace')
        self.assertEqual(dukedom.war(2, False, 5, 150, 0)['outcome'], 'peace')

    def test_war_fighting_spirit(self):
        self.assertEqual(dukedom.war(2, False, 5, 100,  88)['outcome'], 'war')   # max disatisfaction before you get deposed
        self.assertEqual(dukedom.war(2, False, 5, 100,  0 )['outcome'], 'war')
        self.assertEqual(dukedom.war(2, False, 5, 100, -6 )['outcome'], 'war')
        self.assertEqual(dukedom.war(2, False, 5, 100, -7 )['outcome'], 'peace')
        self.assertEqual(dukedom.war(2, False, 5, 100, -50)['outcome'], 'peace') # hightly supportive, well-fed population

    def test_effect_of_desperation_on_peace_casualties(self):
        for desperation in range(2, 12):
            self.assertEqual(dukedom.war(desperation, False, 1, 100, -50)['casualties'], desperation + 1)

    def test_disatisfaction_after_peace_negotiations(self):
        for desperation in range(2, 12):
            war = dukedom.war(desperation, False, 1, 100, -50)
            self.assertEqual(war['disatisfaction'], war['casualties'] * 2)


if __name__ == '__main__':
    unittest.main()

