from __future__ import annotations
import copy
import random
import numpy
from scheduler.problem import Instance, InstanceSolution
from itertools import cycle
from typing import Iterator


class GeneticSolution(InstanceSolution):
    """Class that provides some operations on solutions which are required by the genetic algorithm

    :ivar tasks_mapping: a reversed `processors` structure, the processors are assigned to tasks
    :type tasks_mapping: list
    :ivar average_computation_time: OPT for chosen instance is greater or equal than this attribute
    """
    def __init__(self, instance: Instance, tasks_mapping: list, processors: list = None):
        """Creates an :py:class:`GeneticSolution: object

        :param instance: P||Cmax problem instance
        :param tasks_mapping: a reversed `processors` structure, the processors are assigned to tasks
        :param processors: list of processors with tasks allocated to them
        """
        if processors is None:
            processors = [[] for _ in range(instance.processors_number)]
            for task, processor in enumerate(tasks_mapping):
                processors[processor].append(task)

        self.tasks_mapping = tasks_mapping
        self.average_computation_time = sum(instance.tasks_durations) / instance.processors_number
        super().__init__(instance, processors)

    def to_instance_solution(self) -> InstanceSolution:
        """Reduces the solution to its base class.
        
        :return:
        """
        return InstanceSolution(self.instance, self.processors)

    def include_processor(
            self, other: GeneticSolution, result_p_index: int, p_index: int,
            available_processors: list, tasks_mapping: list, processors: list
    ):
        """Finds tasks assigned to a processor chosen by `p_index` and marks this relation in both `task_mapping`
        and `processors`. Processors from other solutions that have one or more of chosen tasks are marked as unusable
        for further operations.
        
        :param other: other solution 
        :param result_p_index: index of a processor to which the chosen tasks will be assigned
        :param p_index: index of a requested processor
        :param available_processors: processors that can still be used in the future
        :param tasks_mapping: a reversed `processors` structure, the processors are assigned to tasks
        :param processors: list of processors with tasks allocated to them
        """
        for task_index, assigned_processor in enumerate(self.tasks_mapping):
            if assigned_processor == p_index:
                tasks_mapping[task_index] = result_p_index
                processors[result_p_index].append(task_index)
                available_processors[other.tasks_mapping[task_index]] = False

    def cross(self, other: GeneticSolution) -> GeneticSolution:
        """Performs a crossing operation on two solutions.

        :param other: other solution
        :return: generated solution
        """
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
        result_p_index = 0
        for name, p_index, _ in best_processors:
            if result_p_index == self.instance.processors_number - 1:
                break
            if available_processors[name][p_index]:
                available_processors[name][p_index] = False
                if name == "self":
                    self.include_processor(
                        other, result_p_index, p_index, available_processors["other"], task_mapping, processors
                    )
                else:
                    other.include_processor(
                        self, result_p_index, p_index, available_processors["self"], task_mapping, processors
                    )
                result_p_index += 1
        for t_index, assigned_processor in enumerate(task_mapping):
            if assigned_processor == -1:
                p_index = min(enumerate(processors), key=lambda x: len(x[1]))[0]
                task_mapping[t_index] = p_index
                processors[p_index].append(t_index)
        return GeneticSolution(self.instance, task_mapping, processors=processors)

    def mutate(self, weights: list = None) -> GeneticSolution:
        """Performs a mutation on a solution.

        :param weights: probability distribution for the random function
        :return: generated solution
        """
        tasks_mapping = copy.deepcopy(self.tasks_mapping)
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
    def random(instance: Instance) -> GeneticSolution:
        """Creates a random solution.

        :param instance: P||Cmax problem instance
        :return: generated solution
        """
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


def solution_generator(
        instance: Instance, population_size: int, best_specimens_number: int
) -> Iterator[GeneticSolution]:
    """Yields the best solution every generation cycle.

    :param instance: P||Cmax problem instance
    :param population_size: size of the population
    :param best_specimens_number: defines the size of a group that population is reduced to
    :return: generator that yields py:class:`InstanceSolution` objects
    """
    population = [GeneticSolution.random(instance) for _ in range(population_size)]
    weights = [i**10 for i in range(1, instance.processors_number + 1)]
    sigma = sum(weights)
    weights = list(map(lambda x: x / sigma, weights))
    while True:
        best_specimens = sorted(population, key=lambda x: x.total_time)[:best_specimens_number]
        crossed = best_specimens[:1] + [
            best_specimens[i - 1].cross(best_specimens[i]) for i in range(2, best_specimens_number, 2)
        ]
        mutated = [
            solution.mutate(weights=weights) for solution, _ in
            zip(cycle(crossed), range(population_size - len(crossed)))
        ]
        population = crossed + mutated
        best_solution = min(population, key=lambda x: x.total_time)
        yield InstanceSolution(instance, best_solution.processors)


def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a genetic algorithm and default parameters.
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


__all__ = ["solve", "solution_generator"]
