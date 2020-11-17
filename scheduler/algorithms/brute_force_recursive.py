from scheduler.problem import Instance, InstanceSolution
from typing import Iterator


def generate_partitions(whole_list: list, partitions_number: int) -> Iterator[list]:
    """Generator function which yields all possible partitions of the list
    to a given number of sublists

    :param whole_list: the list for which partitions are being generated
    :param partitions_number: number of partitions in which whole_list is divided
    """
    if partitions_number == 1:
        yield [whole_list]
    elif len(whole_list) == partitions_number:
        yield list(map(lambda x: [x], whole_list))
    else:
        element, *rest_of_list = whole_list

        for partition in generate_partitions(rest_of_list, partitions_number - 1):
            yield [*partition, [element]]

        for partition in generate_partitions(rest_of_list, partitions_number):
            for n in range(partitions_number):
                yield partition[:n] + [partition[n] + [element]] + partition[n + 1:]


def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using an iterative version of a brute force algorithm.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """
    
    tasks_indexes = list(range(len(instance.tasks_durations)))
    all_possible_partitions = generate_partitions(tasks_indexes, instance.processors_number)
    solutions = map(lambda p: InstanceSolution(instance, p), all_possible_partitions)
    best_solution = min(solutions, key=lambda s: s.total_time)

    return best_solution


__all__ = ["solve"]

