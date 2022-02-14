from app.draftdata import SetData, DraftData
from app.utils import add_set

# Use this to update the 17lands datatables
if __name__ == "__main__":
    # add set from scryfall
    add_set("NEO")

    # update all data
    # draft = SetData(code="NEO", draftmode="PremierDraft")
    # draft.update_data()

    # update specific colorpair
    # col = "WU"
    # draft.coldata[col] = DraftData(draft.set, draft.draftmode, deck_color=col)
    # draft.coldata[col].load()
