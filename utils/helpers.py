# utils/helpers.py
import matplotlib.pyplot as plt

def plot_bar_chart(df, x_col, y_col, title):
    plt.figure(figsize=(10, 6))
    plt.bar(df[x_col], df[y_col])
    plt.title(title)
    plt.xticks(rotation=90)
    return plt
