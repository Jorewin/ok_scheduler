from scheduler.objects import Computer
from typing import Iterator
import copy


class Tasks:
    """Class that simplifies operations on the tasks list.

    :ivar current: current process indicator
    :type current: int
    :ivar number: total number of tasks
    :type number: int
    :ivar storage: storage[process_indicator - 1] = last processor that was assigned to the process
    :ivar storage: list
    """
    def __init__(self, n_tasks):
        self.current = 1
        self.number = n_tasks
        self.storage = [0 for _ in range(n_tasks)]

    def get_current(self):
        return self.storage[self.current - 1]

    def set_current(self, value):
        self.storage[self.current - 1] = value

    def free(self):
        return self.number - self.current + 1

    def next(self):
        self.current += 1

    def previous(self):
        self.current -= 1

    def __repr__(self):
        return f"Current: {self.current} | Free: {self.free()} | Number: {self.number} | Storage: {self.storage}"


class Processors:
    """Class that simplifies operations on the processors list.

        :ivar current: current processor indicator
        :type current: int
        :ivar number: total number of processors
        :type number: int
        :ivar used: number of processors that have at least one process assigned to them
        :ivar storage: storage[processor_indicator - 1] = list of tasks that are currently assigned to the processor
        :ivar storage: list
        """
    def __init__(self, n_processors):
        self.current = 1
        self.number = n_processors
        self.used = 0
        self.storage = [[] for _ in range(n_processors)]

    def free(self):
        return self.number - self.used

    def reset(self):
        self.current = 1

    def next(self):
        if self.current < self.number:
            self.current += 1

    def previous(self):
        if self.current > 1:
            self.current -= 1

    def add_to_current(self, value):
        if len(self.storage[self.current - 1]) == 0 and self.used < self.number:
            self.used += 1
        self.storage[self.current - 1].append(value)

    def pop_from_current(self):
        result = self.storage[self.current - 1].pop()
        if len(self.storage[self.current - 1]) == 0 and self.used > 1:
            self.used = self.current - 1
        return result

    def len_current(self):
        return len(self.storage[self.current - 1])

    def __repr__(self):
        return f"Current: {self.current} | Free: {self.free()} | Number: {self.number} | Storage: {self.storage}"


def brute_generator(tasks_number: int, processors_number: int) -> Iterator[list]:
    """Yields all of the possible combinations of process assignment.

    :param tasks_number:
    :param processors_number:
    :return: list of processors with tasks assigned to them
    """
    tasks = Tasks(tasks_number)
    processors = Processors(processors_number)

    while tasks.current != 0:
        if tasks.current > tasks.number:
            yield processors.storage
            tasks.previous()
            continue

        if tasks.get_current() == 0:
            if tasks.free() > processors.free():
                processors.reset()
            else:
                processors.current = processors.used
                processors.next()
            tasks.set_current(processors.current)
            processors.add_to_current(tasks.current)
            tasks.next()
            continue

        processors.current = tasks.get_current()
        if processors.len_current() == 1 or processors.current >= processors.number:
            tasks.set_current(0)
            processors.pop_from_current()
            tasks.previous()
        else:
            processors.pop_from_current()
            processors.next()
            tasks.set_current(processors.current)
            processors.add_to_current(tasks.current)
            tasks.next()


def calculate_time(tasks_durations: list, processors: list) -> int:
    """Calculates the time, it takes for the processors to do their tasks synchronously.

    :param tasks_durations: tasks_durations[process_indicator - 1] = time it takes for the task to be completed
    :param processors: combination of process assignments
    :return: calculated time
    """
    result_time = 0
    for processor in processors:
        current_time = sum(map(lambda x: tasks_durations[x - 1], processor))
        result_time = max(current_time, result_time)
    return result_time


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
    for processors in brute_generator(len(tasks_durations), processors_number):
        current_time = calculate_time(tasks_durations, processors)
        if current_time < result_time or result_time == 0:
            result_time, result_processors = current_time, copy.deepcopy(processors)
    return Computer(result_time, result_processors)


__all__ = ["solve"]
