#!/usr/bin/env python3

import sys
import scheduler

if len(sys.argv) != 2:
    print('Incorrect usage', file=sys.stderr)
    sys.exit(1)

instance = scheduler.problem.load_txt(sys.argv[1])

print("OPT >= ", sum(instance.tasks_durations) / instance.processors_number)


algorithms = [
    #('lpt', scheduler.lpt.solve),
    ('basic_3', scheduler.basic_heuristic_3.solve)
]

for algorithm, callback in algorithms:
    solution = callback(instance)
    print(f'{algorithm}: {solution.total_time}')
    solution.plot()

