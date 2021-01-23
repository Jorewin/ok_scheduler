import os.path
import time
import datetime
import itertools
import re
import math
import click
import scheduler


def get_file_name(name, extension):
    match = re.search(f"(.+)(.{extension})", name)
    if match is not None:
        name = match.group(1)
    i = 1
    while os.path.isfile(f"{name}_{i}.{extension}"):
        i += 1
    return f"{name}_{i}.{extension}"


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
    "-i", "source", prompt=True, help="Path to the instance file.", type=click.Path(exists=True)
)
@click.option(
    "-o", "target", help="output", default=None, type=click.Path(exists=True, writable=True)
)
@click.option("-p", "population_size", prompt=True, help="Size of the population.", type=int)
@click.option("-b", "best_specimens_group_size", prompt=True, help="Size of the best specimens group.", type=int)
@click.option(
    "-t", "period", default=None, help="Processing time fmt = HH:MM:SS/MM:SS/SS",
    type=click.DateTime(["%H:%M:%S", "%M:%S", "%S"])
)
def jakub_genetic(source: str, target: str, population_size: int, best_specimens_group_size: int, period: datetime.datetime):
    """Solves the instance read from input and writes the result to the output after KeyboardInterrupt."""
    if best_specimens_group_size > population_size:
        raise ValueError("best_specimens_group_size can't be higher than the population_size")
    else:
        new = datetime.datetime.now()
        if period is not None:
            period = period.replace(year=new.year, month=new.month, day=new.day, tzinfo=new.tzinfo).timestamp()
        else:
            period = 0
        extras = {
            "time period": parse_time(period),
            "population_size": population_size,
            "best specimens group size": best_specimens_group_size
        }
        instance = scheduler.Instance.load_txt(source)
        if target is None:
            target = f"jakub_genetic-m{instance.processors_number}n{len(instance.tasks_durations)}"
        generator = scheduler.jakub_genetic.solution_generator(instance, population_size, best_specimens_group_size)
        best_solution = scheduler.greedy.solve(instance)
        total_times = [best_solution.total_time for _ in range(100)]
        start = time.time()
        average = 0
        average_width = 0
        solution_width = math.ceil(math.log10(best_solution.total_time))
        try:
            for generation, solution in zip(itertools.count(1, 1), generator):
                if period != 0 and time.time() >= period:
                    best_solution.save_txt(get_file_name(target, "toml"), extras=extras)
                    return
                best_solution = min(best_solution, solution, key=lambda x: x.total_time)
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
            best_solution.save_txt(
                get_file_name(target, "toml"), extras=extras.update({"time period": parse_time(time.time() - start)})
            )
            raise KeyboardInterrupt(error)
