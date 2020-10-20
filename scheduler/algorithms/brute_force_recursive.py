from typing import Iterator
from scheduler.tools import Computer, calculate_time
import copy


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


# This version returns tasks durations instead of their ids
# def solve(tasks_durations: list, processors_number: int) -> Computer:
#     """Solves the P||Cmax problem by using a recursive version of a brute-force algorithm.
#
#     :param tasks_durations: list of positive integers that represent durations of consecutive tasks
#     :param processors_number: number of available processors
#     :return: py:class:`Computer` object
#     """
#     partitions = generate_partitions(tasks_durations, processors_number)
#
#     obtain_partition_result_time = lambda p: max(map(sum, p))
#     partitions_with_result_times = map(lambda p: (p, obtain_partition_result_time(p)), partitions)
#     result_processors, result_time = min(partitions_with_result_times, key=lambda x: x[1])
#
#     return Computer(result_time, result_processors)


def solve(tasks_durations: list, processors_number: int) -> Computer:
    """Solves the P||Cmax problem by using an iterative version of a brute force algorithm.

    :param tasks_durations: tasks_durations[process_indicator - 1] = time it takes for the task to be completed
    :param processors_number: number of available processors
    :return: py:class:`Computer` object
    """
    if processors_number <= 0:
        return Computer(0, [])
    result_time = 0
    result_processors = []
    for processors in generate_partitions([i + 1 for i in range(len(tasks_durations))], processors_number):
        current_time = calculate_time(tasks_durations, processors)
        if current_time < result_time or result_time == 0:
            result_time, result_processors = current_time, copy.deepcopy(processors)
    return Computer(result_time, result_processors)


__all__ = ["solve"]
