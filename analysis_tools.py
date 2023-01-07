import pandas as pd


def tracks_performance(df, rel_to="Album", min_unit="Track"):
    criteria = "Play Duration (Minutes)"

    unit_criteria = ["Artist"]
    if min_unit == "Album":
        unit_criteria += ["Album"]
    if min_unit == "Track":
        unit_criteria += ["Album", "Title"]

    left = df.groupby(unit_criteria).sum().reset_index()[unit_criteria + [criteria]]

    if rel_to=="Artist":
        right = df.groupby("Artist").sum().reset_index()[["Artist", criteria]]
        df_performance = left.merge(right, how="left", left_on="Artist", right_on="Artist")

    if rel_to=="Album":
        right = df.groupby(["Artist", "Album"]).sum().reset_index()[["Artist", "Album", criteria]]
        df_performance = left.merge(right, how="left", left_on=["Artist", "Album"], right_on=["Artist", "Album"])

    df_performance["Stickiness (%)"] = df_performance[f"{criteria}_x"]/df_performance[f"{criteria}_y"]

    df_performance.rename(columns={f"{criteria}_x": "Track Play Duration", f"{criteria}_y":f"{rel_to} Play Duration"}, inplace=True)

    return df_performance


def get_performance(df, group, name):
    mask = df[group] == name
    return df[mask]
