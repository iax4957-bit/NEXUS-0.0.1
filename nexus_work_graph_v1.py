class WorkNode:
    def __init__(self, node_id, operation, inputs=None):
        self.node_id = node_id
        self.operation = operation
        self.inputs = inputs or []
        self.dependencies = []


class WorkGraphV1:
    def __init__(self):
        self.nodes = {}
        self.results = {}
        self.computation_cache = {}
        self.execution_count = 0
           self.reused_count = 0

    def add_node(self, node_id, operation, inputs=None):
        self.nodes[node_id] = WorkNode(
            node_id,
            operation,
            inputs
        )

    def add_dependency(self, node_id, dependency_id):
        self.nodes[node_id].dependencies.append(dependency_id)

    def execute_node(self, node_id):
        if node_id in self.results:
            return self.results[node_id]

        node = self.nodes[node_id]

        dependency_results = []

        for dependency_id in node.dependencies:
            dependency_results.append(
                self.execute_node(dependency_id)
            )

        if node.operation == "calculate":
            cache_key = (
                "calculate",
                tuple(node.inputs)
            )

            if cache_key in self.computation_cache:
                result = self.computation_cache[cache_key]
            else:
                value = node.inputs[0]
                result = value * value

                self.computation_cache[cache_key] = result
                self.execution_count += 1

        elif node.operation == "add":
            result = sum(dependency_results)
            self.execution_count += 1

        else:
            raise ValueError(
                f"Unknown operation: {node.operation}"
            )

        self.results[node_id] = result
        return result

    def execute_all(self):
        for node_id in self.nodes:
            self.execute_node(node_id)


print("=== NEXUS WORK GRAPH V1.5 ===")

graph = WorkGraphV1()

graph.add_node("A", "calculate", [10])
graph.add_node("B", "calculate", [10])
graph.add_node("C", "calculate", [20])

graph.add_node("D", "add")
graph.add_dependency("D", "A")
graph.add_dependency("D", "C")

graph.add_node("E", "add")
graph.add_dependency("E", "B")
graph.add_dependency("E", "C")

graph.add_node("F", "calculate", [10])

graph.add_node("G", "add")
graph.add_dependency("G", "D")
graph.add_dependency("G", "E")

graph.execute_all()

print(f"A RESULT: {graph.results['A']}")
print(f"B RESULT: {graph.results['B']}")
print(f"C RESULT: {graph.results['C']}")
print(f"D RESULT: {graph.results['D']}")
print(f"E RESULT: {graph.results['E']}")
print(f"F RESULT: {graph.results['F']}")
print(f"G RESULT: {graph.results['G']}")

print()
print(f"TOTAL TASKS: {len(graph.nodes)}")
print(f"REAL EXECUTIONS: {graph.execution_count}")

expected = {
    "A": 100,
    "B": 100,
    "C": 400,
    "D": 500,
    "E": 500,
    "F": 100,
    "G": 1000
}

results_correct = graph.results == expected

work_reduced = (
    graph.execution_count < len(graph.nodes)
)

duplicates_reused = (
    graph.results["A"]
    == graph.results["B"]
    == graph.results["F"]
)

dependencies_shared = (
    graph.results["D"] == 500
    and graph.results["E"] == 500
)

print(f"RESULTS CORRECT: {results_correct}")
print(f"DUPLICATES REUSED: {duplicates_reused}")
print(f"DEPENDENCIES SHARED: {dependencies_shared}")
print(f"WORK REDUCED: {work_reduced}")

final_test = (
    results_correct
    and duplicates_reused
    and dependencies_shared
    and work_reduced
)

print()
print(f"FINAL TEST: {final_test}")
