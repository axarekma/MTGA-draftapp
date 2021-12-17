from app.draftdata import SetData, DraftData

# Use this to update the 17lands datatables
if __name__ == "__main__":
    print("kakka")
    draft = SetData(code="KHM", draftmode="QuickDraft")
    # draft.load_data()
    col = "WU"
    draft.coldata[col] = DraftData(draft.set, draft.draftmode, deck_color=col)
    draft.coldata[col].load()

