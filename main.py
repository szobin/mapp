import os
import random

from core.graph import Graph
from core.scene import Scene


def main(path, name, n_agents=3, random_seed=10):
    random.seed(random_seed, 2)

    g = Graph()
    g.load_map(os.path.join(path, name))

    s = Scene(g)
    s.place_random_agents(n_agents)
    s.start()
    s.make_map_image(f"./routes/{name}")
    n = 0
    while s.next():
        n += 1
        s.make_map_image(f"./routes/{name}.{n}")
    print(f"done: {name}.png")


# main("./maps", "simple", 3, 10)
main("./maps", "simple", 3, 100)
# main("./maps", "article")
# main("./maps", "lera")
# random.seed(100, 2)
