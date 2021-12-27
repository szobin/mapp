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

            if verbose > 0:
                t = self.scene.t + 1
                self.scene.make_map_image(os.path.join(self.result_path,
                                                       f"{self.map_name}.{self.scene.decision_id}.{t}"))

        if has_collusion:
            t = self.scene.t + 1
            if verbose > 0:
                self.scene.make_map_image(os.path.join(self.result_path,
                                                       f"{self.map_name}.{self.scene.decision_id}.{t}"))
            n = len(self.scene.collisions)
            self.error = f"decision {self.n_decision}: scene {t} has {n} collision(s)"
        return not has_collusion

    def make_result(self, result_path):
        return self.scene.make_result(result_path, self.map_name, self.name, self.n_decision, align=True)

    def update_plan(self, decision, n_agent) -> bool:
        self.scene.constraints[n_agent] = decision.constraints[n_agent]
        path = self.scene.detect_optimal_path(n_agent)
        decision.plan[n_agent] = path
        if path is None:
            agent = self.scene.agents[n_agent]
            s = agent.get("s")
            f = agent.get("f")
            self.error = f"cannot build any path from vertex {s} to {f} for agent {n_agent}"

        return path is not None

    def hls_pbs(self, verbose=0, max_cycles=100):
        self.error = ""

        self.n_decision = 1
        root = Decision(self.scene, self.n_decision)
        for a_i in self.scene.agents:
            success = self.update_plan(root, a_i)
            if not success:
                self.error = "No solution: " + self.error
                return False

        root.calc_cost()

        stack = [root]
        while len(stack) > 0:
            n = stack[-1]
            del stack[-1]

            # check collision here
            if self.fit(n, verbose=verbose):
                return True

            dd = []
            for c in self.scene.collisions:
                a_i = c.get("ai")
                a_j = c.get("aj")
                mode = c.get("mode")
                e_a, e_b = c.get("e")

                self.n_decision += 1
                # to avoid of infinite cycle
                if self.n_decision > max_cycles:
                    break

                n1 = Decision(self.scene, self.n_decision)
                n1.plan = n.plan
                n1.constraints = n.constraints
                n1.agent_sq = n.agent_sq

                # update constraints
                if mode == 'vertex':
                    n1.update_constraints(a_i, (e_b, ))
                else:
                    n1.update_constraints(a_i, (e_a, e_b))
                # update agents sequence
                n1.update_sequence(a_i, a_j)

                success = self.update_plan(n1, a_i)
                if success:
                    n1.calc_cost()
                    dd.append(n1)
            if len(dd) > 1:
                dd = sorted(dd, key=lambda d: d.cost, reverse=True)
            for _d in dd:
                stack.append(_d)

        self.error = "No solution: " + self.error
        return False
