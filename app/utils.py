import json

# import nest_asyncio
# nest_asyncio.apply()
import scrython
import time
import numpy as np
import pandas as pd
from tqdm.auto import trange, tqdm
import json
import re

FOLDER = "c:/Users/axela/appdata/LocalLow/Wizards Of The Coast/MTGA/"
FOLDER = ""


def highlight(s, names):
    pd.options.display.precision = 3
    if s.name not in names:
        return [""] * len(s)

    s_val = pd.to_numeric(s)
    is_min = s == s_val.min()
    is_max = s == s_val.max()
    color = ["#d65f5f", "#5fba7d"]

    style_min = f"background-color: {color[0]}"
    style_max = f"background-color: {color[1]}"
    retval = []
    for cmin, cmax in zip(is_min, is_max):
        if cmin:
            retval.append(style_min)
        elif cmax:
            retval.append(style_max)
        else:
            retval.append("")

    return retval


class Tracker:
    def __init__(self, filename):
        self.filename = filename
        self.draftpacks_id = []

        with open("data/mtgaid_to_name.txt") as f:
            self.id_data = json.load(f)

    def save(self):
        with open("data/mtgaid_to_name.txt", "w") as outfile:
            json.dump(self.id_data, outfile)

    def check_line(self, line):
        search1 = '"DraftPack":'
        search2 = "[UnityCrossThreadLogger]Draft.Notify"

        if search1 in line:
            substring = line[line.find("{") :]
            pack_dict = json.loads(substring)

            cards = [c_id for c_id in pack_dict["payload"]["DraftPack"]]
            return cards

        if search2 in line:
            substring = line[line.find("{") :]
            pack_dict = json.loads(substring)
            cards = [c_id for c_id in pack_dict["PackCards"].split(",")]
            return cards
        return

    def update_lines(self):
        self.draftpacks_id = []
        with open(self.filename, "r", encoding="utf8") as read_obj:
            # Read all lines in the file one by one
            for line in read_obj:
                cards = self.check_line(line)
                if cards:
                    self.draftpacks_id.append(cards)

    def cardlist(self, index=-1):
        if not self.draftpacks_id:
            return []

        card_id = self.draftpacks_id[index]
        for c in card_id:
            if c not in self.id_data:
                print(f"Finding {c}")
                try:
                    card = scrython.cards.ArenaId(id=c)
                    self.id_data[c] = card.name()
                    print(f"Found {card.name()}")
                    time.sleep(0.1)
                except:
                    "Card not found"

        cardnames = [self.id_data.get(c, "None") for c in card_id]
        return cardnames

    def tierlist(self, database, index=-1):
        self.update_lines()
        cards = self.cardlist(index)
        print(cards)
        df_nonan = database.df_processed.replace(np.nan, "", regex=True)
        safe_matches = [re.escape(m) for m in cards]
        df_sel = df_nonan[df_nonan["Name"].str.contains("|".join(safe_matches))]
        return df_sel.sort_values(["metric"], ascending=False).style.apply(
            highlight, names=["WP", "OH WR", "GIH WR", "metric", "metric_ih"]
        )


def get_pack2(picks):
    pack_cards = []
    for c_id in picks["PackCards"].split(","):
        try:
            time.sleep(0.05)
            card = scrython.cards.ArenaId(id=c_id)
            pack_cards.append(card.name())
        except:
            print("failed")
    return pack_cards


def get_lines():
    file_name = FOLDER + "Player.log"

    search1 = '"DraftPack":'
    search2 = "[UnityCrossThreadLogger]Draft.Notify"

    retval = []
    with open(file_name, "r") as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            if search1 in line:
                print(search1, "in line")
                substring = line[line.find("{") :]
                retval.append(get_pack(json.loads(substring)))

            if search2 in line:
                print(search2, "in line")
                substring = line[line.find("{") :]
                retval.append(get_pack2(json.loads(substring)))

    return retval


def get_first_line():
    file_name = FOLDER + "Player.log"
    search = '"DraftPack":'
    with open(file_name, "r") as read_obj:

        # Read all lines in the file one by one
        for line in read_obj:
            if search in line:
                substring = line[line.find("{") :]
                return json.loads(substring)


def get_last_line():
    file_name = FOLDER + "Player.log"
    search = '"DraftPack":'
    with open(file_name, "r") as read_obj:

        # Read all lines in the file one by one
        for line in read_obj:
            if search in line:
                substring = line[line.find("{") :]

    return json.loads(substring)


def get_last_line2():
    file_name = FOLDER + "Player.log"
    search = "[UnityCrossThreadLogger]Draft.Notify"
    with open(file_name, "r") as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            if search in line:
                substring = line[line.find("{") :]

    return json.loads(substring)


def get_pack2(picks):
    pack_cards = []
    for c_id in picks["PackCards"].split(","):
        try:
            time.sleep(0.05)
            card = scrython.cards.ArenaId(id=c_id)
            pack_cards.append(card.name())
        except:
            print("failed")
    return pack_cards


def get_pack(picks):
    print(picks)
    pack_cards = []
    for c_id in picks["payload"]["DraftPack"]:
        time.sleep(0.05)
        card = scrython.cards.ArenaId(id=c_id)
        pack_cards.append(card.name())
    return pack_cards


def sorted_cards(database, cards):
    df_nonan = database.df_processed.replace(np.nan, "", regex=True)
    df_sel = df_nonan[df_nonan["Name"].str.contains("|".join(cards))]
    return df_sel.sort_values(["WP"], ascending=False)


def deckdf(deck, data):
    import re

    df = data.df_processed

    rows = []
    p = re.compile(r"([0-9]) ([^\(]*) \(([\w]*)\) ([\d]*)$")
    for line in deck.split("\n"):
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
    df_deck = df_deck.sort_values("WP", ascending=False)
    return df_deck


def updateid():
    mtgaid_to_name = dict()
    for page in trange(1, 30):
        time.sleep(0.1)
        try:
            data = scrython.cards.Search(q="game:arena", page=page)
            for card in data.data():
                if card.get("arena_id", -1) > 0:
                    mtgaid_to_name[card.get("arena_id", -1)] = card["name"]
                else:
                    print(f'{card["name"]} failed')
        except:
            print(f"Page {page} not found")
            break

    with open("data/mtgaid_to_name.txt", "w") as outfile:
        json.dump(mtgaid_to_name, outfile)


import itertools


def add_set(set):

    counter = 0
    with open("data/mtgaid_to_name.txt") as f:
        mtgaid_to_name = json.load(f)

    for page in tqdm(itertools.count(1, 1)):
        time.sleep(0.1)
        try:
            data = scrython.cards.Search(q=f"set:{set}", page=page)
            for card in data.data():
                if card.get("arena_id", -1) > 0:
                    mtgaid_to_name[card.get("arena_id", -1)] = card["name"]
                    counter += 1
                else:
                    print(f'{card["name"]} failed')
                    print(card)
        except:
            break
    print(f"{set}: {counter} cadrs added.")
    with open("data/mtgaid_to_name.txt", "w") as outfile:
        json.dump(mtgaid_to_name, outfile)
