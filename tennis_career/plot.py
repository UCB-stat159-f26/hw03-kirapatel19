import matplotlib.pyplot as plt


def plot_age_difference(matches):
    """Plot player age against the age difference with opponents."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for result, color, label in [
        ("W", "#639caa", "Win"),
        ("L", "#df855b", "Loss"),
    ]:
        subset = matches[matches["result"] == result]
        ax.scatter(
            subset["player_age"], subset["age_difference"],
            color=color, label=label, s=18, alpha=0.7
        )

    ax.axhline(0, color="gray", linewidth=1)
    ax.set_xlabel("Player age (years)")
    ax.set_ylabel("Player age − opponent age (years)")
    ax.set_title(matches.attrs.get("player_name", "Career matches"))
    ax.legend()
    fig.tight_layout()
    return ax
    