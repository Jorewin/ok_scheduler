import unittest
import random
from scheduler import (
    brute_force_iterative,
    brute_force_recursive,
    greedy,
    generate
)


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


class TestRandomDatasetsGenerator(unittest.TestCase):
    def test_example(self):
        cmax = 10
        tasks_number = 8
        processors_number = 3
        tasks_durations_range = (1, 8)

        random.seed(112997)
        tasks_durations = generate(cmax, tasks_number, processors_number, tasks_durations_range)
        result = brute_force_recursive.solve(tasks_durations, processors_number)

        self.assertEqual(result.time, cmax)


if __name__ == '__main__':
    unittest.main()
