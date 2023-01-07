import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose


def helper(df, unit, name, window, percentage=True, decompose=False, model=None, period=None):
    plt.figure(figsize=(15, 10))

    # Set the title, add decomposition if decomposition is set to True
    title = f"{name}: music history"
    if decompose:
        title += ", decomposition"
    plt.title(title)

    mask = (df[unit] == name)

    # Calculate the requested metric
    data = df[mask]["Stickiness (%)"] if not percentage else df[mask]["Play Duration (Minutes)"]

    series = data.rolling(window).mean()

    if not decompose:
        plt.plot(series, label=name, alpha=0.5)
    else:
        decomposition = seasonal_decompose(series.dropna(), model=model, period=period)
        plt.plot(decomposition.trend, label=name, alpha=0.5)

    plt.xticks(df[mask].index[::50], rotation=90)

    plt.show()


def plot_history(df, unit, name, window, percentage=True, decompose=False, model=None, period=None):
    if decompose:
        assert model is not None and period is not None

    helper(unit=unit, df=df, name=name, window=window, percentage=percentage, decompose=decompose, model=model, period=period)