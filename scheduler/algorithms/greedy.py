from scheduler.problem import Instance, InstanceSolution
from collections import deque


def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a greedy algorithm.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """
    processors = [[0, deque([])] for _ in range(instance.processors_number)]

    for task_index, task_duration in enumerate(instance.tasks_durations):
        free_processor = min(enumerate(processors), key=lambda x: x[1][0])[0]
        processors[free_processor][0] += task_duration
        processors[free_processor][1].append(task_index)

    result_processors = list(map(lambda x: list(x[1]), processors))

    return InstanceSolution(instance, result_processors)


__all__ = ["solve"]

