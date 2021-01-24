import click
import matplotlib.pyplot as pyplot
import scheduler


@click.group()
def analyze():
    """Analyzes the results of the scheduler module"""


@analyze.command()
@click.option(
    "-i", "source", prompt=True, help="Path to the solution file.", type=click.Path(exists=True)
)
def display(source: str):
    """Displays the simulation data and plots the result."""
    solution, extras = scheduler.InstanceSolution.load_toml(source)
    print(f"Solution of instance - m{solution.instance.processors_number}n{len(solution.instance.tasks_durations)}")
    name = "total_time"
    width = max(len(name), max(map(len, extras)))
    print(f"{name:{width}}", solution.total_time)
    for key in extras:
        print(f"{key:{width}}", extras[key])
    _, ax = pyplot.subplots()
    solution.plot(ax=ax)
    ax.set_title(extras.get("algorithm", "unknown"))
    pyplot.show()


@analyze.command()
@click.option(
    "-i1", "source_1", prompt=True, help="Path to the first solution file.", type=click.Path(exists=True)
)
@click.option(
    "-i2", "source_2", prompt=True, help="Path to the second solution file.", type=click.Path(exists=True)
)
def compare(source_1: str, source_2: str):
    """Compares two solutions"""
    solution_1, extras_1 = scheduler.InstanceSolution.load_toml(source_1)
    solution_2, extras_2 = scheduler.InstanceSolution.load_toml(source_2)
    if not solution_1.instance == solution_2.instance:
        raise scheduler.FileContentError("can't compare solutions of different instances")
    title = "Comparison of solutions of instance"
    print(f"{title} - m{solution_1.instance.processors_number}n{len(solution_2.instance.tasks_durations)}")
    name_1 = "total_time"
    name_2 = ''
    width_1 = max(len(name_1), max(map(len, extras_1)), max(map(len, extras_2)))
    width_2 = max(
        len(f"{solution_1.total_time}"), len(f"{solution_2.total_time}"),
        max([len(f"{i}") for i in extras_1.values()]), max([len(f"{i}") for i in extras_2.values()])
    )
    common = list(filter(lambda x: x in extras_2, extras_1))
    print(f"{name_1:{width_1}}", f"{solution_1.total_time:<{width_2}}", f"{solution_2.total_time:<{width_2}}")
    for key in common:
        print(f"{key:{width_1}}", f"{extras_1[key]:<{width_2}}", f"{extras_2[key]:<{width_2}}")
    for key in extras_1:
        if key not in common:
            print(f"{key:{width_1}}", f"{extras_1[key]:<{width_2}}", f"{name_2:-^{width_2}}")
    for key in extras_2:
        if key not in common:
            print(f"{key:{width_1}}", f"{name_2:-^{width_2}}", f"{extras_2[key]:<{width_2}}")
    _, (ax_1, ax_2) = pyplot.subplots(1, 2)
    solution_1.plot(ax=ax_1)
    solution_2.plot(ax=ax_2)
    ax_1.set_title(extras_1.get("algorithm", "unknown"))
    ax_2.set_title(extras_2.get("algorithm", "unknown"))
    pyplot.show()
