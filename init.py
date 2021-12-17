from app.draftdata import SetData

if __name__ == "__main__":
    draft = SetData(code="VOW", draftmode="PremierDraft")
    draft.update_data()
