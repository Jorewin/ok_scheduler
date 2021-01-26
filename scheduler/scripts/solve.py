import os.path
import time
import datetime
import itertools
import re
import math
import click
import scheduler
from threading import Event, Timer


def get_file_name(name, extension):
    match = re.search(f"(.+)(.{extension})", name)
    if match is not None:
        name = match.group(1)
    i = 1
    while os.path.isfile(f"{name}-{i}.{extension}"):
        i += 1
    return f"{name}-{i}.{extension}"


def parse_time(seconds):
    hours = min(seconds // 3600, 24)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f"{int(hours):0>2}:{int(minutes):0>2}:{int(seconds):0>2}"


@click.group()
def solve():
    """Solves the P||Cmax problem using the specified algorithm."""


@solve.command()
@click.option(
    "-i", "source", prompt=True, help="path to the instance file.", type=click.Path(exists=True)
)
@click.option(
    "-o", "target", help="output file or directory", default=None, type=click.Path(writable=True)
)
@click.option("-p", "population_size", prompt=True, help="size of the population.", type=int)
@click.option("-b", "best_specimens_group_size", prompt=True, help="size of the best specimens group.", type=int)
@click.option(
    "-t", "period", default=None, help="processing time",
    type=click.DateTime(["%H:%M:%S", "%-H:%M:%S", "%M:%S", "%-M:%S", "%S", "%-S"])
)
def jakub_genetic(
        source: str, target: str, population_size: int, best_specimens_group_size: int, period: datetime.datetime
):
    """Solves the instance read from input and writes the result to the output after KeyboardInterrupt."""
    if best_specimens_group_size > population_size:
        raise ValueError("best_specimens_group_size can't be higher than the population_size")
    else:
        extras = {
            "algorithm": "jakub_genetic",
            "time_period": "",
            "best_solution_at": "00:00:00",
            "population_size": population_size,
            "best_specimens_group_size": best_specimens_group_size
        }
        instance = scheduler.Instance.load_txt(source)
        default = f"jakub_genetic-m{instance.processors_number}n{len(instance.tasks_durations)}"
        if target is None:
            target = default
        elif os.path.isdir(target):
            target = os.path.join(target, default)
        target = get_file_name(target, "toml")
        new = datetime.datetime.now()
        if period is not None:
            period = new + datetime.timedelta(hours=period.hour, minutes=period.minute, seconds=period.second)
            period = period.timestamp()
        else:
            period = 0
        start = new.timestamp()
        generator = scheduler.jakub_genetic.solution_generator(instance, population_size, best_specimens_group_size)
        best_solution = next(generator)
        total_times = [best_solution.total_time for _ in range(100)]
        average_width = 0
        solution_width = math.ceil(math.log10(best_solution.total_time))
        try:
            for generation, solution in zip(itertools.count(1, 1), generator):
                if solution.total_time < best_solution.total_time:
                    best_solution = solution
                    extras.update({"best_solution_at": parse_time(time.time() - start)})
                if period != 0 and time.time() >= period:
                    raise KeyboardInterrupt()
                total_times[(generation - 1)%100] = solution.total_time
                average = sum(total_times)/len(total_times)
                average_width = max(average_width, math.ceil(math.log10(average)))
                solution_width = max(solution_width, math.ceil(math.log10(best_solution.total_time)))
                print(
                    f"Time elapsed: {parse_time(time.time() - start)}",
                    f"Generations created: {generation}",
                    f"Average solution: {average:{average_width}.0f}",
                    f"Best solution: {best_solution.total_time:{solution_width}}",
                    sep=" | ",
                    end="\r",
                    flush=True
                )
        except KeyboardInterrupt as error:
            extras.update({"time_period": parse_time(time.time() - start)})
            best_solution.save_toml(target, extras=extras)
            print(f"\nSolution saved in {target}")
            raise KeyboardInterrupt(error)


@solve.command()
@click.option(
    "-i", "source", prompt=True, help="path to the instance file.", type=click.Path(exists=True)
)
@click.option(
    "-o", "target", help="output file or directory", default=None, type=click.Path(writable=True)
)
@click.option("-n", "threads", prompt=True, help="number of threads", type=int)
@click.option("-p", "thread_population_size", prompt=True, help="size of the population of each thread.", type=int)
@click.option("-b", "best_specimens_per_thread", prompt=True, help="size of the best specimens group per thread.", type=int)
@click.option(
    "-t", "period", default=None, help="processing time",
    type=click.DateTime(["%H:%M:%S", "%-H:%M:%S", "%M:%S", "%-M:%S", "%S", "%-S"])
)
def eryk_genetic(source: str, target: str, threads: int, thread_population_size: int, best_specimens_per_thread: int, period: datetime.datetime):
    """Solves the instance read from input and writes the result to the output after KeyboardInterrupt."""

    extras = {
        "algorithm": "eryk_heuristic",
        'threads_number': threads,
        'thread_population_size': thread_population_size,
        'best_specimens_per_thread': best_specimens_per_thread
    }

    stop_event = Event()
    start_time = time.time()
    if period is not None:
        Timer(period.hour * 3600 + period.minute * 60 + period.second, lambda: stop_event.set()).start()

    instance = scheduler.Instance.load_txt(source)
    default = f"eryk_genetic-m{instance.processors_number}n{len(instance.tasks_durations)}"
    if target is None:
        target = default
    elif os.path.isdir(target):
        target = os.path.join(target, default)
    target = get_file_name(target, "toml")

    def update_interface(queue):
        current_best = queue.best()
        print(
            f"Elapsed time: {parse_time(time.time() - start_time)}",
            f"Best solution: {current_best.total_time:8}",
            sep=" | ",
            end="\r",
            flush=True
        )
       
    try:
        results_queue = scheduler.eryk_heuristic.SolutionsQueue(4)
        scheduler.eryk_heuristic.solve(instance, results_queue, stop_event, update_interface, threads, thread_population_size, best_specimens_per_thread)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        results_queue.pop().save_toml(target, {**extras, 'time_period': parse_time(time.time() - start_time)})
        print(f"\nSolution saved in {target}")
        raise KeyboardInterrupt()
