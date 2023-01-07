import json
import numpy as np
import pandas as pd
import datetime as dt


def get_semester(x):
    if x > "2022-07-01":
        return "F2022 Duke Senior"
    if x > "2022-01-01":
        return "S2022 Duke Junior"
    if x > "2021-07-01":
        return "F2021 Duke Junior"
    if x > "2021-01-01":
        return "S2021 Online Sophomore"
    if x > "2020-07-01":
        return "F2020 Online Sophomore"
    if x > "2020-01-01":
        return "S2020 Online Freshman"
    if x > "2019-07-01":
        return "F2019 DKU Freshman"

    if x > "2019-01-01":
        return "S2019 UNAM Freshman"
    if x > "2018-07-01":
        return "F2018 UNAM Freshman"

    if x > "2018-01-01":
        return "S2018 HS Senior"
    if x > "2017-07-01":
        return "F2017 HS Senior"
    if x > "2017-01-01":
        return "S2017 HS Junior"
    return "F2017 HS Junior <"

class DataPreprocessing:
    def __init__(self, apple_music_play_history_folder):
        self.apple_music_play_history_folder = apple_music_play_history_folder
        self.apple_music_library = None
        self.df_treated = None
        self.data = None

    def initial_treatment(self):
        # Read the raw file from the given directory
        df = pd.read_csv(f"{self.apple_music_play_history_folder}/Apple Music - Play History Daily Tracks.csv")

        # Expand hours to include all 24 hours per day
        hours_expanded = df["Hours"].str.split(", ").apply(lambda x: [i if str(i) in x else -1 for i in range(0, 24)])

        # Approximate the play time per hour by assuming a uniform distribution
        play_time = df["Play Duration Milliseconds"] / df["Hours"].str.split(',').str.len()

        # Set each number of hours in the original dataframe
        df["Hours Exp"] = hours_expanded
        # Set the approximated play time for each song
        df["Played Time (Approximation) Minutes"] = play_time / (1000 * 60)
        # Explode hours to include all 24 hours per day for every single song
        df_exp = df.explode('Hours Exp')

        # We exclude all those hours that map to -1
        df_exp = df_exp[df_exp["Hours Exp"] > -1]
        # Drop the original column "Hours" from our current dataframe to avoid confusion
        df_exp.drop("Hours", axis=1, inplace=True)

        # Date Played
        date = df_exp["Date Played"].astype(str) + " " + df_exp["Hours Exp"].astype(str)
        date = date.apply(lambda x: x[:4] + "-" + x[4:6] + "-" + x[6:8] + " " + x[8:] + ":00:00")
        dates = date.apply(lambda x: dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))

        # Get all the existing hours in between the earliest and latest date
        hours_delta = dates.max() - dates.min()
        hours_delta = hours_delta.total_seconds() / (60 * 60)

        all_dates = []
        for hour in range(0, int(hours_delta) + 1):
            all_dates.append(dates.min() + dt.timedelta(hours=hour))
        all_dates = pd.Series(all_dates)

        all_index_dates = pd.DataFrame(all_dates)
        all_index_dates["available_data"] = 0
        all_index_dates.set_index(0, inplace=True)

        df_exp['Date'] = dates

        all_index_dates["available_data"].loc[df_exp['Date']] = 1
        all_index_dates.reset_index(inplace=True)

        all_index_dates.rename(columns={0: "Date"}, inplace=True)
        all_index_dates.head()

        # Merge all existing dates into the existing expanded dataframe
        df_exp2 = df_exp.merge(all_index_dates, how="outer", left_on="Date", right_on="Date")
        df_exp2['day'] = df_exp2["Date"].apply(lambda x: x.strftime("%Y-%m-%d"))

        # Save the new expanded dataframe as df_treated
        df_exp2 = df_exp2[df_exp2["Date"] >= "2017-01-01"]

        self.df_treated = df_exp2

    def load_apple_music_library(self):
        # Get filename
        json_filename = f"{self.apple_music_play_history_folder}/Apple Music Library Tracks.json"

        # Open apple music library json file
        with open(json_filename) as json_file:
            music_library = json.load(json_file)

        apple_music_library = pd.DataFrame.from_records(music_library)

        columns = [
            "Apple Music Track Identifier",
            "Title",
            "Artist",
            "Album",
            "Genre",
            "Track Duration"
        ]

        apple_music_library = apple_music_library[columns]

        apple_music_library.replace("Adult Alternative", "Alternative", inplace=True)
        apple_music_library.replace("Alt Rock", "Alternative", inplace=True)
        apple_music_library.replace("Alternativa", "Alternative", inplace=True)
        apple_music_library.replace("Alternative & Punk", "Alternative", inplace=True)
        apple_music_library.replace("Alternative Rock", "Alternative", inplace=True)
        apple_music_library.replace("Alternative-Rock", "Alternative", inplace=True)

        apple_music_library.replace("Hard Rock", "Rock", inplace=True)
        apple_music_library.replace("Rock y Alternativo", "Rock", inplace=True)

        apple_music_library.replace("Alternative Rap", "Hip-Hop/Rap", inplace=True)
        apple_music_library.replace("Hip-Hop", "Hip-Hop/Rap", inplace=True)
        apple_music_library.replace("Rap", "Hip-Hop/Rap", inplace=True)
        apple_music_library.replace("Rap & Hip-Hop", "Hip-Hop/Rap", inplace=True)
        apple_music_library.replace("R&B/Soul", "Hip-Hop/Rap", inplace=True)
        apple_music_library.replace("Old School Rap", "Hip-Hop/Rap", inplace=True)
        apple_music_library.replace("Latin Rap", "Hip-Hop/Rap", inplace=True)

        apple_music_library.replace("Classical Crossover", "Classical", inplace=True)
        apple_music_library.replace("Classical Music / Instrumental", "Classical", inplace=True)

        apple_music_library.replace("Linkin Park", "LINKIN PARK", inplace=True)

        apple_music_library.drop_duplicates(inplace=True)
        apple_music_library.dropna(inplace=True)

        self.apple_music_library = apple_music_library

    def join_library_and_history(self):
        df_full = self.df_treated.merge(self.apple_music_library, how="left", left_on="Track Identifier",
                                        right_on="Apple Music Track Identifier")

        columns = [
            'Apple Music Track Identifier',
            'Play Duration Milliseconds',
            'Played Time (Approximation) Minutes',
            'day',
            'Track Duration',
            'Genre',
            'Album',
            'Title',
            'Artist'
        ]

        df_full = df_full[columns]

        df_full["Played Time (Approximation) Minutes"] = df_full["Played Time (Approximation) Minutes"].replace(np.nan,0)
        df_full["Play Duration Milliseconds"] = df_full["Play Duration Milliseconds"].replace(np.nan, 0)
        df_full["Track Duration"] = df_full["Track Duration"].replace(np.nan, 0) / (1000 * 60)
        df_full["Apple Music Track Identifier"] = df_full["Apple Music Track Identifier"].fillna(-1)

        self.data = df_full


