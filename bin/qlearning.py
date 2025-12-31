import itertools
import random
import pandas as pd
import os
import ast
from collections import defaultdict


class QLearningAgent:
    def __init__(self, history, alpha=0.1, gamma=0.9, epsilon=0.1,
                 q_file="q_table.csv", load_if_exists=True):
        self.history = history
        self.models = list(history.keys())
        self.n_models = len(self.models)

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        self.actions = list(itertools.product([0, 1], repeat=self.n_models))
        self.Q = defaultdict(float)

        self.q_file = q_file

        if load_if_exists and os.path.exists(self.q_file):
            self.load_q()

    # ----------- CORE -----------
    def get_state(self, i, j):
        return tuple(self.history[m][i][j] for m in self.models)

    def get_reward(self, i, j, action):
        reward = 0
        for k, m in enumerate(self.models):
            if action[k] == 1 and j + 1 < len(self.history[m][i]):
                reward += self.history[m][i][j + 1]
        return reward

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        qs = [self.Q[(state, a)] for a in self.actions]
        return self.actions[qs.index(max(qs))]
    def choose_max_action(self, state):
        print("choose_max_action()", state)
        best_action = None
        best_score = float("-inf")

        for a in self.actions:
            q = self.Q.get((state, a), 0.0)
            if q > best_score:
                best_score = q
                best_action = a

        return best_action, best_score


    def train(self, epochs=10):
        for _ in range(epochs):
            print('epochs: ',_)
            for i in range(len(next(iter(self.history.values())))):
                length = len(next(iter(self.history.values()))[i])
                for j in range(length - 1):
                    state = self.get_state(i, j)
                    action = self.choose_action(state)
                    reward = self.get_reward(i, j, action)
                    next_state = self.get_state(i, j + 1)

                    max_next_q = max(
                        self.Q[(next_state, a)] for a in self.actions
                    )

                    self.Q[(state, action)] += self.alpha * (
                        reward + self.gamma * max_next_q - self.Q[(state, action)]
                    )

    # ----------- SAVE / LOAD -----------
    def save_q(self):
        rows = []
        for (state, action), q in self.Q.items():
            rows.append({
                "state": str(state),
                "action": str(action),
                "Q": q
            })
        pd.DataFrame(rows).to_csv(self.q_file, index=False)

    def load_q(self):
        df = pd.read_csv(self.q_file)
        for _, row in df.iterrows():
            state = ast.literal_eval(row["state"])
            action = ast.literal_eval(row["action"])
            self.Q[(state, action)] = row["Q"]

    # ----------- EXPORT -----------
    def q_dataframe(self):
        return pd.DataFrame(
            [{"state": s, "action": a, "Q": q}
             for (s, a), q in self.Q.items()]
        ).sort_values("Q", ascending=False)



# agent = QLearningAgent(jsmodels)
# agent.train(epochs=20)

# print(agent.models)
# print(agent.q_dataframe())

