import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .scrape import getdata

DATA = dict()


class DraftData:
    def __init__(self, expansion, format, deck_color="", tiers=4, ratings=10):
        self.tiers = tiers
        self.ratings = ratings
        if expansion + format + deck_color not in DATA:
            print("Scraping data...", expansion, format)
            DATA[expansion + format + deck_color] = getdata(
                expansion=expansion, format=format, deck_color=deck_color
            )
        print(expansion + format + deck_color)
        self.df = DATA.get(expansion + format + deck_color).copy()

        self.df_processed = self.process()

    def process(self):
        df = self.df.copy()
        # print(df.isna().sum())

        print("Number of cards", len(df))
        GP_score = df["GP WR"].isna().sum() / len(df)
        GIH_score = df["GIH WR"].isna().sum() / len(df)
        print(f"GP_score {GP_score:.3} GIH_score {GIH_score:.3}")

        df["GP WR"] = df["GP WR"].apply(percentage2val)
        df["OH WR"] = df["OH WR"].apply(percentage2val)
        df["GD WR"] = df["GD WR"].apply(percentage2val)
        df["GIH WR"] = df["GIH WR"].apply(percentage2val)
        df["GND WR"] = df["GND WR"].apply(percentage2val)
        df["IWD"] = df["IWD"].apply(pp2val)
        # df["IWD"].fillna(0.0, inplace=True)
        df["Color"].fillna("", inplace=True)

        # df = df.dropna(how="any", axis=0)

        mean_wp = df["GP WR"].mean()
        mean_gif = df["GIH WR"].mean()
        print(f"mean WP", mean_wp)
        print(f"mean GIH WP", mean_gif)

        data = df[["ATA", "GP WR"]].dropna(how="any", axis=0).to_numpy()
        fgp = np.poly1d(np.polyfit(data[:, 0], data[:, 1], 1))

        data = df[["ATA", "GIH WR"]].dropna(how="any", axis=0).to_numpy()
        fgih = np.poly1d(np.polyfit(data[:, 0], data[:, 1], 1))

        df["fgp"] = fgp(df["ATA"])
        df["fgih"] = fgih(df["ATA"])

        df["GP WR"].fillna(df["fgp"], inplace=True)
        df["GIH WR"].fillna(df["fgih"], inplace=True)

        df["WP"] = (df["GP WR"] + df["GIH WR"]) / 2
        df["weight"] = (df["# GP"] / df["# Picked"]).clip(lower=1)
        df["metric"] = df["weight"] * (df["WP"] - mean_wp)
        df["metric_ih"] = df["weight"] * (df["GIH WR"] - mean_gif)

        df["Rating"] = pd.qcut(
            df["metric"], self.ratings, labels=[str(i + 1) for i in range(self.ratings)]
        )

        # f = np.poly1d(np.polyfit(df["ALSA"], df["metric"], 3))
        # df["VORP"] = df["metric"] - f(df["ALSA"])
        df["tier"] = pd.qcut(
            df["ALSA"], self.tiers, labels=[i for i in range(self.tiers)]
        )

        df["weight"] = df["weight"].round(2)
        df["metric"] = (100 * df["metric"]).round(2)
        df["metric_ih"] = (100 * df["metric_ih"]).round(2)
        # df["VORP"] = (100 * df["VORP"]).round(2)

        df["WP"] = df["WP"].round(3)
        df["GIH WR"] = df["GIH WR"].round(3)
        df["GIH WR"] = df["GIH WR"].round(3)

        df_list = df[
            [
                "Name",
                "Color",
                "Rarity",
                "ALSA",
                "tier",
                "WP",
                "OH WR",
                "GIH WR",
                "IWD",
                "weight",
                "metric",
                "metric_ih",
                "Rating",
            ]
        ]
        df_list.sort_values(["Color", "Name"])

        return df_list

    def tierlist(self, col=""):
        if col == "gold":
            mask = self.df_processed["Color"].str.len() > 1
        elif len(col):
            mask = self.df_processed["Color"] == col
        else:
            mask = self.df_processed["Color"] == ""

        return self.df_processed.loc[mask].sort_values(["Name"])

    def draftmeta(self, mode):
        meta(self.df_processed, mode)

    def guilds(self, mode):
        guildmeta(self.df_processed, mode)

    def toptier(self, tier, color="", mode="all", head=10):
        if mode == "all":
            func = alltier
        if mode == "nonland":
            func = nonlandtier
        if mode == "common":
            func = commontier

        return func(self.df_processed, color, tier).head(head)

    def colortier(self, tier, colors, head=10):
        return get_cards(self.df_processed, colors, tier).head(head)


def percentage2val(string):
    try:
        string = string.replace("%", "")
        return float(string) / 100
    except:
        return None


def pp2val(string):
    try:
        string = string.replace("pp", "")
        return float(string)
    except:
        return None


