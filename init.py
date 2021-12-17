from app.draftdata import SetData

# Use this to update the 17lands datatables
if __name__ == "__main__":
    draft = SetData(code="VOW", draftmode="PremierDraft")
    draft.update_data()
