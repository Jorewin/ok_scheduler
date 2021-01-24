from __future__ import annotations
import matplotlib.axes as axes
import matplotlib.pyplot as pyplot
import numpy
import toml
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

    def __eq__(self, other: Instance) -> bool:
        """Compares two Instance objects

        :param other: other instance
        """
        return self.tasks_durations == other.tasks_durations and self.processors_number == other.processors_number

    @staticmethod
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

    def save_txt(self, filename: str):
        """Saves a py:class:`Instance` object in a txt file.

        :param filename: name of the text file
        """
        with open(filename, 'w') as target:
            print(self.processors_number, file=target)
            print(len(self.tasks_durations), file=target)

            for i in range(len(self.tasks_durations)):
                print(self.tasks_durations[i], file=target)


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

    def plot(self, ax: pyplot.Axes = None) -> axes.Axes:
        """Creates a graphical visualization of the solution.

        :param ax: optional title
        :return: filled ax if ax provided
        """
        if ax is None:
            inplace = True
            _, ax = pyplot.subplots()
        else:
            inplace = False
        y = numpy.arange(self.instance.processors_number)
        length = max([len(processor) for processor in self.processors])
        x = numpy.zeros((length, self.instance.processors_number))
        for i, processor in enumerate(self):
            for j in range(len(processor)):
                x[j][self.instance.processors_number - 1 - i] = processor[j]
        sigma = numpy.zeros(self.instance.processors_number)
        for i in range(length):
            ax.barh(y, x[i], left=sigma)
            sigma += x[i]
        labels = [f"{i}" for i in range(self.instance.processors_number - 1, -1, -1)]
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.set_title("instance solution visualization")
        ax.set_ylabel("processor")
        ax.set_xlabel("execution time")
        if inplace:
            pyplot.show()
        return ax

    def save_toml(self, filename: str, extras: dict = None):
        """Saves a py:class:`InstanceSolution` object alongside additional data in a toml file.

        :param filename: name of the toml file
        :param extras: dictionary containing additional simulation data
        """
        package = {
            "results": {"total_time": self.total_time},
            "simulation_data": extras,
            "solution": {f"processor_{i}": j for i, j in enumerate(self.processors)},
            "instance": {
                "number_of_processors": self.instance.processors_number,
                "number_of_tasks": len(self.instance.tasks_durations),
                "tasks_durations": self.instance.tasks_durations
            }
        }
        with open(filename, 'w') as target:
            toml.dump(package, target)

    @staticmethod
    def load_toml(filename: str) -> (InstanceSolution, dict):
        """

        :param filename: name of the toml file
        :return: created object and simulation data
        """
        with open(filename, 'r') as source:
            package = toml.load(source)
        if "instance" not in package:
            raise FileContentError("file doesn't define instance")
        if "results" not in package:
            raise FileContentError("file doesn't contain results")
        if "solution" not in package:
            raise FileContentError("file doesn't define solution")
        instance = Instance(
            package["instance"].get("number_of_processors"),
            package["instance"].get("tasks_durations")
        )
        if instance.tasks_durations is None or instance.processors_number is None:
            raise FileContentError("instance definition is not complete")
        if len(instance.tasks_durations) != package["instance"].get("number_of_tasks"):
            raise FileContentError("instance definition is corrupted")
        if len(package["solution"]) != instance.processors_number:
            raise FileContentError("solution definition is corrupted")
        processors = []
        tasks = [False for _ in instance.tasks_durations]
        for i in range(instance.processors_number):
            processor = package["solution"].get(f"processor_{i}")
            if processor is None:
                raise FileContentError("solution definition is corrupted")
            for task in processor:
                if task >= len(tasks):
                    raise FileContentError("solution definition is corrupted")
                if tasks[task]:
                    raise FileContentError("solution definition is corrupted")
                else:
                    tasks[task] = True
            processors.append(processor)
        solution = InstanceSolution(instance, processors)
        if package["results"].get("total_time") != solution.total_time:
            raise FileContentError("results are corrupted")
        return solution, package.get("simulation_data", {})
