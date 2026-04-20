"""
Team Configuration & Mappings
==============================
Pre-mapped popular football teams with their FlashScore slugs and IDs.
This serves as a fallback when search doesn't work reliably.

To find a team's slug and ID:
  1. Go to https://www.flashscore.in/football/
  2. Search for the team
  3. The URL will be: /team/{slug}/{id}/
  
Usage:
  from team_config import TEAM_MAPPINGS, get_team, add_team
"""

# ─── Popular Team Mappings ────────────────────────────────────────────────────
# Format: "search_key": {"slug": "...", "id": "...", "name": "...", "country": "..."}

TEAM_MAPPINGS = {
    # ─── England - Premier League ─────────────────────────────────────────
    "manchester united": {
        "slug": "manchester-united",
        "id": "ppjDR086",
        "name": "Manchester Utd",
        "country": "England",
    },
    "manchester city": {
        "slug": "manchester-city",
        "id": "xtQgHdOF",
        "name": "Manchester City",
        "country": "England",
    },
    "arsenal": {
        "slug": "arsenal",
        "id": "hA1Zm19f",
        "name": "Arsenal",
        "country": "England",
    },
    "liverpool": {
        "slug": "liverpool",
        "id": "lId4TMwf",
        "name": "Liverpool",
        "country": "England",
    },
    "chelsea": {
        "slug": "chelsea",
        "id": "YBjK3xpT",
        "name": "Chelsea",
        "country": "England",
    },
    "tottenham": {
        "slug": "tottenham-hotspur",
        "id": "6rzbOkPM",
        "name": "Tottenham",
        "country": "England",
    },
    "aston villa": {
        "slug": "aston-villa",
        "id": "pDa3kSeD",
        "name": "Aston Villa",
        "country": "England",
    },
    "newcastle": {
        "slug": "newcastle-united",
        "id": "GSIH5Lhf",
        "name": "Newcastle Utd",
        "country": "England",
    },
    "west ham": {
        "slug": "west-ham-united",
        "id": "MKfpMt7E",
        "name": "West Ham",
        "country": "England",
    },
    "brighton": {
        "slug": "brighton-hove-albion",
        "id": "W079GGjU",
        "name": "Brighton",
        "country": "England",
    },
    "bournemouth": {
        "slug": "bournemouth",
        "id": "GKmiBRCf",
        "name": "Bournemouth",
        "country": "England",
    },
    "crystal palace": {
        "slug": "crystal-palace",
        "id": "AH1dOmbj",
        "name": "Crystal Palace",
        "country": "England",
    },
    "brentford": {
        "slug": "brentford",
        "id": "nFXl9lDG",
        "name": "Brentford",
        "country": "England",
    },
    "fulham": {
        "slug": "fulham",
        "id": "xADhRW1A",
        "name": "Fulham",
        "country": "England",
    },
    "wolverhampton": {
        "slug": "wolverhampton-wanderers",
        "id": "bcwfRuVQ",
        "name": "Wolverhampton",
        "country": "England",
    },
    "everton": {
        "slug": "everton",
        "id": "Q2GXWQK9",
        "name": "Everton",
        "country": "England",
    },
    "nottingham forest": {
        "slug": "nottingham-forest",
        "id": "Q2xpv9mA",
        "name": "Nottingham Forest",
        "country": "England",
    },
    "ipswich": {
        "slug": "ipswich-town",
        "id": "b5T3IZlp",
        "name": "Ipswich Town",
        "country": "England",
    },
    "leicester": {
        "slug": "leicester-city",
        "id": "KSrjtVgj",
        "name": "Leicester City",
        "country": "England",
    },
    "southampton": {
        "slug": "southampton",
        "id": "zBLSHExN",
        "name": "Southampton",
        "country": "England",
    },

    # ─── Spain - La Liga ──────────────────────────────────────────────────
    "real madrid": {
        "slug": "real-madrid",
        "id": "W8mj7MDD",
        "name": "Real Madrid",
        "country": "Spain",
    },
    "barcelona": {
        "slug": "barcelona",
        "id": "SKbpVP5K",
        "name": "Barcelona",
        "country": "Spain",
    },
    "atletico madrid": {
        "slug": "atletico-madrid",
        "id": "th7eaGHq",
        "name": "Atletico Madrid",
        "country": "Spain",
    },
    "real sociedad": {
        "slug": "real-sociedad",
        "id": "S2bmr8jj",
        "name": "Real Sociedad",
        "country": "Spain",
    },
    "real betis": {
        "slug": "real-betis",
        "id": "6xQv0MLe",
        "name": "Real Betis",
        "country": "Spain",
    },
    "villarreal": {
        "slug": "villarreal",
        "id": "dWGIJeao",
        "name": "Villarreal",
        "country": "Spain",
    },
    "athletic bilbao": {
        "slug": "athletic-bilbao",
        "id": "8RPC0Y0h",
        "name": "Athletic Bilbao",
        "country": "Spain",
    },
    "sevilla": {
        "slug": "sevilla",
        "id": "2VGmJLqu",
        "name": "Sevilla",
        "country": "Spain",
    },

    # ─── Germany - Bundesliga ─────────────────────────────────────────────
    "bayern munich": {
        "slug": "bayern-munich",
        "id": "CKkk77Dj",
        "name": "Bayern Munich",
        "country": "Germany",
    },
    "borussia dortmund": {
        "slug": "borussia-dortmund",
        "id": "KfkBt0il",
        "name": "Borussia Dortmund",
        "country": "Germany",
    },
    "rb leipzig": {
        "slug": "rb-leipzig",
        "id": "tqhPhCrt",
        "name": "RB Leipzig",
        "country": "Germany",
    },
    "bayer leverkusen": {
        "slug": "bayer-leverkusen",
        "id": "SN4RlwUj",
        "name": "Bayer Leverkusen",
        "country": "Germany",
    },

    # ─── Italy - Serie A ──────────────────────────────────────────────────
    "inter milan": {
        "slug": "inter-milan",
        "id": "x4vJHjTp",
        "name": "Inter Milan",
        "country": "Italy",
    },
    "ac milan": {
        "slug": "ac-milan",
        "id": "xVflOWMl",
        "name": "AC Milan",
        "country": "Italy",
    },
    "juventus": {
        "slug": "juventus",
        "id": "IQ7eSPKg",
        "name": "Juventus",
        "country": "Italy",
    },
    "napoli": {
        "slug": "napoli",
        "id": "tELTiDHn",
        "name": "Napoli",
        "country": "Italy",
    },
    "roma": {
        "slug": "roma",
        "id": "tS105Cdf",
        "name": "Roma",
        "country": "Italy",
    },
    "lazio": {
        "slug": "lazio",
        "id": "SBSBbr3j",
        "name": "Lazio",
        "country": "Italy",
    },
    "atalanta": {
        "slug": "atalanta",
        "id": "bo2ONBHK",
        "name": "Atalanta",
        "country": "Italy",
    },

    # ─── France - Ligue 1 ─────────────────────────────────────────────────
    "psg": {
        "slug": "paris-saint-germain",
        "id": "KcqlBpqI",
        "name": "Paris SG",
        "country": "France",
    },
    "paris saint germain": {
        "slug": "paris-saint-germain",
        "id": "KcqlBpqI",
        "name": "Paris SG",
        "country": "France",
    },
    "marseille": {
        "slug": "marseille",
        "id": "dHaJv6R5",
        "name": "Marseille",
        "country": "France",
    },
    "lyon": {
        "slug": "lyon",
        "id": "CrDBmK3d",
        "name": "Lyon",
        "country": "France",
    },
    "monaco": {
        "slug": "monaco",
        "id": "OiauQZWr",
        "name": "Monaco",
        "country": "France",
    },

    # ─── India ─────────────────────────────────────────────────────────────
    "mohun bagan": {
        "slug": "mohun-bagan-sg",
        "id": "WfXKBN7l",
        "name": "Mohun Bagan SG",
        "country": "India",
    },
    "east bengal": {
        "slug": "east-bengal",
        "id": "bj3kNrTC",
        "name": "East Bengal",
        "country": "India",
    },
    "kerala blasters": {
        "slug": "kerala-blasters",
        "id": "UDm7fGCj",
        "name": "Kerala Blasters",
        "country": "India",
    },
    "mumbai city": {
        "slug": "mumbai-city",
        "id": "hihKbB0N",
        "name": "Mumbai City",
        "country": "India",
    },
    "bengaluru fc": {
        "slug": "bengaluru",
        "id": "UfK6sRAr",
        "name": "Bengaluru FC",
        "country": "India",
    },

    # ─── Portugal ──────────────────────────────────────────────────────────
    "benfica": {
        "slug": "benfica",
        "id": "4DQGW6T6",
        "name": "Benfica",
        "country": "Portugal",
    },
    "porto": {
        "slug": "porto",
        "id": "WN2FYRMQ",
        "name": "Porto",
        "country": "Portugal",
    },
    "sporting cp": {
        "slug": "sporting-cp",
        "id": "tYUwIjKD",
        "name": "Sporting CP",
        "country": "Portugal",
    },

    # ─── Netherlands ──────────────────────────────────────────────────────
    "ajax": {
        "slug": "ajax",
        "id": "vpJ8Ckm6",
        "name": "Ajax",
        "country": "Netherlands",
    },
    "psv": {
        "slug": "psv-eindhoven",
        "id": "ElBcjei4",
        "name": "PSV",
        "country": "Netherlands",
    },
    "feyenoord": {
        "slug": "feyenoord",
        "id": "baMY7p40",
        "name": "Feyenoord",
        "country": "Netherlands",
    },
}


# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_team(name: str) -> dict | None:
    """Look up a team by name (case-insensitive)."""
    key = name.lower().strip()
    return TEAM_MAPPINGS.get(key)


def add_team(search_key: str, slug: str, team_id: str, name: str, country: str = ""):
    """Add a new team mapping at runtime."""
    TEAM_MAPPINGS[search_key.lower().strip()] = {
        "slug": slug,
        "id": team_id,
        "name": name,
        "country": country,
    }


def list_teams(country: str = None) -> list[dict]:
    """List all mapped teams, optionally filtered by country."""
    teams = []
    for key, info in sorted(TEAM_MAPPINGS.items()):
        if country and info.get("country", "").lower() != country.lower():
            continue
        teams.append({"search_key": key, **info})
    return teams


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        team = get_team(query)
        if team:
            print(f"✅ {team['name']} ({team['country']})")
            print(f"   URL: https://www.flashscore.in/team/{team['slug']}/{team['id']}/")
        else:
            print(f"❌ '{query}' not found. Available teams:")
            for t in list_teams():
                print(f"   • {t['search_key']:25s} → {t['name']} ({t['country']})")
    else:
        print("Available teams:")
        for t in list_teams():
            print(f"  • {t['search_key']:25s} → {t['name']} ({t['country']})")
