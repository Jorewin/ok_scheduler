import unittest
from scheduler import brute_force_iterative, brute_force_recursive


class BruteForceIterative(unittest.TestCase):
	def test_example(self):
		tasks_durations = [1, 5, 2, 5, 6, 8, 1, 2]
		processors_number = 3

		result = brute_force_iterative.solve(tasks_durations, processors_number)
		print(result.time, result.processors)

		self.assertEqual(result.time, 10)


class BruteForceRecursive(unittest.TestCase):
	def test_example(self):
		tasks_durations = [1, 5, 2, 5, 6, 8, 1, 2]
		processors_number = 3

		result = brute_force_recursive.solve(tasks_durations, processors_number)
		print(result.time, result.processors)

		self.assertEqual(result.time, 10)


if __name__ == '__main__':
	unittest.main()
