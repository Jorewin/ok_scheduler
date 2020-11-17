import unittest
import random
from scheduler import (
    brute_force_iterative,
    brute_force_recursive,
    greedy,
    generate,
    Instance,
)


class TestBruteForceIterative(unittest.TestCase):
    def test_example(self):
        instance = Instance(3, [1, 5, 2, 5, 6, 8, 1, 2])
        solution = brute_force_iterative.solve(instance)

        self.assertEqual(solution.total_time, 10)


class TestBruteForceRecursive(unittest.TestCase):
    def test_example(self):
        instance = Instance(3, [1, 5, 2, 5, 6, 8, 1, 2])
        solution = brute_force_recursive.solve(instance)

        self.assertEqual(solution.total_time, 10)


class TestGreedy(unittest.TestCase):
    def test_example(self):
        instance = Instance(3, [1, 5, 2, 5, 6, 8, 1, 2])
        solution = greedy.solve(instance)

        self.assertEqual(solution.total_time, 13)


class TestRandomDatasetsGenerator(unittest.TestCase):
    def test_example(self):
        cmax = 10
        tasks_number = 8
        processors_number = 3
        tasks_durations_range = (1, 8)
        random.seed(112997)

        instance = generate(cmax, tasks_number, processors_number, tasks_durations_range)
        solution = brute_force_recursive.solve(instance)

        self.assertEqual(solution.total_time, cmax)


if __name__ == '__main__':
    unittest.main()
