import copy
import os
import random
from PIL import Image, ImageDraw, ImageFont

from .conf import CW, CH, AW2, AH2, AW4, AH4
from .helper import get_x, get_y, get_node, is_agent_finished


class Scene:
    def __init__(self, graph):
        self.graph = graph
        self.agents = {}
        self.agent_sq = []
        self.constraints = {}
        self.t = 0
        self.collisions = []
        self.decision_id = -1

    def is_node_free(self, node_id, except_node_id=None):
        if except_node_id == node_id:
            return False
        for a_id, a in self.agents.items():
            s_node_id = a.get("s")
            if s_node_id == node_id:
                return False
            f_node_id = a.get("f")
            if f_node_id == node_id:
                return False
        return True

    def get_random_free_node(self, except_node_id=-1):
        while True:
            node_id = random.choice(list(self.graph.nodes.keys()))
            if self.is_node_free(node_id, except_node_id=except_node_id):
                return node_id

    def place_random_agents(self, n_agents, random_seed=10):
        random.seed(random_seed, 2)
        self.agents = {}
        for a in range(n_agents):
            s_node_id = self.get_random_free_node()
            f_node_id = self.get_random_free_node(s_node_id)
            self.agents[a] = dict(s=s_node_id, f=f_node_id)

    def detect_optimal_path(self, n_agent):
        agent = self.agents[n_agent]
        s_node_id = agent.get("s")
        f_node_id = agent.get("f")
        used_nodes = set(self.constraints[n_agent])
        used_nodes.add(s_node_id)
        ns = self.graph.get_neighbors(s_node_id, used_nodes)
        paths = [[n] for n in ns]
        for n in set(ns):
            used_nodes.add(n)
        while True:
            has_neighbors = 0
            for i, p in enumerate(paths):
                leaf_id = p[-1]
                pp = copy.copy(p)
                if leaf_id == f_node_id:
                    return pp
                ns = self.graph.get_neighbors(leaf_id, used_nodes)
                if len(ns) == 0:
                    continue
                has_neighbors += 1
                used_nodes.add(ns[0])
                paths[i].append(ns[0])
                del ns[0]
                for n in ns:
                    used_nodes.add(n)
                    ppp = copy.copy(pp)
                    ppp.append(n)
                    paths.append(ppp)
            if has_neighbors == 0:
                return None

    def start(self):
        self.t = -1
        for a_id, agent in self.agents.items():
            agent["i"] = agent["s"]
            agent["c"] = False

        return True

    def try_next(self) -> bool:
        self.collisions = []
        nodes_occupied = {}
        edges_occupied = []
        # for finished agents
        for a_id, agent in self.agents.items():
            if is_agent_finished(agent):
                i = agent.get("f")
                nodes_occupied[i] = a_id

        for a_id in self.agent_sq:
            agent = self.agents[a_id]
            agent_has_collision = False
            if is_agent_finished(agent):
                continue

            e_a = agent.get("i")
            path = agent.get("p")
            e_b = path[self.t+1]
            if e_b in nodes_occupied:
                agent_has_collision = True
                self.collisions.append(dict(ai=a_id, aj=nodes_occupied[e_b], mode="vertex", e=(e_a, e_b),
                                            msg=f"collision in vertex {e_b}"))
            nodes_occupied[e_b] = a_id

            if (e_a, e_b) in edges_occupied:
                if not agent_has_collision:
                    self.collisions.append(dict(ai=a_id, mode="edge", e=(e_a, e_b),
                                                msg=f"collision in edge ({e_a},{e_b})"))
                    agent_has_collision = True
            edges_occupied.append((e_a, e_b))

            if (e_b, e_a) in edges_occupied:
                if not agent_has_collision:
                    self.collisions.append(dict(ai=a_id, mode="edge", e=(e_b, e_a),
                                                msg=f"collision in edge ({e_b},{e_a})"))
                    agent_has_collision = True
            edges_occupied.append((e_b, e_a))
            agent["c"] = agent_has_collision

        return len(self.collisions) == 0  # has collisions

    def next(self):
        self.t += 1
        n_finished = 0
        for a_id in self.agent_sq:
            agent = self.agents[a_id]
            if is_agent_finished(agent):
                n_finished += 1
                continue

            path = agent.get("p")
            agent["i"] = path[self.t]
        return n_finished < len(self.agent_sq)

    def detect_soc(self):
        r = 0
        for a_id, agent in self.agents.items():
            path = agent["p"]
            r += len(path)
        return r

    def detect_makespan(self):
        r = 0
        for a_id, agent in self.agents.items():
            path = agent["p"]
            r = max(r, len(path))
        return r

    def starts(self):
        r = ""
        for a_id, agent in self.agents.items():
            s = agent.get("s")
            n = get_node(s, self.graph.nodes)
            x = round(n.get("x"))
            y = round(n.get("y"))
            r += f"({x},{y}),"
        return r

    def goals(self):
        r = ""
        for a_id, agent in self.agents.items():
            f = agent.get("f")
            n = get_node(f, self.graph.nodes)
            x = round(n.get("x"))
            y = round(n.get("y"))
            r += f"({x},{y}),"
        return r

    def make_result(self, f_path, fn, solver, decisions, align=False):
        span = self.detect_makespan()
        lines = ["instance=none\n",
                 f"agents={len(self.agents)}\n",
                 f"map_file={fn}.map\n",
                 f"solver={solver}\n",
                 "solved=0\n",
                 f"soc={self.detect_soc()}\n",
                 f"makespan={span}\n",
                 f"comp_time={decisions}\n",
                 f"starts={self.starts()}\n",
                 f"goals={self.goals()}\n",
                 "solution=\n"]
        for a_id, agent in self.agents.items():
            p = agent.get("p")
            s_id = agent.get("s")
            n = get_node(s_id, self.graph.nodes)
            x, y = round(n.get("x")), round(n.get("y"))
            s = f"{a_id}:({x},{y}),"
            for i in p:
                n = get_node(i, self.graph.nodes)
                x, y = round(n.get("x")), round(n.get("y"))
                s += f"({x},{y}),"

            if align:
                if len(p) < span:
                    for _ in range(span - len(p)):
                        s += f"({x},{y}),"

            lines.append(s+"\n")

        with open(os.path.join(f_path, fn+".txt"), "w") as f:
            f.writelines(lines)
            f.close()
        return True

    def make_map_image(self, fn):
        x_max = self.graph.get_x_max()
        y_max = self.graph.get_y_max()

        image = Image.new("RGB", (CW*(x_max+1), CH*(y_max+1)), "white")
        font = ImageFont.truetype("./font/freesans.ttf", size=8)
        draw = ImageDraw.Draw(image)
        self.graph.draw_map(draw, font)

        for a_id, agent in self.agents.items():
            f_node_id = agent.get("f")
            f_node = get_node(f_node_id, self.graph.nodes)
            agent_has_collision = agent.get("c")
            if agent_has_collision is None:
                agent_has_collision = False
            cx, cy = f_node.get("x"), f_node.get("y")
            x, y = get_x(cx), get_y(cy)
            draw.ellipse((x - AW2, y - AH2, x + AW2, y + AH2), fill="white")
            draw.text((x, y), str(a_id), font=font, fill="black", anchor="mm")

            i_node_id = agent.get("i")
            agent_finished = i_node_id == f_node_id
            x, y = self.graph.get_node_rect(i_node_id)

            p = agent.get("p")
            a_color = "red" if p is None else "green"
            draw.rectangle((x - AW2, y - AH2, x + AW2, y + AH2), fill=a_color)
            if agent_finished:
                draw.ellipse((x - AW4, y - AH4, x + AW4, y + AH4), fill="blue")
            draw.text((x, y), str(a_id), font=font, fill="white", anchor="mm")

            if (not agent_finished) and (p is not None):
                n_id = p[self.t+1]
                x, y, = self.graph.get_node_d_rect(i_node_id, n_id)
                color = "red" if agent_has_collision else "green"
                draw.rectangle((x - AW4, y - AH4, x + AW4, y + AH4), fill=color)
                draw.text((x, y), str(len(p)), font=font, fill="white", anchor="mm")

        image.save(fn+'.png')