class CreateHistory(DataPreprocessing):
    def __init__(self, apple_music_play_history_folder):
        super().__init__(apple_music_play_history_folder)
        self.tracks = {}
        self.albums = {}
        self.artists = {}
        self.genres = {}

    def calculate_track_history(self, save_to=None):
        df_time_per_track = self.data.groupby(['day', 'Title', 'Album', 'Genre', 'Artist']).sum().reset_index()
        df_time_on_app = self.data.fillna(0).groupby('day').sum().reset_index()[["day", "Play Duration Milliseconds"]].rename(columns={"Play Duration Milliseconds": "Time on Apple Music"})

        df_unfilled = df_time_per_track.merge(df_time_on_app, how="right", left_on="day", right_on="day")
        df_unfilled['Stickiness (%)'] = (100*df_unfilled["Play Duration Milliseconds"]/df_unfilled["Time on Apple Music"]).replace([np.inf, -np.inf, np.nan], 0)

        criteria = ['Title', 'Album', 'Genre', 'Artist']
        df_filled = pd.pivot(df_unfilled, index='day', columns=criteria, values="Stickiness (%)")
        df_filled_melted = pd.melt(df_filled, value_vars=df_filled.columns.tolist(), ignore_index=False, value_name="Stickiness (%)")

        df_tracks = df_filled_melted.merge(df_time_on_app, how="left", left_on="day", right_on="day").replace([np.inf, -np.inf, np.nan], 0)
        df_tracks["Play Duration (Minutes)"] = df_tracks["Stickiness (%)"]*df_tracks["Time on Apple Music"]/360000

        columns = [
            "day",
            "Title",
            "Album",
            "Artist",
            "Genre",
            "Stickiness (%)",
            "Play Duration (Minutes)",
            "Time on Apple Music"
        ]

        df_tracks = df_tracks.drop_duplicates()[columns]
        df_tracks.set_index('day', inplace=True)

        df_tracks["Track"] = df_tracks["Title"].astype(str) + " -- " + df_tracks["Album"].astype(str) + " -- " + df_tracks["Artist"].astype(str)

        for unit in ["Track", "Album", "Artist", "Genre"]:
            temp_sum = df_tracks.groupby(unit).sum()["Play Duration (Minutes)"]
            temp_mean = 100*temp_sum/temp_sum.sum()
            relevant = temp_mean >= 1.0

            if unit == "Track":
                self.tracks["Relevant"] = temp_mean[relevant].index
                self.tracks["Irrelevant"] = temp_mean[~relevant].index
            if unit == "Album":
                self.albums["Relevant"] = temp_mean[relevant].index
                self.albums["Irrelevant"] = temp_mean[~relevant].index
            if unit == "Artist":
                self.artists["Relevant"] = temp_mean[relevant].index
                self.artists["Irrelevant"] = temp_mean[~relevant].index
            if unit == "Genres":
                self.genres["Relevant"] = temp_mean[relevant].index
                self.genres["Irrelevant"] = temp_mean[~relevant].index

        if save_to is not None:
            df_tracks.to_csv(save_to, index=True, header=True)

        return df_tracks
