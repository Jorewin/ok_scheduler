import copy
import random
from scheduler import greedy
from scheduler.problem import Instance, InstanceSolution
from collections import deque

GENERATIONS = 128

POPULATION_UNIT = 16
POPULATION_SIZE = 64

BEST_SPECIMENS = 2 * POPULATION_UNIT
SPECIMENS_IN_POPULATION = POPULATION_SIZE * BEST_SPECIMENS


class GeneticSolution:
    def __init__(self, instance, tasks_mapping):
        self.instance = instance
        self.tasks_mapping = tasks_mapping

        self.processors_times = [0] * self.instance.processors_number
        for task_index, processor_index in enumerate(tasks_mapping):
            self.processors_times[processor_index] += instance.tasks_durations[task_index]

        self.max_time = max(self.processors_times)

    @staticmethod
    def from_instance_solution(solution):
        tasks_mapping = [0] * len(solution.instance.tasks_durations)
        for processor_index, tasks in enumerate(solution.processors):
            for task_index in tasks:
                tasks_mapping[task_index] = processor_index

        return GeneticSolution(solution.instance, tasks_mapping)

    def to_instance_solution(self):
        processors = [[] for _ in range(self.instance.processors_number)]
        for task_index, processor_index in enumerate(self.tasks_mapping):
            processors[processor_index].append(task_index)

        return InstanceSolution(self.instance, processors)

    def score(self):
        return self.max_time

    def cross(self, other):
        result = [0] * len(self.tasks_mapping)
        result[::2] = self.tasks_mapping[::2]
        result[1::2] = other.tasks_mapping[1::2]

        return GeneticSolution(self.instance, result)

    def mutate(self):
        task_index = random.randrange(len(self.instance.tasks_durations))
        processor_index = random.randrange(self.instance.processors_number)

        task_duration = self.instance.tasks_durations[task_index]

        previous_processor_index = self.tasks_mapping[task_index]
        self.tasks_mapping[task_index] = processor_index

        self.processors_times[previous_processor_index] -= task_duration
        self.processors_times[processor_index] += task_duration
        self.max_time = max(self.processors_times)

    @staticmethod
    def random(instance):
        tasks_number = len(instance.tasks_durations)
        tasks_mapping = [random.randrange(instance.processors_number) for _ in range(tasks_number)]
        return GeneticSolution(instance, tasks_mapping)


def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a genetic algorithm.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """
    population = [GeneticSolution.random(instance) for _ in range(POPULATION_SIZE)]
    for _ in range(GENERATIONS):
        best_specimens = sorted(population, key=lambda x: x.score())[:BEST_SPECIMENS]
        best_specimen = best_specimens[0]
        for index, specimen in enumerate(best_specimens[1:], 1):
            best_specimens[index] = best_specimens[index].cross(best_specimen)


        for specimen in best_specimens:
            if random.random() < 0.112 / 0.997:
                specimen.mutate()

        population = sum([copy.deepcopy(best_specimens) for _ in range(POPULATION_SIZE)], [])
        random.shuffle(population)

    best_solution = min(population, key=lambda x: x.score())
    return best_solution.to_instance_solution()


__all__ = ["solve"]

