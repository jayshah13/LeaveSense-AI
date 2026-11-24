# LeaveSense-AI

Type a leave request the way you'd actually say it, and LeaveSense-AI pulls out the three things an HR system really needs: the **leave type**, the **start date** and the **end date**.

> "I want to apply sick leave from 5th December 2026 to 8th December 2026 due to fever"

```json
{
    "Leave Type": "sick leave",
    "Start Date": "05/12/2026",
    "End Date": "08/12/2026"
}
```

No dropdowns and no date pickers, just a sentence.

## Why this exists

Filling in leave forms is boring, and reading free-text leave emails is worse. I wanted to see if a small NER (named entity recognition) model could do the reading part so a person doesn't have to. It turned out to be doable with two lightweight spaCy models and a bit of plain Python for the tricky bits like "today" and "tomorrow".

## How it works

Every request goes through two separate spaCy NER models:

1. **Leave type model** spots the kind of leave: `CASUAL`, `SICK`, `EARNED` or `HALF DAY`.
2. **Date model** spots the `START DATE` and `END DATE`.

Before the models see the text, a small preprocessing step converts dates written like `14th May 2024` or `May 16th 2024` into `14/05/2024`, so the model only has to deal with one format.

A few rules sit on top of the models:

- If the sentence says **"today"** or **"tomorrow"**, the dates are worked out from the current date. A number in the sentence is treated as a number of days.
- If **no dates** (or only one) are found, start and end come back as `null`.
- If a date is **in the past**, or the end date is **before** the start date, both come back as `null` rather than guessing.
- If no leave type is found, the API returns a `400` error.

All dates use the `DD/MM/YYYY` format.

## What's in the repo

```
LeaveSense-AI/
├── leave_app.py                 # Flask API (the main file)
├── leave_application.ipynb      # Notebook used to train the models
├── requirements.txt
├── model-best-leavetype/        # Trained leave type model (used by the app)
├── model-best-dates/            # Trained date model (used by the app)
├── model-last-leavetypes/       # Last training checkpoint
├── model-last-dates/            # Last training checkpoint
├── Dataset_Dates/
│   ├── leave dates.txt          # Raw example sentences
│   └── annotations.json         # Labelled dates (made with NER Annotator)
```

## Getting started

You'll need Python 3.9 or newer.

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/LeaveSense-AI.git
cd LeaveSense-AI

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the API
python leave_app.py
```

By default the app starts on `10.170.80.113:8039`, which was the original development machine. To run it on your own computer, change the last line of `leave_app.py` to:

```python
app.run(host="127.0.0.1", port=8039, debug=True)
```

> The trained models were built with spaCy 3.7.x, so stick with that version (the `requirements.txt` already does).

## Try it

Send a POST request to `/predict_leave` with your sentence in `leave_query`:

```bash
curl -X POST http://127.0.0.1:8039/predict_leave \
  -H "Content-Type: application/json" \
  -d '{"leave_query": "need casual leave tomorrow due to a family function"}'
```

More examples of what it understands:

| You type | Leave type | Dates |
|---|---|---|
| `half day leave tomorrow for urgent work` | half day | tomorrow, tomorrow |
| `I want earned leave` | earned leave | `null`, `null` (no dates given) |
| `sick leave from 5th December 2026 to 8th December 2026` | sick leave | 05/12/2026, 08/12/2026 |

## Training your own models

Both models were trained the same way:

1. Collect example sentences in a text file.
2. Label them with [NER Annotator](https://tecoholic.github.io/ner-annotator/) and export the JSON.
3. Run `leave_application.ipynb` to convert the labels into spaCy's training format and train.
4. Copy the `model-best` folder into the project and point `leave_app.py` at it.

Step-by-step notes are in the two PDFs in the repo.

## Known limitations

- The web page is not included yet. The `/` route expects a `templates/index.html`, but the API at `/predict_leave` works without it.
- Both models report a perfect score on their own training data, which mostly means the dataset is small. Expect surprises on phrasing the models haven't seen.
- Only English, and only the `DD/MM/YYYY` style.
- Only four leave types are supported for now.

## Ideas for next time

- [ ] Add the frontend (`templates/index.html`)
- [ ] Support more leave types (maternity, unpaid, comp-off)
- [ ] Understand phrases like "next Monday" or "for the next 3 days"
- [ ] Train on a bigger and more varied dataset
- [ ] Add tests

## Built with

- Python
- [spaCy](https://spacy.io/) for the NER models
- [Flask](https://flask.palletsprojects.com/) for the API

## License

Add a license before publishing (MIT is a common choice for projects like this) and mention it here.
