from typing import Iterator
from collections import deque
from scheduler.instance import ProblemInstance, ProblemInstanceSolution
import copy


def solve(instance: ProblemInstance) -> ProblemInstanceSolution:
    """Solves the P||Cmax problem by using a greedy algorithm.

    :param tasks_durations: tasks_durations[process_indicator - 1] = time it takes for the task to be completed
    :param processors_number: number of available processors
    :return: py:class:`Computer` object
    """
    processors = [[0, deque([])] for _ in range(instance.processors_number)]

    for task_index, task_duration in enumerate(instance.tasks_durations):
        free_processor = min(enumerate(processors), key=lambda x: x[1][0])[0]
        processors[free_processor][0] += task_duration
        processors[free_processor][1].append(task_index)

    result_time = max(processors, key=lambda x: x[0])[0]
    result_processors = list(map(lambda x: list(x[1]), processors))

    return ProblemInstanceSolution(instance, result_processors, result_time)

__all__ = ["solve"]

