class ProblemInstance:
    def __init__(self, tasks_durations, processors_number):
        self.tasks_durations = tasks_durations
        self.processors_number = processors_number


class ProblemInstanceSolution:
    def __init__(self, instance, tasks_indexes_per_processors, total_time=None):
        self.instance = instance
        self.tasks_indexes_per_processors = tasks_indexes_per_processors
        
        if total_time is None:
            total_time = max(map(sum, self))
        self.total_time = total_time

    def __len__(self):
        return self.instance.processors_number

    def __iter__(self):
        for n in range(self.instance.processors_number):
            yield self[n]

    def __getitem__(self, processor_index):
        return list(map(
            lambda t: self.instance.tasks_durations[t],
            self.tasks_indexes_per_processors[processor_index]
        ))

    
class ProblemInstanceFile(ProblemInstance):
    def __init__(self, filename):
        with open(filename) as f:
            processors_number = int(f.readline())
            tasks_number = int(f.readline())
            tasks_durations = list(map(int, f.readlines()))

        super().__init__(tasks_durations, processors_number)


