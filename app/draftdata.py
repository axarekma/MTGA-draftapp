import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from itertools import combinations
from tqdm.auto import tqdm
import pandas as pd
import json
import re

from .scrape import getdata
from .tierlist import DraftData


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


class DraftData:
    def __init__(self, expansion=None, format=None, deck_color=""):
        self.DATA = dict()
        self.expansion = expansion
        self.format = format
        self.deck_color = deck_color
        self._df_proc = None

        self.gp_wp = None
        self.gih_wp = None

    @property
    def df_name(self):
        return "data/" + self.expansion + self.format + self.deck_color + ".pkl"

    def load(self):

        try:
            self.df = pd.read_pickle(self.df_name)
        except:
            print(f"Failed to load {self.df_name}, scraping")
            self.update()
            self.load()

    def save(self):
        self.df.to_pickle(self.df_name)

    def update(self):
        self.df = getdata(
            expansion=self.expansion, format=self.format, deck_color=self.deck_color
        )
        self.save()

    @property
    def df_proc(self):
        if self._df_proc is None:
            self.process()
        return self._df_proc

    def process(self, gp_wp=None, gih_wp=None, gpweight=True):
        df = self.df.copy()
        GP_score = df["GP WR"].isna().sum() / len(df)
        GIH_score = df["GIH WR"].isna().sum() / len(df)

        df["GP WR"] = df["GP WR"].apply(percentage2val)
        df["OH WR"] = df["OH WR"].apply(percentage2val)
        df["GD WR"] = df["GD WR"].apply(percentage2val)
        df["GIH WR"] = df["GIH WR"].apply(percentage2val)
        df["GND WR"] = df["GND WR"].apply(percentage2val)
        df["IWD"] = df["IWD"].apply(pp2val)
        # df["IWD"].fillna(0.0, inplace=True)
        df["Color"].fillna("", inplace=True)

        # df = df.dropna(how="any", axis=0)
        self.gp_wp = df["GP WR"].mean()
        self.gih_wp = df["GIH WR"].mean()

        mean_wp = gp_wp if gp_wp else self.gp_wp
        mean_gih = gih_wp if gih_wp else self.gih_wp

        df["GP WR"].fillna(0, inplace=True)
        df["OH WR"].fillna(0, inplace=True)
        df["GIH WR"].fillna(0, inplace=True)
        df["IWD"].fillna(0, inplace=True)

        df["WP"] = (df["GP WR"] + df["GIH WR"]) / 2

        if GP_score > 0.95 or GIH_score > 0.95:
            print(" \n", self.deck_color, "has less that 5% data")
            df["weight"] = 0
            df["metric"] = 0
            df["metric_ih"] = 0
        else:
            if gpweight:
                df["weight"] = (df["# GP"] / df["# Picked"]).clip(lower=0.5)
            else:
                df["weight"] = (df["# GP"] / df["# Picked"]).clip(lower=0.1, upper=1.0)
            df["metric"] = df["weight"] * (df["WP"] - mean_wp)
            df["metric_ih"] = df["weight"] * (df["GIH WR"] - mean_gih)

        df["weight"] = df["weight"].astype(float).round(decimals=2)
        df["ALSA"] = df["ALSA"].astype(float).round(decimals=2)

        df["metric"] = (1000 * df["metric"]).astype("int32")
        df["metric_ih"] = (1000 * df["metric_ih"]).astype("int32")

        df["WP"] = (1000 * df["WP"]).astype("int32")
        df["OH WR"] = (1000 * df["OH WR"]).astype("int32")
        df["GIH WR"] = (1000 * df["GIH WR"]).astype("int32")

        df_list = df[
            [
                "Name",
                "Color",
                "Rarity",
                "ALSA",
                "WP",
                # "OH WR",
                "GIH WR",
                "IWD",
                "weight",
                "metric",
                "metric_ih",
            ]
        ]
        df_list.sort_values(["Color", "Name"])

        self._df_proc = df_list


def highlight(s, names, pick=1):
    colorpairs = [p[0] + p[1] for p in list(combinations("WUBRG", 2))]

    pd.options.display.precision = 3
    if s.name not in names and s.name not in colorpairs:
        return [""] * len(s)

    # print(s)

    s_val = pd.to_numeric(s)
    is_min = s == s_val.min()
    is_max = (s > 0) & (s == s_val.max())
    is_positive = s >= 0
    is_negative = s < 0
    is_bad = s < -10

    color = ["#d7191c", "#fdae61", "#a6d96a", "#1a9641"]
    style_min = f"background-color: {color[0]}"
    style_med = f"background-color: {color[1]}"
    style_pos = f"background-color: {color[2]}"
    style_max = f"background-color: {color[3]}"
    retval = []
    if s.name == "GIH WR":
        top_three = s_val.nlargest(3).values
        is_top = [v in top_three for v in s_val]
        for top in is_top:
            if top:
                retval.append(style_max)
            else:
                retval.append("")
        return retval

    if s.name == "ALSA":
        wheeling = s_val.nlargest(max(0, 16 - pick - 8)).values
        top_three = s_val.nsmallest(3).values
        is_wheeling = [v in wheeling for v in s_val]
        is_signal = [v in top_three for v in s_val]
        for wh, sig in zip(is_wheeling, is_signal):
            if wh:
                retval.append(style_min)
            elif sig:
                retval.append(style_max)
            else:
                retval.append("")
        return retval

    # print(s.name)
    for val, cmin, cmax, cpos, cneg, cbad in zip(
        s_val, is_min, is_max, is_positive, is_negative, is_bad
    ):
        if s.name == "ALSA":
            if val + 2 < pick:
                retval.append(style_max)
            elif val - 1 > pick:
                retval.append(style_min)
            else:
                retval.append("")
        elif cbad:
            retval.append(style_min)
        elif cmax:
            retval.append(style_max)
        elif cpos:
            retval.append(style_pos)
        elif cneg:
            retval.append(style_med)
        else:
            retval.append("")

    return retval


