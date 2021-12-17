from flask import Flask, render_template, request, jsonify, session
from flask_bootstrap import Bootstrap
import pandas as pd
import numpy as np
import json
import os
from werkzeug.datastructures import MultiDict
from wtforms import BooleanField

from app import app
from app.forms import FormatForm, DeckForm, PickForm, DecklistForm
from app.draftdata import SetData
from app.utils import Tracker
import pandas as pd

draft = SetData(code="VOW", draftmode="PremierDraft")
tracker = Tracker(app.config["LOG_PATH"])
tracker.update_lines()


def session_color():
    if "deck_args" not in session:
        return None
    col = ""
    if session["deck_args"]["node_w"]:
        col = col + "W"
    if session["deck_args"]["node_u"]:
        col = col + "U"
    if session["deck_args"]["node_b"]:
        col = col + "B"
    if session["deck_args"]["node_r"]:
        col = col + "R"
    if session["deck_args"]["node_g"]:
        col = col + "G"
    print("col = ", col)
    if len(col) > 2:
        print("Too many colors. Showing all")
        return None
    return col


def cardlist():
    if "pick_args" not in session:
        pick = -1
    else:
        pick = session["pick_args"]["pick"]
    tracker.update_lines()
    return tracker.cardlist(pick)


@app.route("/deck.html", methods=["GET", "POST"])
def decklist():
    if not draft.loaded:
        draft.load_data()
    decklist = DecklistForm()
    deckform = DeckForm()

    if deckform.submitdeck.data and deckform.validate():
        print("submit deckform")
        session["deck_args"] = deckform.data
        session["deck_args"].pop("csrf_token")
        session["deck_args"].pop("submitdeck")

    if decklist.submitlist.data and decklist.validate():
        session["decklist"] = decklist.data["decklist"]

    if "decklist" in session and len(session["decklist"].strip()):
        x = draft.draft_deck(session["decklist"], session_color())
    else:
        x = draft.all_frame(col=session_color())

    if "deck_args" in session:
        deckform.node_w.checked = session["deck_args"]["node_w"]
        deckform.node_u.checked = session["deck_args"]["node_u"]
        deckform.node_b.checked = session["deck_args"]["node_b"]
        deckform.node_r.checked = session["deck_args"]["node_r"]
        deckform.node_g.checked = session["deck_args"]["node_g"]

    return render_template(
        "deck.html",
        data=x.to_html(table_id="example"),
        deckform=deckform,
        decklist=decklist,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    formatform = FormatForm()
    deckform = DeckForm()
    pickform = PickForm()

    if formatform.submitformat.data and formatform.validate():
        print("submit formatform")
        session["format_args"] = formatform.data
        session["format_args"].pop("csrf_token")
        session["format_args"].pop("submitformat")

    if deckform.submitdeck.data and deckform.validate():
        print("submit deckform")
        session["deck_args"] = deckform.data
        session["deck_args"].pop("csrf_token")
        session["deck_args"].pop("submitdeck")

    if pickform.submitpick.data and pickform.validate():
        print("submit pickform")
        session["pick_args"] = pickform.data
        session["pick_args"].pop("csrf_token")
        session["pick_args"].pop("submitpick")

    formatform = (
        FormatForm(MultiDict(session["format_args"]))
        if "format_args" in session
        else FormatForm()
    )
    pickform = (
        PickForm(MultiDict(session["pick_args"]))
        if "pick_args" in session
        else PickForm()
    )

    if "deck_args" in session:
        deckform.node_w.checked = session["deck_args"]["node_w"]
        deckform.node_u.checked = session["deck_args"]["node_u"]
        deckform.node_b.checked = session["deck_args"]["node_b"]
        deckform.node_r.checked = session["deck_args"]["node_r"]
        deckform.node_g.checked = session["deck_args"]["node_g"]

    if "format_args" in session:
        if draft.set != session["format_args"]["setfield"]:
            draft.set = session["format_args"]["setfield"]
            draft.loaded = False
        if draft.draftmode != session["format_args"]["formatfield"]:
            draft.draftmode = session["format_args"]["formatfield"]
            draft.loaded = False

    if not draft.loaded:
        draft.load_data()

    cards = cardlist()
    if cards:
        x = draft.draft_frame(cards, col=session_color()).render(table_id="example")
    else:
        x = pd.DataFrame(columns=["Log File is Empty!"]).to_html()
    return render_template(
        "index.html",
        data=x,
        formatform=formatform,
        deckform=deckform,
        pickform=pickform,
    )


if __name__ == "__main__":
    app.run(debug=True)
