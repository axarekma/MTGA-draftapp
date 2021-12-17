## MTGA-draftapp

- change LOG_PATH in app/configure.py to the path to the MTGA logfile
- run flask app

```
set FLASK_APP=hello
flask run
```

### Features
#### Page: Pick data
- Select set and format and "Submit Format" to load the datatables (if not cached in /data, this will take some time)
- Select primary color(s) to filter color data and "Submit Colors" . If over 2 colors are checked colors defaults to None
- The pick will default to the current (latest in log). To check previous picks, use dropdown and select Submit Pick

#### Page: Deck
- An empty deck will default to the whole data table.
- Paste the string from MTGA export to use your pool.
- Select primary color(s) to filter color data and "Submit Colors" . If over 2 colors are checked colors defaults to None





