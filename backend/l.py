import numpy as np
from collections import defaultdict


class PeakValleyQLearning:

    HOLD = 0
    BUY = 1
    SELL = 2

    FLAT = 0
    LONG = 1

    def __init__(
        self,
        alpha=0.1,
        gamma=0.95,
        epsilon=0.1
    ):

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        self.q = defaultdict(
            lambda: np.zeros(3)
        )

        self.reset()

    def reset(self):

        self.position = self.FLAT
        self.entry_price = None

    # ==========================
    # Feature
    # ==========================

    def trend(self, prices):

        if len(prices) < 20:
            return 1

        ma5 = np.mean(prices[-5:])
        ma20 = np.mean(prices[-20:])

        if ma5 > ma20:
            return 2

        if ma5 < ma20:
            return 0

        return 1

    def momentum(self, prices):

        if len(prices) < 6:
            return 2

        change = (
            prices[-1] - prices[-6]
        ) / prices[-6]

        if change < -0.03:
            return 0

        if change < -0.01:
            return 1

        if change < 0.01:
            return 2

        if change < 0.03:
            return 3

        return 4

    def get_state(self, prices):

        return (
            self.position,
            self.trend(prices),
            self.momentum(prices)
        )

    # ==========================
    # Action
    # ==========================

    def valid_actions(self):

        if self.position == self.FLAT:
            return [self.HOLD, self.BUY]

        return [self.HOLD, self.SELL]

    def choose_action(self, state):

        actions = self.valid_actions()

        if np.random.random() < self.epsilon:
            return np.random.choice(actions)

        qvals = self.q[state]

        best = actions[0]
        best_q = qvals[best]

        for a in actions:

            if qvals[a] > best_q:
                best_q = qvals[a]
                best = a

        return best

    # ==========================
    # Execute
    # ==========================

    def execute(self, action, price):

        reward = 0

        if (
            action == self.BUY
            and self.position == self.FLAT
        ):

            self.position = self.LONG
            self.entry_price = price

        elif (
            action == self.SELL
            and self.position == self.LONG
        ):

            reward = (
                price
                - self.entry_price
            )

            self.position = self.FLAT
            self.entry_price = None

        return reward

    # ==========================
    # Update Q
    # ==========================

    def update(
        self,
        state,
        action,
        reward,
        next_state
    ):

        old_q = self.q[state][action]

        next_q = np.max(
            self.q[next_state]
        )

        self.q[state][action] = (
            old_q
            + self.alpha
            * (
                reward
                + self.gamma * next_q
                - old_q
            )
        )

    # ==========================
    # Train
    # ==========================

    def train(
        self,
        prices,
        epochs=100
    ):

        for _ in range(epochs):

            self.reset()

            for i in range(30, len(prices)):

                history = prices[:i]

                state = self.get_state(
                    history
                )

                action = self.choose_action(
                    state
                )

                reward = self.execute(
                    action,
                    prices[i]
                )

                next_state = self.get_state(
                    prices[:i+1]
                )

                self.update(
                    state,
                    action,
                    reward,
                    next_state
                )

    # ==========================
    # Runtime
    # ==========================

    def predict(self, prices):

        state = self.get_state(prices)

        actions = self.valid_actions()

        qvals = self.q[state]

        best = actions[0]
        best_q = qvals[best]

        for a in actions:

            if qvals[a] > best_q:
                best_q = qvals[a]
                best = a

        return best

# prices = np.load("prices.npy")

agent = PeakValleyQLearning()

agent.train(
    prices,
    epochs=300
)