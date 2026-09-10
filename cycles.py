"""Discover complete local exports, keeping the newest revision of each cycle."""
import json
from pathlib import Path

def available_cycles(root):
    latest = {}
    for path in Path(root).glob('cycle-*/metadata.json'):
        if not (path.parent / 'gcw_points.csv').is_file() or not (path.parent / 'crisis.csv').is_file():
            continue
        meta = json.loads(path.read_text())
        key = meta['start']
        rank = (meta['mode'] == 'completed', meta['generated_at'])
        if key not in latest or rank > latest[key][0]:
            latest[key] = (rank, dict(meta, directory=path.parent.name))
    return [latest[key][1] for key in sorted(latest, reverse=True)]

def cycle_label(meta):
    start = meta['start'][:10]
    if meta['mode'] == 'current':
        return f'{start} onward · In progress'
    return f"{start} – {meta['end_exclusive'][:10]} · Completed"
