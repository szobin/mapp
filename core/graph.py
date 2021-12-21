import os

from .helper import to_node, to_edge, check_edge, get_node, get_x, get_y, update_edge
from .conf import AW2, AH2, NW2, NH2, DX, DY


class Graph:

    def __init__(self):
        self.nodes = {}
        self.edges = []

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

    def draw_map(self, draw, font):
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