class SetData:
    def __init__(self, code=None, draftmode=None):
        self.set = code
        self.draftmode = draftmode

        with open("data/mtgaid_to_name.txt") as f:
            self.id_data = json.load(f)

        self.col_tag = [p[0] + p[1] for p in list(combinations("WUBRG", 2))]

        self.setdata = None
        self.coldata = dict()
        self.loaded = False

    def update_data(self):
        self.setdata = DraftData(self.set, self.draftmode)
        self.setdata.update()
        for col in tqdm(self.col_tag):
            self.coldata[col] = DraftData(self.set, self.draftmode, deck_color=col)
            self.coldata[col].update()

    def load_data(self):
        print("Loading ", self.set, self.draftmode)
        self.setdata = DraftData(self.set, self.draftmode)
        self.setdata.load()
        self.setdata.process()
        for col in tqdm(self.col_tag):
            self.coldata[col] = DraftData(self.set, self.draftmode, deck_color=col)
            self.coldata[col].load()
            # self.coldata[col].process(self.setdata.gp_wp, self.setdata.gih_wp)
            self.coldata[col].process(gpweight=False)
        self.loaded = True

    def save_data(self):
        pass

    def all_frame(self, col=None):
        df_all = self.setdata.df_proc.copy()
        for colorpair in self.col_tag:
            if col is None or col in colorpair:
                # df_all[colorpair] = self.coldata[colorpair].df_proc["WP"]
                df_all[colorpair] = self.coldata[colorpair].df_proc["metric_ih"]
        return df_all

    def pauper_frame(self, col=None):
        df_all = self.setdata.df_proc.copy()
        for colorpair in self.col_tag:
            if col is None or col in colorpair:
                # df_all[colorpair] = self.coldata[colorpair].df_proc["WP"]
                df_all[colorpair] = self.coldata[colorpair].df_proc["metric_ih"]

        return df_all[df_all["Rarity"].str.contains("|".join(["C", "U"]))]

    def draft_frame(self, cards, col=None):

        df_all = self.all_frame(col)

        pick_no = 16 - len(cards)
        # df_all["p_seen"] = np.exp(-(pick_no - 1) / df_all["ALSA"])
        df_nonan = df_all.replace(np.nan, "", regex=True)

        # handlse split cards
        split_cards = []
        for c in cards:
            parts = c.split(" //")
            split_cards.extend(parts)

        # handle e.g. +2 mace
        safe_matches = [re.escape(m) for m in split_cards]

        df_sel = df_nonan[df_nonan["Name"].str.contains("|".join(safe_matches))]
        df_ret = df_sel.sort_values(["metric"], ascending=False)
        # df_ret.style.set_caption("Hello World")

        return df_ret.style.apply(
            highlight,
            names=["ALSA", "WP", "OH WR", "GIH WR", "IWD", "metric", "metric_ih"],
            pick=pick_no,
        )

    def draft_deck(self, deck, col=None, col2=None):
        df_all = self.setdata.df_proc.copy()
        for colorpair in self.col_tag:
            if col is None or col in colorpair:
                df_all[colorpair] = self.coldata[colorpair].df_proc["metric_ih"]
                df_all[f"{colorpair}_GIH"] = self.coldata[colorpair].df_proc["GIH WR"]
            if col2 is not None and col2 in colorpair:
                df_all[colorpair] = self.coldata[colorpair].df_proc["metric_ih"]

        # return deckdf(deck, df_all).sort_values(["metric"], ascending=False)
        return deckdf(deck, df_all).sort_values([col, "metric"], ascending=False)


def deckdf(deck, df):
    import re

    rows = []
    p = re.compile(r"([0-9]) ([^\(]*)( \(([\w]*)\))?( [\d]*)?$")
    for line in deck.split("\n"):
        line = line.rstrip()
        m = p.match(line)

        if m:
            name = m.group(2)
            amount = int(m.group(1))
            #         print(amount, name)
            row = df[df["Name"] == name]
            if len(row):
                for n in range(amount):
                    rows.append(row.to_dict("records")[0])
            else:
                print(name, "not found")

    df_deck = pd.DataFrame(rows)
    df_deck = df_deck.sort_values("metric", ascending=False)
    return df_deck
