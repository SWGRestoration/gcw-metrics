# GCW Observatory

A public dashboard for Galactic Civil War scoring.

- **GCW cycles:** points by faction, scoring type, planet and region for each cycle,
  with filters and downloads of selected records.
- **Shatterpoints:** Crisis control movement for each event, using the event's own
  dates and scoring scale.

## Run

Python 3.12:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The data ships with the repository, so no credentials or game access are needed.
Set `GCW_DATA_DIR` to read a different copy of `data/published/`.

## Data

- `data/published/cycle-<start>/` holds one cycle: `gcw_points.csv` and
  `metadata.json` (dates, row count, coverage notes, checksum).
- `data/published/events/event-<id>.json` holds one Shatterpoint's results.
- `data/gcw_points.csv` is the original February–March 2026 sample.

Completed cycles and ended events are final. Only name-free metrics belong here.

## Reading the metrics

- GCW points are recorded adjustments, including deductions. They don't reconstruct
  final planetary control or personal rewards.
- A scoring record is not necessarily a unique activity. Source IDs can be game
  objects as well as characters, so they are not player counts.
- Older records can lack multiplier fields; summaries exclude missing values.
- Crisis requested and applied movement are magnitudes. Net movement favors Imperial
  when positive and Rebel when negative. Totals alone don't establish a winner.
- Each cycle shows its coverage notes and last scoring time. Cycle dates alone don't
  prove complete coverage.

## Test

```sh
python -m unittest -v test_app
```
