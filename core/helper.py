from typing import Optional

from .conf import CW, CH, CW2, CH2, DX, DY


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
