import os

from .scene import Scene
from .decision import Decision

_SOLVER_NAME = "HLS-PBS"


class Solver:
    def __init__(self, graph, n_agents, map_name, result_path, random_seed):
        self.scene = Scene(graph)
        self.scene.place_random_agents(n_agents, random_seed=random_seed)
        self.map_name = map_name
        self.result_path = result_path
        self.error = ""
        self.n_decision = 0

    @property
    def name(self):
        return _SOLVER_NAME

    def fit(self, decision, verbose=0) -> bool:
        decision.start_fit()
        if verbose > 0:
            self.scene.make_map_image(os.path.join(self.result_path,
                                                   f"{self.map_name}.{self.scene.decision_id}.0"))
        has_collusion = True
        while self.scene.try_next():
            if not self.scene.next():
                # all finished
                has_collusion = False
                break
            t = self.scene.t + 1
            if verbose > 0:
                self.scene.make_map_image(os.path.join(self.result_path,
                                                       f"{self.map_name}.{self.scene.decision_id}.{t}"))
        if has_collusion:
            t = self.scene.t + 1
            n = len(self.scene.collisions)
            self.error = f"scene {t} has {n} collision(s)"
        return not has_collusion

    def make_result(self, result_path, map_name):
        self.scene.make_result(result_path, map_name, self.name, self.n_decision)

    def update_plan(self, decision, n_agent) -> bool:
        self.scene.constraints[n_agent] = decision.constraints[n_agent]
        path = self.scene.detect_optimal_path(n_agent)
        decision.plan[n_agent] = path
        return path is not None

    def hls_pbs(self, verbose=0):
        self.error = ""

        self.n_decision = 1
        root = Decision(self.scene, self.n_decision)
        for a_i in self.scene.agents:
            success = self.update_plan(root, a_i)
            if not success:
                a = self.scene.debug.get("a")
                s = self.scene.debug.get("s")
                f = self.scene.debug.get("f")
                self.error = f"No solution: cannot build any path from vertex {s} to {f} for agent {a}"
                return False

        root.calc_cost()

        stack = [root]
        while len(stack) > 0:
            n = stack[-1]
            del stack[-1]

            if self.fit(n, verbose=verbose):
                return True

            dd = []
            for c in self.scene.collisions:
                a_id = c.get("a")
                agent = self.scene.agents[a_id]
                i = c.get("i")
                ii = c.get("ii")

                self.n_decision += 1
                # to avoid of infinite cycle
                if self.n_decision > 100:
                    break

                n1 = Decision(self.scene, self.n_decision)
                n1.plan = n.plan
                n1.constraints = n.constraints
                n1.agent_sq = n.agent_sq

                # update constraints
                f = agent["f"]
                n1.update_constraints(a_id, (i, ii), f)
                # update agents sequence
                n1.update_sequence(a_id)

                success = self.update_plan(n1, a_id)
                if success:
                    n1.calc_cost()
                    dd.append(n1)
            if len(dd) > 1:
                dd = sorted(dd, key=lambda d: d.cost, reverse=True)
            for _d in dd:
                stack.append(_d)

        self.error = f"No solution: {self.error}"
        return False
