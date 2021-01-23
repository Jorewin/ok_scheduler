import scheduler
from scheduler.problem import Instance, InstanceSolution
from collections import deque


def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a LPT algorithm.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """

    transformed_instance = Instance(
        instance.processors_number,
        list(sorted(instance.tasks_durations, reverse=True))
    )

    return scheduler.greedy.solve(transformed_instance)

__all__ = ["solve"]

