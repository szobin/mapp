class Decision:
    def __init__(self, scene, n=0):
        self.scene = scene
        self.plan = {a_id: [] for a_id in self.scene.agents}
        self.agent_sq = [a_id for a_id in self.scene.agents]
        self.constraints = {a_id: [] for a_id in self.scene.agents}
        self.cost = 0
        self.n = n

    def start_fit(self):
        for a_id in self.plan:
            path = self.plan[a_id]
            self.scene.agents[a_id]["p"] = path

        self.scene.constraints = self.constraints
        self.scene.agent_sq = self.agent_sq
        self.scene.decision_id = self.n
        self.scene.start()

    def calc_cost(self):
        self.cost = max([len(path) if path is not None else 0 for a_id, path in self.plan.items()])

    def update_constraints(self, a_id, edge):
        agent = self.scene.agents[a_id]
        f = agent.get("f")
        for e in edge:
            if (e is not None) and (e != f):
                self.constraints[a_id].append(e)

    def update_sequence(self, a_i, a_j):
        i = self.agent_sq.index(a_i)
        j = self.agent_sq.index(a_j) if a_j is not None else 0
        if i != j:
            v = self.agent_sq[i]
            self.agent_sq[i] = self.agent_sq[j]
            self.agent_sq[j] = v
