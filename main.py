import os

from core.graph import Graph
from core.solver import Solver
from core.helper import check_dir


def main(path, map_name, n_agents=3, random_seed=10):
    result_path = "./routes"
    check_dir(result_path)

    g = Graph()
    g.load_map(os.path.join(path, map_name))

    solver = Solver(g, n_agents, map_name, "./routes/", random_seed=random_seed)
    if not solver.hls_pbs(verbose=1):
        print(f"fail: {solver.error}: {map_name}.map")
        return 1

    solver.make_result(result_path, map_name)
    print(f"success: {map_name}.text")
    return 0


# main("./maps", "small", 3, 13)  # collision agent 2 vertex 2
# main("./maps", "small", 3, 212)  # collision agent 2 vertex 9
# main("./maps", "small", 3, 100)  # ok
# main("./maps", "small", 3, 10)  # ok
main("./maps", "sample")
# random.seed(100, 2)
