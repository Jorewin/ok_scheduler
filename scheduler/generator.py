from scheduler.problem import Instance
from scheduler.exceptions import IncorrectGeneratorDatasetError
import math
import random


def generate_list_which_sums_to_value(sum_value: int, list_length: int, elements_range: (int, int)) -> list:
    """Function generates a list of given length
    and fills it with randomly generated elements from a range
    whose sum is equal to a given value.

    :param sum_value:
    :param list_length:
    :param elements_range: tuple in format (min, max) which indicate a closed range
    :raise IncorrectGeneratorDatasetError: if it's not possible to generate such list
    :return: generated list
    """

    element_value_min, element_value_max = elements_range

    # Checking constraints
    if not (element_value_min * list_length <= sum_value <= element_value_max * list_length):
        raise IncorrectGeneratorDatasetError('Sum is out of possible ranges')

    result_list = [element_value_min] * list_length
    remaining = sum_value - element_value_min * list_length
    for index in range(list_length - 1):
        increase = random.randint(0, min(remaining, element_value_max))
        result_list[index] += increase
        remaining -= increase

    result_list[-1] += remaining

    return result_list


def generate(cmax: int, tasks_number: int, processors_number: int, task_duration_max: int) -> Instance:
    """Function generate a dataset for P||Cmax problem

    :param cmax: Total time of execution of all tasks
    :param tasks_number: Number of tasks that should be generated
    :param processors_number: Number of processors on which tasks will be executed
    :param task_duration_max: Max value of task duration
    as a tuple (min, max)
    :return: Generated problem instance
    """

    # Set up some necessary values
    tasks_rectangle_width = cmax - 1
    tasks_in_rectangle = tasks_number - 1
    total_length_of_rest_of_tasks = processors_number * tasks_rectangle_width
    
    max_tasks_per_processor = math.floor(tasks_rectangle_width / 2)
    min_tasks_per_processor = math.ceil(tasks_rectangle_width / task_duration_max)
    tasks_per_processor_range = (min_tasks_per_processor, max_tasks_per_processor)
   
    # Checking some constraints
    if not (2 * tasks_in_rectangle <= total_length_of_rest_of_tasks <= task_duration_max * tasks_in_rectangle):
        raise IncorrectGeneratorDatasetError('Cmax is out of possible ranges')

    result_list = [1]

    tasks_per_procesor = generate_list_which_sums_to_value(tasks_in_rectangle, processors_number, tasks_per_processor_range)
    for tasks_number in tasks_per_procesor:
        result_list += generate_list_which_sums_to_value(tasks_rectangle_width, tasks_number, (2, task_duration_max))


    random.shuffle(result_list)

    return Instance(processors_number, result_list)

