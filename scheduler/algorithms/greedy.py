from typing import Iterator
from collections import deque
from scheduler.tools import Computer, calculate_time
import copy


def solve(tasks_durations: list, processors_number: int) -> Computer:
    """Solves the P||Cmax problem by using a greedy algorithm.

    :param tasks_durations: tasks_durations[process_indicator - 1] = time it takes for the task to be completed
    :param processors_number: number of available processors
    :return: py:class:`Computer` object
    """
    processors = [[0, deque([])] for _ in range(processors_number)]

    for task_index, task_duration in enumerate(tasks_durations):
        free_processor = min(enumerate(processors), key=lambda x: x[1][0])[0]
        processors[free_processor][0] += task_duration
        processors[free_processor][1].append(task_index + 1)

    result_time, result_processors = max(processors, key=lambda x: x[0])
    return Computer(result_time, list(result_processors))


__all__ = ["solve"]
