import copy
import random
from PIL import Image, ImageDraw, ImageFont

from .conf import CW, CH, AW2, AH2, AW4, AH4
from .helper import get_x, get_y, get_node


class Scene:
    def __init__(self, graph):
        self.graph = graph
        self.agents = {}
        self.agent_sq = []
        self.t = 0

    def get_random_free_node(self, except_node_id=-1):
        while True:
            node_id = random.choice(list(self.graph.nodes.keys()))
            if self.is_node_free(node_id, except_node_id=except_node_id):
                return node_id

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

    def detect_optimal_path(self, n_agent):
        agent = self.agents[n_agent]
        s_node_id = agent.get("s")
        f_node_id = agent.get("f")
        ns = self.graph.get_neighbors(s_node_id)
        paths = [[n] for n in ns]
        used_nodes = set(ns)
        used_nodes.add(s_node_id)
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

    def place_random_agents(self, n_agents):
        self.agents = {}
        for a in range(n_agents):
            s_node_id = self.get_random_free_node()
            f_node_id = self.get_random_free_node(s_node_id)
            self.agents[a] = dict(s=s_node_id, f=f_node_id)
        for a_id in self.agents:
            self.agents[a_id]["p"] = self.detect_optimal_path(a_id)

    def start(self):
        self.agent_sq = self.agents.keys()
        self.t = -1
        for a_id in self.agent_sq:
            agent = self.agents[a_id]
            agent["i"] = agent["s"]
            if agent.get("p") is None:
                return False
        return True

    def next(self):
        self.t += 1
        n_finished = 0
        for a_id in self.agent_sq:
            agent = self.agents[a_id]
            f_id = agent["f"]
            i_id = agent["i"]
            if f_id == i_id:
                n_finished += 1
                continue

            path = agent.get("p")
            agent["i"] = path[self.t]
        return n_finished < len(self.agent_sq)

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
                draw.rectangle((x - AW4, y - AH4, x + AW4, y + AH4), fill="green")
                draw.text((x, y), str(len(p)), font=font, fill="white", anchor="mm")


        image.save(fn+'.png')
