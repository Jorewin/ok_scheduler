import copy
import random
from scheduler.problem import Instance, InstanceSolution

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
                print(list(enumerate(solution["processors_times"])))
                solution["tasks_mapping"][task] = processor
                solution["processors_times"][processor] += self.instance.tasks_durations[task]
        return GeneticSolution(self.instance, solution["tasks_mapping"])

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
        for specimen in crossed:
            if random.random() < 0.112 / 0.997:
                specimen.mutate()

        population = sum([copy.deepcopy(crossed) for _ in range(POPULATION_SIZE)], [])
        random.shuffle(population)

    best_solution = min(population, key=lambda x: x.score())
    return best_solution.to_instance_solution()


__all__ = ["solve"]