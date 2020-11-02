from scheduler.generator import generate
from scheduler.algorithms import brute_force_recursive

Cmax = 10
n = 8
p = 3
rng = (1, 8)

tasks_list = generate(Cmax, n, p, rng)
print(f'Wygenerowano listę {n} zadań; dla {p} procesorów powinna dać Cmax = {Cmax}')
print('Zadania: ', tasks_list)
print()

print('Wykonuje się algorytm brute-force')
result = brute_force_recursive.solve(tasks_list, p)
print(f'Cmax = {result.time}')
for i, tasks in enumerate(result.processors):
    resolved_tasks = list(map(lambda i: tasks_list[i - 1], tasks))
    print(f'Procesor nr {i + 1}: {resolved_tasks}')
