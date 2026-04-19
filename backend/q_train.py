import json
from q import QTradingBot



def train(model_name, epoch, window_size = 5):
    history_buffer_path = f"history/{model_name}.json"
    q_table_path = f"qtable/{model_name}.json"

    bot = QTradingBot( window_size=window_size, filename=q_table_path, epsilon = 0.3)
    history_buffer = []
    with open(history_buffer_path, 'r', encoding='utf-8') as f:
        history_buffer = json.load(f)
    print(f"load history_buffer len: {len(history_buffer)}")

    #history_buffer dang [1,-1,1,1,...] cac so 1, va -1

    for e in range(epoch):
        print(f"epoch {e}")
        for i in range(window_size, len(history_buffer)): 
            history = history_buffer[i - window_size : i]
            current_state = bot.get_state(history)
            action = bot.choose_action(current_state)
            result = history_buffer[i] 
            reward = result if action == 1 else 0
            next_history = history[1:] + [result]
            next_state = bot.get_state(next_history)

            bot.update_q(current_state, action, reward, next_state)

    bot.save_q_table()


train(model_name = "decision_tree", epoch = 1000)
train(model_name = "knn", epoch = 1000)
train(model_name = "random_forest", epoch = 1000)