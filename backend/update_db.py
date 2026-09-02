from handle_db import *
from beautydata import *



if __name__ == "__main__":

    update_local_db()
    df, data, label = load_data_from_pickle()

    X_clean, y_clean, le = clean_data(data, label)
    clean = {'X_clean': X_clean, 'y_clean': y_clean, 'le': le}
    save_clean(clean)