def maketier(df, tiers=4):
    df = df.copy()

    df["GP WR"] = df["GP WR"].apply(percentage2val)
    df["OH WR"] = df["OH WR"].apply(percentage2val)
    df["GD WR"] = df["GD WR"].apply(percentage2val)
    df["GIH WR"] = df["GIH WR"].apply(percentage2val)
    df["GND WR"] = df["GND WR"].apply(percentage2val)
    df["Color"].fillna(" ", inplace=True)

    print(df.isna().any()[lambda x: x])
    df = df.dropna(how="any", axis=0)
    print(df.isna().any()[lambda x: x])

    mean_wp = df["GP WR"].mean()

    df["WP"] = (df["GP WR"] + df["GIH WR"]) / 2
    df["metric"] = df["# GP"] / df["# Picked"] * (df["WP"] - mean_wp)

    df["Rating"] = pd.qcut(df["metric"], 10, labels=[str(i + 1) for i in range(10)])

    f = np.poly1d(np.polyfit(df["ALSA"], df["metric"], 3))
    df["VORP"] = df["metric"] - f(df["ALSA"])
    df["tier"] = pd.qcut(df["ALSA"], tiers, labels=[i for i in range(tiers)])

    df_list = df[
        ["Name", "Color", "Rarity", "WP", "metric", "IWD", "Rating", "tier", "VORP"]
    ]
    df_list.sort_values(["Color", "Name"])

    return df_list


def select_tier(df_col, tier):
    if tier is not None:
        sel = df_col.loc[df_col["tier"] == tier].sort_values(
            ["metric", "GIH WR"], ascending=False
        )
    else:
        sel = df_col.sort_values(["metric", "GIH WR"], ascending=False)
    return sel


def commontier(df_list, color, tier):
    df_sel = df_list[df_list["Rarity"].str.contains("|".join(["C", "U"]))]
    df_col = df_sel[df_sel["Color"].str.contains(color)]
    return select_tier(df_col, tier)


def nonlandtier(df_list, color, tier):
    df_sel = df_list[df_list["Rarity"].str.contains("|".join(["C", "U", "R", "M"]))]
    df_col = df_sel[df_sel["Color"].str.contains(color)]
    return select_tier(df_col, tier)


def alltier(df_list, color, tier):
    df_col = df_list[df_list["Color"].str.contains(color)]
    return select_tier(df_col, tier)


def meta(df, mode="nonland"):

    values = dict()
    from matplotlib.ticker import MaxNLocator

    if mode == "all":
        func = alltier
    if mode == "nonland":
        func = nonlandtier
    if mode == "common":
        func = commontier

    tiers = int(df["tier"].max()) + 1

    for color in "WUBRG":
        values[color] = []
        for tier in range(tiers):
            sel = func(df, color, tier)
            value = sel[sel["metric"] > 0]["metric"].sum()
            values[color].append(value)

    plt.style.use("dark_background")
    plotcol = {"W": "w", "U": "b", "B": "k", "R": "r", "G": "g"}
    ax = plt.axes()
    for c in "WUBRG":
        ax.plot(values[c], c=plotcol[c], label=c)
        ax.plot(values[c], c=plotcol[c], linewidth=3, alpha=0.5)

    # ax.legend()
    ax.set_facecolor("gray")
    ax.set_xlabel("Tier")
    ax.set_ylabel("Value")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title(mode)


def get_cards(df, col, tier):
    all_colors = "WUBRG"

    df_ret = df

    for c in col:
        all_colors = all_colors.replace(c, "")

    for c in all_colors:
        df_ret = df_ret[~df_ret["Color"].str.contains(c)]

    sel = df_ret.loc[df_ret["tier"] == tier].sort_values(["metric"], ascending=False)
    return sel


from itertools import combinations


def guildmeta(df, mode):
    values = dict()
    from matplotlib.ticker import MaxNLocator

    if mode == "all":
        func = alltier
    if mode == "nonland":
        func = nonlandtier
    if mode == "common":
        func = commontier

    tiers = int(df["tier"].max()) + 1

    guilds = list(combinations("WUBRG", 2))
    for guild in guilds:
        # for colors in combinations("WUBRG", 2):
        #     guild = "".join(colors)
        values[guild] = []
        for tier in range(tiers):
            sel = get_cards(df, guild, tier)
            value = sel[sel["metric"] > 0]["metric"].sum()
            values[guild].append(value)

    plt.style.use("dark_background")
    plotcol = {"W": "w", "U": "b", "B": "k", "R": "r", "G": "g"}
    ax = plt.axes()
    for guild in guilds:
        # for colors in combinations("WUBRG", 2):
        #     guild = "".join(colors)
        vals = np.array(values[guild])
        ax.plot(vals - 2, c=plotcol[guild[0]], linewidth=2)
        ax.plot(vals + 2, c=plotcol[guild[1]], linewidth=2)

    # ax.legend()
    ax.set_facecolor("gray")
    ax.set_xlabel("Tier")
    ax.set_ylabel("Value")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title(mode)
