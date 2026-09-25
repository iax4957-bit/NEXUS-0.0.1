import time

from nexus_work_graph_v1_6 import WorkGraphV1


print("=== NEXUS WORK GRAPH V1.6 LARGE TEST ===")

graph = WorkGraphV1()

TOTAL_TASKS = 1000
UNIQUE_VALUES = 100

start = time.perf_counter()

for i in range(TOTAL_TASKS):
    value = (i % UNIQUE_VALUES) + 1

    graph.add_node(
        f"T{i}",
        "calculate",
        [value]
    )

graph.execute_all()

elapsed = time.perf_counter() - start


total_tasks = len(graph.nodes)
real_executions = graph.execution_count
reused_results = graph.reused_count

work_saved = total_tasks - real_executions
work_saved_percent = (
    work_saved / total_tasks
) * 100


results_correct = True

for i in range(TOTAL_TASKS):
    value = (i % UNIQUE_VALUES) + 1
    expected = value * value

    if graph.results[f"T{i}"] != expected:
        results_correct = False
        break


work_reduced = real_executions < total_tasks


print()
print(f"TOTAL TASKS: {total_tasks}")
print(f"UNIQUE CALCULATIONS: {UNIQUE_VALUES}")
print(f"REAL EXECUTIONS: {real_executions}")
print(f"REUSED RESULTS: {reused_results}")
print(f"WORK SAVED: {work_saved}")
print(f"WORK SAVED %: {work_saved_percent:.2f}%")
print(f"ELAPSED: {elapsed:.6f}s")

print()
print(f"RESULTS CORRECT: {results_correct}")
print(f"WORK REDUCED: {work_reduced}")

final_test = (
    results_correct
    and work_reduced
    and real_executions == UNIQUE_VALUES
    and reused_results == TOTAL_TASKS - UNIQUE_VALUES
)

print()
print(f"FINAL TEST: {final_test}")
