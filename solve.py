import os.path
import time
import itertools
import math
import pickle
import click
import scheduler


def get_name(name, extension):
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


@click.command()
@click.option(
    "-i", "--input", "input", prompt=True, help="Path to the instance file.", type=click.Path(exists=True)
)
@click.option("-p", "population_size", prompt=True, help="Size of the population.", type=int)
@click.option("-b", "best_specimens_group_size", prompt=True, help="Size of the best specimens group.", type=int)
def solve(input, population_size, best_specimens_group_size):
    if best_specimens_group_size > population_size:
        raise ValueError("best_specimens_group_size can't be higher than the population_size")
    else:
        instance = scheduler.Instance.load_txt(input)
        generator = scheduler.jakub_genetic.solution_generator(instance, population_size, best_specimens_group_size)
        best_solution = scheduler.greedy.solve(instance)
        total_times = [best_solution.total_time for _ in range(100)]
        start = time.time()
        average = 0
        average_width = 0
        solution_width = math.ceil(math.log10(best_solution.total_time))
        try:
            for generation, solution in zip(itertools.count(1, 1), generator):
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
            with open(get_name(input[:-4], "obj"), "wb") as target:
                pickle.dump(best_solution, target)
            raise KeyboardInterrupt(error)


if __name__ == "__main__":
    solve()
