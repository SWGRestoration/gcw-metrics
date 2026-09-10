# GCW Observatory

A public dashboard for GCW scoring across three periods.
Overview, Scoring, Planets and Records views support faction and date filters
and downloads of selected records. Empty cycles are hidden.
A separate **Latest Shatterpoint** view shows the latest event's recorded Crisis
movement using its own event dates. Older event mechanics are not compared.

## Run

Python 3.12 recommended:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The repository includes prepared datasets under `data/published/`. No credentials
or access to game infrastructure are needed. Three populated scoring periods are available from the cycle selector.
`GCW_DATA_DIR` can point to another prepared archive. The public bundle is used by default.

## Reading the metrics

- GCW points are recorded adjustments, including deductions. They do not
  reconstruct final planetary control scores or personal character rewards.
- A scoring record is not necessarily a unique activity. Source IDs may represent
  game objects as well as characters; they are not verified player counts.
- Historical multiplier fields can be missing. Summaries exclude missing values
  and weight each recorded adjustment equally.
- Crisis requested/applied movement are magnitudes. Signed movement favors Imperial
  when positive and Rebel when negative. Totals alone do not establish the winner.
- Each cycle shows coverage limitations and its last observed scoring time.
  Complete cycle dates do not prove complete underlying data coverage.

## Dataset layout

Each `cycle-*` directory contains `gcw_points.csv`, `metadata.json`, and a reserved
`crisis.csv`. The selector uses metadata to choose the latest revision per cycle.
Historical event details are not displayed. `latest_event.json` supplies the
independent latest-event view. Only prepared, name-free metrics belong in this repo.

## Test

```sh
python -m unittest -v test_app
```
