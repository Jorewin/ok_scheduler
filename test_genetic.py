#!/usr/bin/env python3

import scheduler
instance = scheduler.problem.load_txt('examples/m30.txt')
solution = scheduler.genetic.solve(instance)
print(solution.total_time)

