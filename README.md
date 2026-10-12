# Postseason Hitter Model

Scores MLB hitters on the skills that hold up against October pitching: contact, bat speed and damage, swing decisions, velocity and two-strike whiff, baserunning, and defense.

## Run it (recommended)

Requires Python 3.8+ (no packages to install).

```
python3 serve.py
```

Your browser opens to http://localhost:8765. On load the page pulls:

- **MLB Stats API**: plate appearances, K%, BB%, ISO, SB success, baserunning runs, wRC+, handedness, positions
- **Baseball Savant leaderboards**: custom leaderboard (whiff, chase, zone swing, zone contact, barrel, hard-hit, xwOBA, sprint speed), bat tracking, sprint speed, outs above average

Click **Refresh live data** any time. Responses are cached for 10 minutes. Windows: `py serve.py`.

Options: `--port 9000`, `--no-browser`.

## Without the helper

Double-click `hitter-model.html`. The MLB Stats API may load directly; Savant does not allow browser pages to read it, so use the export links in the left rail and drop the CSVs onto the page.

## Pitch-level data (velocity and two-strike)

Whiff rate vs 95+ mph and two-strike whiff rate need pitch-by-pitch data, which is too large to pull automatically. Export from Statcast Search (https://baseballsavant.mlb.com/statcast_search), one team or date range per file (Savant caps exports at 25,000 pitches), and drop the CSVs onto the page. They merge with everything else by MLBAM player id.

## Notes

- Imported data and your weights/filters are saved in the browser's local storage for that address. `localhost:8765` and the double-clicked file are different addresses, so they keep separate saved data.
- Scores are percentiles within the pool of hitters at or above the PA minimum. Coverage shows how much of the weighted model has data behind each hitter.
- If Savant renames a column or changes an export URL, a source shows "failed" in the data bar. Download that export manually from the Savant page and drop it in; columns are matched by aliases.
- The helper only relays requests to statsapi.mlb.com and baseballsavant.mlb.com and only listens on 127.0.0.1.
