import copy
import random
import numpy
from scheduler.problem import Instance, InstanceSolution
from itertools import cycle


class GeneticSolution(InstanceSolution):
    def __init__(self, instance, tasks_mapping, processors=None):
        if processors is None:
            processors = [[] for _ in range(instance.processors_number)]
            for task, processor in enumerate(tasks_mapping):
                processors[processor].append(task)

        self.tasks_mapping = tasks_mapping
        self.average_computation_time = sum(instance.tasks_durations) / instance.processors_number
        super().__init__(instance, processors)

    @staticmethod
    def from_instance_solution(solution):
        tasks_mapping = [0] * len(solution.instance.tasks_durations)
        for processor_index, tasks in enumerate(solution.processors):
            for task_index in tasks:
                tasks_mapping[task_index] = processor_index

        return GeneticSolution(solution.instance, tasks_mapping, processors=solution.processors)

    def to_instance_solution(self):
        return InstanceSolution(self.instance, self.processors)

    def include_processor(self, other, solution_p_index, p_index, available_processors, tasks_mapping, processors):
        for task_index, assigned_processor in enumerate(self.tasks_mapping):
            if assigned_processor == p_index:
                tasks_mapping[task_index] = solution_p_index
                processors[solution_p_index].append(task_index)
                available_processors[other.tasks_mapping[task_index]] = False

    def cross(self, other):
        available_processors = {
            "self": [True for _ in range(self.instance.processors_number)],
            "other": [True for _ in range(self.instance.processors_number)]
        }
        best_processors = sorted(
            filter(
                lambda x: (x[2] - self.average_computation_time) >= 0,
                [("self", i, j) for i, j in enumerate(map(sum, self))] +
                [("other", i, j) for i, j in enumerate(map(sum, self))]
            ),
            key=lambda x: x[2]
        )
        task_mapping = [-1 for _ in self.tasks_mapping]
        processors = [[] for _ in range(self.instance.processors_number)]
        solution_p_index = 0
        for name, p_index, _ in best_processors:
            if solution_p_index == self.instance.processors_number - 1:
                break
            if available_processors[name][p_index]:
                available_processors[name][p_index] = False
                if name == "self":
                    self.include_processor(
                        other, solution_p_index, p_index, available_processors["other"], task_mapping, processors
                    )
                else:
                    other.include_processor(
                        self, solution_p_index, p_index, available_processors["self"], task_mapping, processors
                    )
                solution_p_index += 1
        for t_index, assigned_processor in enumerate(task_mapping):
            if assigned_processor == -1:
                p_index = min(enumerate(processors), key=lambda x: len(x[1]))[0]
                task_mapping[t_index] = p_index
                processors[p_index].append(t_index)
        return GeneticSolution(self.instance, task_mapping, processors=processors)

    def mutate(self, weights=None):
        tasks_mapping = copy.deepcopy(self.tasks_mapping)
        # processor_1 = random.randrange(self.instance.processors_number)
        processor_1, = numpy.random.default_rng().choice(
            self.instance.processors_number, size=1, replace=False, p=weights, shuffle=False
        )
        processor_2 = random.randrange(1, self.instance.processors_number)
        processor_2 = (processor_1 + processor_2) % self.instance.processors_number
        if self.processors[processor_1] != []:
            index_1 = random.choice(self.processors[processor_1])
            tasks_mapping[index_1] = processor_2
        if self.processors[processor_2] != []:
            index_2 = random.choice(self.processors[processor_2])
            tasks_mapping[index_2] = processor_1
        return GeneticSolution(self.instance, tasks_mapping)

    @staticmethod
    def random(instance):
        tasks_number = len(instance.tasks_durations)
        tasks_mapping = [0 for _ in range(tasks_number)]
        splitter = -instance.processors_number
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


def solution_generator(instance, population_size, best_specimens_number):
    population = [GeneticSolution.random(instance) for _ in range(population_size)]
    weights = [i**10 for i in range(1, instance.processors_number + 1)]
    sigma = sum(weights)
    weights = list(map(lambda x: x / sigma, weights))
    while True:
        best_specimens = sorted(population, key=lambda x: x.total_time)[:best_specimens_number]
        crossed = cross_list_of_specimens(best_specimens)
        mutated = [
            solution.mutate(weights=weights) for solution, _ in
            zip(cycle(crossed), range(population_size - len(crossed)))
        ]
        population = crossed + mutated
        best_solution = min(population, key=lambda x: x.total_time)
        yield best_solution


def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a genetic algorithm.
    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """
    generations = 512
    population_size = 128
    best_specimens_number = 32
    generator = solution_generator(instance, population_size, best_specimens_number)
    best_solution = GeneticSolution(instance, [0 for _ in range(len(instance.tasks_durations))])
    for _, solution in zip(range(generations), generator):
        best_solution = min(best_solution, solution, key=lambda x: x.total_time)
    return best_solution.to_instance_solution()


# __all__ = ["solve", "solution_generator", "GeneticSolution"]
