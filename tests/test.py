import unittest
from scheduler import brute_force_iterative, brute_force_recursive, greedy


class TestBruteForceIterative(unittest.TestCase):
    def test_example(self):
        tasks_durations = [1, 5, 2, 5, 6, 8, 1, 2]
        processors_number = 3

        result = brute_force_iterative.solve(tasks_durations, processors_number)

        self.assertEqual(result.time, 10)


class TestBruteForceRecursive(unittest.TestCase):
    def test_example(self):
        tasks_durations = [1, 5, 2, 5, 6, 8, 1, 2]
        processors_number = 3

        result = brute_force_recursive.solve(tasks_durations, processors_number)

        self.assertEqual(result.time, 10)

class TestGreedy(unittest.TestCase):
    def test_example(self):
        tasks_durations = [1, 5, 2, 5, 6, 8, 1, 2]
        processors_number = 3

        result = greedy.solve(tasks_durations, processors_number)

        self.assertEqual(result.time, 13)

if __name__ == '__main__':
    unittest.main()
