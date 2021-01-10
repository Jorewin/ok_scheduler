import copy
import random
import scheduler
from scheduler.problem import Instance, InstanceSolution
from collections import deque


GENERATIONS_NUMBER = 128
GENERATION_SIZE = 256
BEST_SPECIMENS = 8
MUTATION_PROBABILITY = 0.1


def run_by_index(callback, iterable):
    return callback(enumerate(iterable), key=lambda e: e[1])

def min_index(iterable):
    return run_by_index(min, iterable)[0]

def max_index(iterable):
    return run_by_index(max, iterable)[0]

def sort_by_index(iterable):
    return list(map(lambda x: x[0], iterable))

def swap_elements_between_lists(first_list, first_index, second_list, second_index):
    value = first_list[first_index]
    first_list[first_index] = second_list[second_index]
    second_list[second_index] = value

def move_element_between_lists(first_list, first_index, second_list):
    swap_elements_between_lists(first_list, first_index, first_list, -1)
    value = first_list.pop()
    second_list.append(value)


class GeneticSolution(InstanceSolution):
    def __init__(self, initial: InstanceSolution):
        self.instance = initial.instance
        self.processors = initial.processors
        self.total_time = initial.total_time

        self.sums = list(map(sum, self))
        # TODO: optimize to not doing max()
        # self.sums_order = sort_by_index(self.sums)


    def mutate(self):
        if random.random() < MUTATION_PROBABILITY:
            first_index = random.randrange(len(self.processors))
            second_index = random.randrange(len(self.processors))

            if len(self.processors[first_index]) > 0 and len(self.processors[second_index]) > 0:
                first_task_index = random.randrange(len(self.processors[first_index]))
                #second_task_index = random.randrange(len(self.processors[second_index]))
                self.move_task(first_index, first_task_index, second_index)

    def cross(self):
        shortest_processor_index = min_index(self.sums)
        longest_processor_index = max_index(self.sums)

        shortest_task_index = random.randrange(len(self.processors[shortest_processor_index]))
        longest_task_index = random.randrange(len(self.processors[longest_processor_index]))

        #shortest_task_index = min_index(self.processors[shortest_processor_index])
        #longest_task_index = max_index(self.processors[longest_processor_index])

        self.swap_tasks(
            shortest_processor_index, shortest_task_index,
            longest_processor_index, longest_task_index
        )

    def score(self):
        return self.total_time


    def move_task(self, old_processor_index, first_task_index, new_processor_index):
        old_processor = self.processors[old_processor_index]
        new_processor = self.processors[new_processor_index]

        task = old_processor[first_task_index]

        task_duration = self.instance.tasks_durations[task]
        self.sums[old_processor_index] -= task_duration
        self.sums[new_processor_index] += task_duration
        self.total_time = max(self.sums)

        move_element_between_lists(old_processor, first_task_index, new_processor)


    def swap_tasks(self, first_processor_index, first_task_index, second_processor_index, second_task_index):
        first_processor = self.processors[first_processor_index]
        second_processor = self.processors[second_processor_index]

        first_task = first_processor[first_task_index]
        second_task = second_processor[second_task_index]

        first_processor[first_task_index] = second_task
        second_processor[second_task_index] = first_task

        first_task_duration = self.instance.tasks_durations[first_task]
        second_task_duration = self.instance.tasks_durations[second_task]

        self.sums[first_processor_index] += second_task_duration - first_task_duration
        self.sums[second_processor_index] += first_task_duration - second_task_duration
        self.total_time = max(self.sums)

    
def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a basic heuristic.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """

    greedy_solution = scheduler.lpt.solve(instance)
    best_specimens = [GeneticSolution(copy.deepcopy(greedy_solution)) for _ in range(BEST_SPECIMENS)]

    for _ in range(GENERATIONS_NUMBER):
        generation = sum([copy.deepcopy(best_specimens) for _ in range(GENERATION_SIZE // BEST_SPECIMENS)], [])
        for specimen in generation:
            specimen.mutate()

        best_specimens = sorted(generation, key=lambda s: s.score())[:BEST_SPECIMENS]
        for specimen in generation:
            specimen.cross()

    return best_specimens[0]


__all__ = ["solve"]

