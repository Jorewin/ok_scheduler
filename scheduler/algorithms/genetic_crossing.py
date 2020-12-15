import copy
import random
from scheduler.problem import Instance, InstanceSolution
from itertools import cycle


GENERATIONS = 128

POPULATION_UNIT = 16
POPULATION_SIZE = 64

BEST_SPECIMENS = 2 * POPULATION_UNIT
SPECIMENS_IN_POPULATION = POPULATION_SIZE * BEST_SPECIMENS


class GeneticSolution:
    def __init__(self, instance, tasks_mapping):
        self.instance = instance
        self.tasks_mapping = tasks_mapping
        self.processors_times = [0 for _ in range(self.instance.processors_number)]
        for task_index, processor_index in enumerate(tasks_mapping):
            self.processors_times[processor_index] += instance.tasks_durations[task_index]

        self.max_time = max(self.processors_times)
        self.average_computation_time = sum(self.processors_times) / self.instance.processors_number

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

    def include_processor(self, other, name, index, processor, available_processors, solution):
        for task, choice in enumerate(self.tasks_mapping):
            if choice == processor:
                solution["tasks_mapping"][task] = index
                solution["processors_times"][index] = self.processors_times[choice]
                available_processors[name][other.tasks_mapping[task]] = False

    def cross(self, other):
        available_processors = {
            "self": [True for _ in range(len(self.processors_times))],
            "other": [True for _ in range(len(self.processors_times))]
        }
        best_processors = sorted(
            (
                    [("self", i, j) for i, j in enumerate(self.processors_times)] +
                    [("other", i, j) for i, j in enumerate(other.processors_times)]
            ),
            key=lambda x: x[2]
        )
        best_processors = \
            list(filter(lambda x: x[2] - self.average_computation_time >= 0, best_processors)) + \
            list(filter(lambda x: x[2] - self.average_computation_time < 0, best_processors))[::-1]
        solution = {
            "tasks_mapping": [-1 for _ in self.tasks_mapping],
            "processors_times": [0 for _ in self.processors_times]
        }
        index = 0
        for name, processor, _ in best_processors:
            if index == self.instance.processors_number - 1:
                break
            if available_processors[name][processor]:
                available_processors[name][processor] = False
                if name == "self":
                    self.include_processor(other, "other", index, processor, available_processors, solution)
                else:
                    other.include_processor(self, "self", index, processor, available_processors, solution)
                index += 1
        for task, choice in enumerate(solution["tasks_mapping"]):
            if choice == -1:
                processor = min(enumerate(solution["processors_times"]), key=lambda x: x[1])[0]
                solution["tasks_mapping"][task] = processor
                solution["processors_times"][processor] += self.instance.tasks_durations[task]
        return GeneticSolution(self.instance, solution["tasks_mapping"])

    def mutate(self):
        result = copy.deepcopy(self)
        processor_1 = random.randrange(result.instance.processors_number)
        processor_2 = random.randrange(1, result.instance.processors_number)
        processor_2 = (processor_1 + processor_2) % self.instance.processors_number
        tasks_1 = list(filter(lambda x: x[1] == processor_1, enumerate(result.tasks_mapping)))
        tasks_2 = list(filter(lambda x: x[1] == processor_2, enumerate(result.tasks_mapping)))
        if tasks_1 != []:
            index_1 = random.choice(tasks_1)[0]
        else:
            index_1 = random.randrange(len(result.tasks_mapping))
            processor_1 = result.tasks_mapping[index_1]
        if tasks_2 != []:
            index_2 = random.choice(tasks_2)[0]
        else:
            index_2 = random.randrange(len(result.tasks_mapping))
            processor_2 = result.tasks_mapping[index_2]
        result.tasks_mapping[index_1] = processor_2
        result.tasks_mapping[index_2] = processor_1
        difference = result.instance.tasks_durations[index_1] - result.instance.tasks_durations[index_2]
        result.processors_times[processor_1] -= difference
        result.processors_times[processor_2] += difference
        return result

    @staticmethod
    def random(instance):
        tasks_number = len(instance.tasks_durations)
        tasks_mapping = [0 for _ in range(tasks_number)]
        splitter = 0
        if tasks_number > instance.processors_number:
            splitter = random.randrange(tasks_number - instance.processors_number)
        for task in range(splitter):
            tasks_mapping[task] = random.randrange(instance.processors_number)
        for processor, task in enumerate(range(splitter, splitter + instance.processors_number)):
            tasks_mapping[task] = processor
        for task in range(splitter + instance.processors_number, tasks_number):
            tasks_mapping[task] = random.randrange(instance.processors_number)
        return GeneticSolution(instance, tasks_mapping)


def cross_list_of_specimens(specimens):
    result = []

    for index in range(1, len(specimens), 2):
        result.append(specimens[index - 1].cross(specimens[index]))

    return result


def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a genetic algorithm.
    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """
    population = [GeneticSolution.random(instance) for _ in range(POPULATION_SIZE)]
    for _ in range(GENERATIONS):
        best_specimens = sorted(population, key=lambda x: x.score())[:BEST_SPECIMENS]
        crossed = cross_list_of_specimens(best_specimens)
        mutated = [solution.mutate() for solution, _ in zip(cycle(crossed), range(POPULATION_SIZE - len(crossed)))]
        population = copy.deepcopy(crossed) + copy.deepcopy(mutated)
        random.shuffle(population)

    best_solution = min(population, key=lambda x: x.score())
    return best_solution.to_instance_solution()


__all__ = ["solve"]