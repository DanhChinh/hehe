from handle_db import *

update_local_db()
df, data, label = load_data_from_pickle()
print(df)