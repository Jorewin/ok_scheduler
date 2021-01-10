#!/usr/bin/env python3

import sys
import scheduler

if len(sys.argv) != 2:
    print('Incorrect usage', file=sys.stderr)
    sys.exit(1)

instance = scheduler.problem.load_txt(sys.argv[1])
algorithms = [
    ('greedy', scheduler.greedy.solve),
    ('basic_1', scheduler.basic_heuristic.solve),
    ('basic_2', scheduler.basic_heuristic_2.solve)
]

for algorithm, callback in algorithms:
    solution = callback(instance)
    print(f'{algorithm}: {solution.total_time}')
    solution.plot()

