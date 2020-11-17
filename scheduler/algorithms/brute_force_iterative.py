from scheduler.problem import Instance, InstanceSolution
from typing import Iterator


class Lists:
    def __init__(self, number):
        self.current = 0
        self.number = number
        self.used = -1
        self.storage = []

    def reset(self):
        self.current = 0

    def next(self):
        if self.current < self.number - 1:
            self.current += 1
            return True
        return False

    def previous(self):
        if self.current > 0:
            self.current -= 1
            return True
        return False

    def get_current(self):
        return self.storage[self.current]

    def set_current(self, value):
        self.storage[self.current] = value


class Tasks(Lists):
    """Class that simplifies operations on the tasks list.

    :ivar current: current task index
    :type current: int
    :ivar number: total number of tasks
    :type number: int
    :ivar storage: storage[task_index] = last processor that was assigned to the process
    :ivar storage: list
    """
    def __init__(self, n_tasks):
        super().__init__(n_tasks)
        self.storage = [-1 for _ in range(n_tasks)]

    def free(self):
        return self.number - self.current + 1


class Processors(Lists):
    """Class that simplifies operations on the processors list.

        :ivar current: current processor index
        :type current: int
        :ivar number: total number of processors
        :type number: int
        :ivar used: number of processors that have at least one task assigned to them
        :ivar storage: storage[processor_index] = list of tasks that are currently assigned to the processor
        :ivar storage: list
        """
    def __init__(self, n_processors):
        super().__init__(n_processors)
        self.storage = [[] for _ in range(n_processors)]

    def free(self):
        return self.number - self.used

    def add_to_current(self, value):
        if len(self.storage[self.current]) == 0 and self.used < self.number - 1:
            self.used += 1
        self.storage[self.current].append(value)

    def pop_from_current(self):
        result = self.storage[self.current].pop()
        if len(self.storage[self.current]) == 0 and self.used > 0:
            self.used = self.current - 1
        return result

    def len_current(self):
        return len(self.storage[self.current])


def brute_generator(tasks_number: int, processors_number: int) -> Iterator[list]:
    """Yields all of the possible combinations of process assignment.

    :param tasks_number:
    :param processors_number:
    :return: list of processors with tasks assigned to them
    """
    tasks = Tasks(tasks_number)
    processors = Processors(processors_number)
    lower_bound = True
    upper_bound = True

    while lower_bound:
        if not upper_bound:
            yield [list(processor) for processor in processors.storage]
            upper_bound = True
            continue

        if tasks.get_current() == -1:
            if tasks.free() > processors.free():
                processors.reset()
            else:
                processors.current = processors.used
                processors.next()
            tasks.set_current(processors.current)
            processors.add_to_current(tasks.current)
            upper_bound = tasks.next()
            continue

        processors.current = tasks.get_current()
        if processors.len_current() == 1 or processors.current == processors.number - 1:
            tasks.set_current(-1)
            processors.pop_from_current()
            lower_bound = tasks.previous()
        else:
            processors.pop_from_current()
            processors.next()
            tasks.set_current(processors.current)
            processors.add_to_current(tasks.current)
            upper_bound = tasks.next()


def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using an iterative version of a brute force algorithm.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """
    all_possible_partitions = brute_generator(len(instance.tasks_durations), instance.processors_number)
    solutions = map(lambda p: InstanceSolution(instance, p), all_possible_partitions)
    best_solution = min(solutions, key=lambda s: s.total_time)

    return best_solution


__all__ = ["solve"]
