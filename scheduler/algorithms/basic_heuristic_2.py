import copy
import random
from scheduler import greedy
from scheduler.problem import Instance, InstanceSolution
from collections import deque

GENERATIONS_NUMBER = 16
GENERATION_SIZE = 64
BEST_SPECIMENS = 16
MUTATION_PROBABILITY = 1




def optimize_by_index(callback, iterable):
    return callback(enumerate(iterable), key=lambda e: e[1])[0]

def min_index(iterable):
    return optimize_by_index(min, iterable)

def max_index(iterable):
    return optimize_by_index(max, iterable)



def swap_two_random_elements_between_lists(list_1: list, list_2: list):
    if len(list_1) > 0 and len(list_2) > 0:
        index_1 = random.randrange(len(list_1))
        index_2 = random.randrange(len(list_2))
       
        value = list_1[index_1]
        list_1[index_1] = list_2[index_2]
        list_2[index_2] = value


def generate_initial_solutions(instance: InstanceSolution) -> list:
    greedy_solution = greedy.solve(instance)
    return [mutate(copy.deepcopy(greedy_solution)) for _ in range(GENERATION_SIZE)]

def mutate(solution: InstanceSolution) -> InstanceSolution:
    if random.random() < MUTATION_PROBABILITY:
        processors = solution.processors
        old_processor = random.choice(processors)
        new_processor = random.choice(processors)
        if len(old_processor) > 0:
            task = old_processor.pop()
            new_processor.append(task)
            return InstanceSolution(solution.instance, processors)

    return solution

def score(solution: InstanceSolution) -> int:
    return solution.total_time

def cross(solution: InstanceSolution) -> InstanceSolution:
    # It crosses itself
    # TODO: optimize by storing sums

    times = list(map(sum, solution))
    shortest_index = min_index(times)
    longest_index = max_index(times)

    shortest_processor = solution.processors[shortest_index]
    longest_processor = solution.processors[longest_index]

    swap_two_random_elements_between_lists(shortest_processor, longest_processor)
    return InstanceSolution(solution.instance, solution.processors)

def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a basic heuristic.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """

    generation = generate_initial_solutions(instance)

    for _ in range(GENERATIONS_NUMBER):
        best_specimens = sorted(generation, key=score)[:BEST_SPECIMENS]
        best_specimens = list(map(cross, best_specimens))
        generation = sum([copy.deepcopy(best_specimens) for _ in range(GENERATION_SIZE // BEST_SPECIMENS)], [])
        generation = list(map(mutate, generation))

    return min(generation, key=score)


__all__ = ["solve"]

