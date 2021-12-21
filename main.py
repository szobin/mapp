import os
from core.graph import Graph


def main(path, name, n_agents=3):
    g = Graph()
    g.load_map(os.path.join(path, name))
    g.place_random_agents(n_agents)
    g.make_map_image(f"./routes/{name}.png")
    print(f"done: {name}.png")


main("./maps", "simple")
main("./maps", "article")
main("./maps", "lera")

