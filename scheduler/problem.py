from .exceptions import FileContentError


class Instance:
    """A class used for operations on instances of P||Cmax problem.

    :ivar processors_number: number of available processors
    :type processors_number: int
    :ivar tasks_durations: tasks_durations[process_indicator] = time it takes for the task to be completed
    :type tasks_durations: list
    """
    def __init__(self, processors_number: int, tasks_durations: list):
        """Creates a py:class:`ProblemInstance` object.

        :param processors_number: number of available processors
        :param tasks_durations: tasks_durations[process_indicator] = time it takes for the task to be completed
        """
        if processors_number <= 0:
            raise ValueError(f"number of processors must be > 0, not ({processors_number})")
        self.processors_number = processors_number
        self.tasks_durations = tasks_durations


class InstanceSolution:
    """A class used for operations on solutions of a P||Cmax problem instances.

    :ivar instance: P||Cmax problem instance
    :type instance: py:class:`Instance`
    :ivar processors: list of processors with tasks allocated to them
    :type processors: list
    """
    def __init__(self, instance: Instance, processors: list):
        """Creates an py:class:`Solution` object.

        :param instance: P||Cmax problem instance
        :param processors: list of processors with tasks allocated to them
        """
        self.instance = instance
        self.processors = processors
        self.total_time = max(map(sum, self))

    def __len__(self):
        """Returns the processors number."""
        return self.instance.processors_number

    def __iter__(self):
        """Iterates through processors."""
        for n in range(self.instance.processors_number):
            yield self[n]

    def __getitem__(self, processor_index: int):
        """Replaces tasks indexes in the chosen processor with their execution time.
        :param processor_index: index of a chosen processor
        """
        return list(map(
            lambda t: self.instance.tasks_durations[t],
            self.processors[processor_index]
        ))


def load_txt(filename: str) -> Instance:
    """Creates a py:class:`Instance` object from a valid txt file.

    :param filename: name of the text file
    :return: created object
    """
    with open(filename, 'r') as source:
        try:
            processors_number = int(source.readline())
            tasks_number = int(source.readline())
            tasks_durations = list(map(int, source.read().strip().split('\n')))
        except ValueError:
            raise FileContentError(
                f"file must contain <processors_number> and <tasks_number>, every value must be an \\n separated int"
            )

        if processors_number <= 0:
            raise FileContentError(f"number of processors must be > 0, not ({processors_number})")
        if tasks_number < 0:
            raise FileContentError(f"number of tasks must be >= 0, not ({tasks_number})")
        if len(tasks_durations) != tasks_number:
            raise FileContentError(
                f"declared number of tasks ({tasks_number}) is not equal to the length of tasks durations list"
            )

    return Instance(processors_number, tasks_durations)


def save_txt(filename: str, instance: Instance):
    """Saves a py:class:`ProblemInstance` object in a txt file.

    :param filename: name of the text file
    :param instance: object to be saved to a text file
    """
    with open(filename, 'w') as target:
        print(instance.processors_number, file=target)
        print(len(instance.tasks_durations), file=target)

        for i in range(len(instance.tasks_durations)):
            print(instance.tasks_durations[i], file=target)

