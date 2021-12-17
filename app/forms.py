from flask_wtf import FlaskForm
from itertools import combinations
from wtforms import SelectField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, DataRequired
from wtforms import widgets


class FormatForm(FlaskForm):
    sets = ["VOW", "MID", "AFR", "STX", "KHM"]
    setfield = SelectField("Set", [DataRequired()], choices=[(s, s) for s in sets])
    formatfield = SelectField(
        "Format",
        [DataRequired()],
        choices=[
            ("PremierDraft", "PremierDraft"),
            ("TradDraft", "TradDraft"),
            ("QuickDraft", "QuickDraft"),
        ],
    )

    submitformat = SubmitField("Submit Format")


class DeckForm(FlaskForm):
    node_w = BooleanField("W")
    node_u = BooleanField("U")
    node_b = BooleanField("B")
    node_r = BooleanField("R")
    node_g = BooleanField("G")
    submitdeck = SubmitField("Submit Colors")

    def set_with_session(self, session):
        if "deck_args" in session:
            self.node_w.checked = session["deck_args"]["node_w"]
            self.node_u.checked = session["deck_args"]["node_u"]
            self.node_b.checked = session["deck_args"]["node_b"]
            self.node_r.checked = session["deck_args"]["node_r"]
            self.node_g.checked = session["deck_args"]["node_g"]


class PickForm(FlaskForm):
    max_history = 8
    choises = [-i for i in range(1, max_history + 1)]
    names = [f"{-i}" for i in range(max_history)]
    names[0] = "current"

    pick = SelectField(
        "Block Size",
        [DataRequired()],
        coerce=int,
        choices=[(c, n) for c, n in zip(choises, names)],
    )
    submitpick = SubmitField("Submit Pick")


class DecklistForm(FlaskForm):
    decklist = TextAreaField()
    submitlist = SubmitField("Submit List")

