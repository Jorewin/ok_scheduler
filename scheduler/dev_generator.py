import random
from scheduler.problem import Instance, InstanceSolution


def processor_filler(time: int, step: int) -> list:
    """Fills a list with randomly generated time periods

    :param time: time to which the list sums to
    :param step: minimal difference between two generated time periods
    :return:
    """
    result = []
    while time != 0:
        period = random.randrange(1, time + 1, step)
        result.append(period)
        time -= period
    return result


def generate(c_max: int, processors_number: int, step: int) -> (Instance, InstanceSolution):
    """Generates a P||Cmax problem instance.

    :param c_max: time it takes for all of the processors to finish their tasks synchronously
    :param processors_number: number of available processors
    :param step: minimal difference between two generated time periods
    :return: problem instance and it's solution
    """
    instance = Instance(processors_number, [])
    processors = []
    task_index = -1
    for _ in range(processors_number):
        offset = random.choice((0, step))
        current = processor_filler(c_max - offset, step)
        instance.tasks_durations += current
        processors.append([(task_index := task_index + 1) for _ in range(len(current))])
    return instance, InstanceSolution(instance, processors)
