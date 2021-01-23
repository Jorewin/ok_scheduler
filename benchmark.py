#!/usr/bin/env python3

import sys
import scheduler

if len(sys.argv) != 2:
    print('Incorrect usage', file=sys.stderr)
    sys.exit(1)

instance = scheduler.problem.Instance.load_txt(sys.argv[1])

print("OPT >= ", sum(instance.tasks_durations) / instance.processors_number)


algorithms = [
    ('eryk_heuristic', scheduler.eryk_heuristic.solve)
]

for algorithm, callback in algorithms:
    solution = callback(instance)
    print(f'{algorithm}: {solution.total_time}')
    solution.plot()

