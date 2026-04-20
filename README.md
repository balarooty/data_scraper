# ⚽ FlashScore Football Results Scraper

Scrapes recent match results for any football team from [flashscore.in](https://www.flashscore.in/football/) using Playwright browser automation.

## Setup

```bash
pip3 install playwright --break-system-packages
python3 -m playwright install chromium
```

## Usage

### Search by Team Name
```bash
python3 flashscore_scraper.py "Manchester United"
python3 flashscore_scraper.py "Arsenal" --limit 10
python3 flashscore_scraper.py "Real Madrid" --show-more 3
```

### Direct URL Mode (faster, no search needed)
```bash
python3 flashscore_scraper.py --slug manchester-united --id ppjDR086 --name "Manchester Utd"
python3 flashscore_scraper.py --slug arsenal --id WRYMhbL1 --name "Arsenal"
```

### Output Formats
```bash
# Terminal table (default)
python3 flashscore_scraper.py "Liverpool"

# JSON output
python3 flashscore_scraper.py "Liverpool" --output json

# Save to file
python3 flashscore_scraper.py "Liverpool" --output json --save results/liverpool.json
python3 flashscore_scraper.py "Liverpool" --output csv --save results/liverpool.csv
```

### Options
| Flag | Description |
|------|-------------|
| `--limit N` | Show only N most recent results |
| `--show-more N` | Click "Show more" N times for older results |
| `--output table\|json\|csv` | Output format |
| `--save PATH` | Save results to file |
| `--no-headless` | Show the browser window |
| `--slug` + `--id` | Use direct team URL (bypass search) |

## Team Lookup

List all pre-mapped teams:
```bash
python3 team_config.py
```

Search for a specific team:
```bash
python3 team_config.py "Arsenal"
```

## Output Fields

Each match result contains:
- `datetime` – Match date & time
- `league` – Competition name
- `home_team` / `away_team` – Team names
- `home_score` / `away_score` – Individual scores
- `score` – Combined score (e.g. "2-1")
- `total_goals` – Sum of goals
- `result` – W/D/L relative to the searched team
- `venue` – Home/Away

## Examples

```
================================================================================
  ⚽ Manchester Utd  |  England  |  15 results
================================================================================
  Date            League                    Home               Score   Away               Result
  19.04. 00:30    ENGLAND: EPL              Chelsea            1-0     Manchester Utd      ❌ L
  14.04. 00:30    ENGLAND: EPL              Manchester Utd     1-0     Leicester City      ✅ W
  ...

  📈 Form: 8W 3D 4L  |  Avg Goals: 2.3 per match
================================================================================
```

## Project Structure

```
data_scraper/
├── flashscore_scraper.py   # Main scraper tool
├── team_config.py          # Team name → FlashScore URL mappings
├── results/                # Saved results (auto-created)
└── README.md
```
# data_scraper
