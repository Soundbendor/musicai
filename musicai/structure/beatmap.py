import pandas as pd


class BeatMap:

    def __init__(self):
        columns = ['Note', 'Start', 'Duration']
        _beat_df_ = pd.DataFrame(columns=columns)
        print(_beat_df_)


if __name__ == '__main__':
    BeatMap()
