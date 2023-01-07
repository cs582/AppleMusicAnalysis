import pandas as pd
from data_tools import CreateHistory


class Analysis(CreateHistory):
    def __init__(self, apple_music_play_history_folder, data_filepath):
        self.apple_music_play_history_folder = apple_music_play_history_folder
        self.data_filepath = data_filepath
        self.data_preprocessing = None
        self.tracks_history = None

    def labeling(self, get_from=None):
        # If the data is not available, then re-calculate
        base_data_directory = self.apple_music_play_history_folder

        # Data preprocessing
        self.data_preprocessing = CreateHistory(base_data_directory)
        self.data_preprocessing.initial_treatment()
        self.data_preprocessing.load_apple_music_library()
        self.data_preprocessing.join_library_and_history()
        self.data_preprocessing.calculate_track_history(save_to=f"{self.data_filepath}/track_history.csv")

        self.tracks_history = pd.read_csv(f"{self.data_filepath}/track_history.csv", index_col=0)