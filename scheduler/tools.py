class Computer:
    def __init__(self, time, processors):
        self.time = time
        self.processors = processors


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
