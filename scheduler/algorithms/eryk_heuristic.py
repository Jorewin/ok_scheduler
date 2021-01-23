import math
import copy
import heapq
import random
from threading import Event, Timer, Thread, Lock

import scheduler
from scheduler.problem import Instance, InstanceSolution

WORKING_TIME = 60 # seconds
THREADS = 8
THREAD_POPULATION_SIZE = 32
BEST_SPECIMENS_PER_THREAD = 6


def index_of_min(iterable):
    return min(enumerate(iterable), key=lambda x: x[1])[0]

def index_of_max(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]


class SolutionsQueue:
    def __init__(self, size):
        self.stored_elements = 2 ** math.ceil(math.log(size + 1, 2))
        self.queue = []
        self.lock = Lock()

    def push(self, element):
        with self.lock:
            heapq.heappush(self.queue, element)
            if len(self.queue) > self.stored_elements:
                self.queue = self.queue[:self.stored_elements]

    def pop(self):
        while True:
            with self.lock:
                if not self.empty():
                    return heapq.heappop(self.queue)

    def empty(self):
        return len(self.queue) == 0


# Odwołuje się do zadań normalnie po wartościach, nie indeksach
class GeneticSolution(InstanceSolution):
    def __init__(self, initial: InstanceSolution):
        self.instance = initial.instance
        self.total_time = initial.total_time
        self.processors = list(map(
            lambda p: list(map(
                lambda t: self.instance.tasks_durations[t],
                p
            )),
            initial.processors
        ))

        self.processors_times = list(map(sum, self.processors))

    def __getitem__(self, processor_index: int):
        return self.processors[processor_index]


    def __lt__(self, other):
        return self.score() < other.score()


    def score(self):
        return self.total_time


    def mutate(self):
        start_processor_index = random.randrange(len(self.processors))
        end_processor_index = random.randrange(len(self.processors))
        
        if start_processor_index != end_processor_index and len(self.processors[start_processor_index]) > 0 and len(self.processors[end_processor_index]) > 0:
            start_task_index = random.randrange(len(self.processors[start_processor_index]))
            end_task_index = random.randrange(len(self.processors[end_processor_index]))

            task = self.processors[start_processor_index].pop(start_task_index)
            self.processors[end_processor_index].insert(end_task_index, task)

            self.processors_times[start_processor_index] -= task
            self.processors_times[end_processor_index] += task
            
            if self.processors_times[end_processor_index] > self.total_time:
                self.total_time = self.processors_times[end_processor_index]
            else:
                self.total_time = max(self.processors_times)


    def cross(self):
        start_processor_index = index_of_max(self.processors_times)
        end_processor_index = index_of_min(self.processors_times)
        processors_difference = self.processors_times[start_processor_index] - self.processors_times[end_processor_index]

        # Zakładam, że w problemie szeregowania jest przynajmniej jedno zadanie (znajduje się na najbardziej obciążonym procesorze)
        start_task_index = random.randrange(len(self.processors[start_processor_index]))

        if len(self.processors[end_processor_index]) == 0:
            first_task = self.processors[start_processor_index].pop(start_task_index)
            self.processors[end_processor_index].append(first_task)
            
            self.processors_times[start_processor_index] -= first_task
            self.processors_times[end_processor_index] += first_task
            self.total_time = max(self.processors_times)
        else:
            end_task_index = index_of_min(map(
                lambda task: abs(processors_difference - 2 * (self.processors[start_processor_index][start_task_index] - task)),
                self.processors[end_processor_index]
            ))

            first_task = self.processors[start_processor_index][start_task_index]
            second_task = self.processors[end_processor_index][end_task_index]
            tasks_difference = first_task - second_task

            if tasks_difference > 0 and tasks_difference < processors_difference:
                self.processors[start_processor_index][start_task_index] = second_task
                self.processors[end_processor_index][end_task_index] = first_task

                self.processors_times[start_processor_index] -= tasks_difference
                self.processors_times[end_processor_index] += tasks_difference
                self.total_time = max(self.processors_times)



def algorithm_thread(best_solutions, stop_event):
    while not stop_event.is_set():
        parent = best_solutions.pop()
        
        population = [copy.deepcopy(parent) for _ in range(THREAD_POPULATION_SIZE)]
        for specimen in population:
            specimen.mutate()

        best_specimens = heapq.nsmallest(BEST_SPECIMENS_PER_THREAD, population, key=lambda s: s.score())
        for specimen in best_specimens:
            specimen.cross()
            best_solutions.push(specimen)




def solve(instance: Instance) -> InstanceSolution:
    """Solves the P||Cmax problem by using a basic heuristic.

    :param instance: valid problem instance
    :return: generated solution of a given problem instance
    """

    best_solutions = SolutionsQueue(THREAD_POPULATION_SIZE * THREADS)
    stop_event = Event()
    Timer(WORKING_TIME, lambda: stop_event.set()).start()

    #lpt_solution = scheduler.lpt.solve(instance)
    lpt_solution = scheduler.greedy.solve(instance)
    genetic_solution = GeneticSolution(lpt_solution)
    threads = []

    for _ in range(THREADS):
        copied_solution = copy.deepcopy(genetic_solution)
        best_solutions.push(copied_solution)

        t = Thread(target=algorithm_thread, args=(best_solutions, stop_event))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    return genetic_solution if best_solutions.empty() else best_solutions.pop()


__all__ = ["solve"]

