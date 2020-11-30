import copy
import random
from scheduler import greedy
from scheduler.problem import Instance, InstanceSolution
from collections import deque

generations_number = 100
generation_size = 500
best_specimens_number = 1
swapped_pairs = 5

def swap_two_random_elements_between_lists(list_1: list, list_2: list):
    index_1 = random.randrange(len(list_1))
    index_2 = random.randrange(len(list_2))
   
    value = list_1[index_1]
    list_1[index_1] = list_2[index_2]
    list_2[index_2] = value

def mutate(solution: InstanceSolution) -> InstanceSolution:
    # It only swaps two tasks between processors at the moment

    processors = copy.deepcopy(solution.processors)
    processor_1 = random.choice(processors)
    processor_2 = random.choice(processors)
    for _ in range(swapped_pairs):
        swap_two_random_elements_between_lists(processor_1, processor_2)

    return InstanceSolution(solution.instance, processors)

def score(solution: InstanceSolution) -> int:
    return solution.total_time

def cross(solution: list):
    return solution[0]

def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a genetic algorithm.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """
    best_solution = greedy.solve(instance)
    for _ in range(generations_number):
        generation = [mutate(best_solution) for _ in range(generation_size)]
        best_specimens = sorted(generation, key=score)[:best_specimens_number]
        best_solution = cross(best_specimens)

    return best_solution


__all__ = ["solve"]

