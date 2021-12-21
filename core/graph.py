import os
import copy
import random
# import glob
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

CW = CH = 80
CW2, CH2 = CW // 2, CH // 2

NW, NH = round(CW*0.70), round(CH*0.7)
NW2, NH2 = NW // 2, NH // 2

DX, DY = NW2 // 2, NH2 // 2

AW, AH = round(NW*0.70), round(NH*0.7)
AW2, AH2 = AW // 2, AH // 2
AW4, AH4 = AW2 // 2, AH2 // 2

# random.seed(100, 2)
random.seed(10, 2)


# def get_ttf():
#     ttf_files = glob.glob("*.ttf")
#     return ttf_files[0]


def get_x(cx: int) -> int:
    return cx*CW + CW2


def get_y(cy: int) -> int:
    return cy*CH + CH2


def update_edge(a_x, a_y, b_x, b_y, dx=DX, dy=DY):
    aa_x, aa_y = a_x, a_y
    bb_x, bb_y = b_x, b_y
    if a_y < b_y:  # up
        aa_x -= dx
        bb_x -= dx
    if a_y > b_y:  # dn
        aa_x += dx
        bb_x += dx
    if a_x < b_x:  # lf
        aa_y -= dy
        bb_y -= dy
    if a_x > b_x:  # lf
        aa_y += dy
        bb_y += dy
    return aa_x, aa_y, bb_x, bb_y


def to_node(line: str) -> Optional[dict]:
    cells = line.split(" ")
    if len(cells) == 3:
        return dict(id=int(cells[0]), x=float(cells[1]), y=float(cells[2]))
    return None


def to_edge(line: str) -> Optional[dict]:
    cells = line.split(" ")
    if len(cells) == 2:
        return dict(a=int(cells[0]), b=int(cells[1]))
    return None


def get_node(node_id: int, nodes: dict) -> Optional[dict]:
    return nodes.get(node_id)


def has_id_in_nodes(node_id: int, nodes: dict) -> bool:
    return get_node(node_id, nodes) is not None


def check_edge(edge: dict, nodes: dict) -> bool:
    if edge is None:
        return False
    return has_id_in_nodes(edge.get("a"), nodes) and has_id_in_nodes(edge.get("b"), nodes)


class Graph:

    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.agents = {}

    def load_map(self, a_name: str):
        with open(os.path.join(a_name, 'nodes.txt'), 'r') as f_nodes:
            node_lines = f_nodes.readlines()
            f_nodes.close()

        with open(os.path.join(a_name, 'edges.txt'), 'r') as f_edges:
            edge_lines = f_edges.readlines()
            f_edges.close()

        node_list = filter(lambda item: item is not None, map(to_node, node_lines))
        self.nodes = {node.get("id"): {'x': node.get("x"), 'y': node.get("y")} for node in node_list}
        self.edges = list(filter(lambda item: check_edge(item, self.nodes), map(to_edge, edge_lines)))

    def get_x_max(self):
        x_max = 0
        for node_id, node in self.nodes.items():
            x = int(node.get("x"))
            x_max = max(x_max, x)
        return x_max

    def get_y_max(self):
        y_max = 0
        for node_id, node in self.nodes.items():
            y = int(node.get("y"))
            y_max = max(y_max, y)
        return y_max

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
            node_id = random.choice(list(self.nodes.keys()))
            if self.is_node_free(node_id, except_node_id=except_node_id):
                return node_id

    def place_random_agents(self, n_agents):
        self.agents = {}
        for a in range(n_agents):
            s_node_id = self.get_random_free_node()
            f_node_id = self.get_random_free_node(s_node_id)
            self.agents[a] = dict(s=s_node_id, f=f_node_id)
        for a_id in self.agents:
            self.agents[a_id]["p"] = self.detect_optimal_path(a_id)

    def get_neighbors(self, node_id, exceptions=None):
        ns = []
        for edge in self.edges:
            a_node_id = edge.get("a")
            if node_id != a_node_id:
                continue
            b_node_id = edge.get("b")
            if (exceptions is not None) and (b_node_id in exceptions):
                continue
            ns.append(b_node_id)
        return ns

    def detect_optimal_path(self, n_agent):
        agent = self.agents[n_agent]
        s_node_id = agent.get("s")
        f_node_id = agent.get("f")
        ns = self.get_neighbors(s_node_id)
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
                ns = self.get_neighbors(leaf_id, used_nodes)
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

    def get_node_rect(self, n_id):
        node = get_node(n_id, self.nodes)
        cx, cy = node.get("x"), node.get("y")
        return get_x(cx), get_y(cy)

    def get_node_d_rect(self, n_id, nn_id):
        x, y = self.get_node_rect(n_id)
        xd, yd = self.get_node_rect(nn_id)
        xx, yy = x, y
        if x > xd:
            xx -= AW2
        if x < xd:
            xx += AW2
        if y > yd:
            yy -= AH2
        if y < yd:
            yy += AH2
        return xx, yy

    def make_map_image(self, path):
        x_max = self.get_x_max()
        y_max = self.get_y_max()

        image = Image.new("RGB", (CW*(x_max+1), CH*(y_max+1)), "white")
        font = ImageFont.truetype("./font/freesans.ttf", size=8)
        draw = ImageDraw.Draw(image)
        for node_id, node in self.nodes.items():
            cx, cy = node.get("x"), node.get("y")
            x, y = get_x(cx), get_y(cy)
            draw.ellipse((x-NW2, y-NH2, x+NW2, y+NH2), fill="navy")
            draw.text((x-DX-10, y+DY+10), str(node_id), font=font, fill="black", anchor="mm")
        for edge in self.edges:
            a, b = edge.get("a"), edge.get("b")
            node_a, node_b = get_node(a, self.nodes), get_node(b, self.nodes)
            a_cx, a_cy = node_a.get("x"), node_a.get("y")
            b_cx, b_cy = node_b.get("x"), node_b.get("y")
            a_x, a_y = get_x(a_cx), get_y(a_cy)
            b_x, b_y = get_x(b_cx), get_y(b_cy)
            a_x, a_y, b_x, b_y = update_edge(a_x, a_y, b_x, b_y)
            draw.line((a_x, a_y, b_x, b_y), fill="red")

        for a_id, agent in self.agents.items():
            s_node_id = agent.get("s")
            x, y = self.get_node_rect(s_node_id)

            draw.rectangle((x - AW2, y - AH2, x + AW2, y + AH2), fill="green")
            draw.text((x, y), str(a_id), font=font, fill="white", anchor="mm")

            p = agent.get("p")
            if p is not None:
                n_id = p[0]
                x, y, = self.get_node_d_rect(s_node_id, n_id)
                draw.rectangle((x - AW4, y - AH4, x + AW4, y + AH4), fill="green")
                draw.text((x, y), str(len(p)), font=font, fill="white", anchor="mm")

            f_node_id = agent.get("f")
            f_node = get_node(f_node_id, self.nodes)
            cx, cy = f_node.get("x"), f_node.get("y")
            x, y = get_x(cx), get_y(cy)
            draw.ellipse((x - AW2, y - AH2, x + AW2, y + AH2), fill="white")
            draw.text((x, y), str(a_id), font=font, fill="black", anchor="mm")

        image.save(path)
