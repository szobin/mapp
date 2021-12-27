import os

from core.graph import Graph
from core.solver import Solver
from core.helper import check_dir


def main(path, map_name, n_agents=3, random_seed=10):
    print(f"MAPP started for {map_name}")
    result_path = "./routes"
    check_dir(result_path)

    g = Graph()
    if not g.load_map(os.path.join(path, map_name)):
        print(f" - load map failed: {g.error}: {map_name}.map")
        return 1
    print(" - load map OK")

    solver = Solver(g, n_agents, map_name, "./routes/", random_seed=random_seed)
    if not solver.hls_pbs(verbose=1):
        print(f"fail: {solver.error}: {map_name}.map")
        return 1
    print(f" - solved OK: {solver.n_decision} decision(s)")

    if not solver.make_result(result_path):
        print(f" - result store failed: {solver.error}: {map_name}.txt")
        return 1

    print(f" - result stored OK: {map_name}.txt")
    return 0


# main("./maps", "small", 3, 13)  # collision agent 2 vertex 2
# main("./maps", "small", 3, 212)  # collision agent 2 vertex 9
# main("./maps", "small", 3, 100)  # ok
# main("./maps", "small", 3, 10)  # ok
main("./maps", "sample")
# random.seed(100, 2)
