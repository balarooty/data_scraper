#!/usr/bin/env python3
"""
FlashScore Football Results Scraper
====================================
Scrapes recent match results for a specific football team from flashscore.in.

Usage:
    python3 flashscore_scraper.py "Manchester United"
    python3 flashscore_scraper.py "Arsenal" --limit 20
    python3 flashscore_scraper.py "Real Madrid" --output csv
    python3 flashscore_scraper.py "Liverpool" --output json --save results/liverpool.json
    python3 flashscore_scraper.py "Barcelona" --show-more 3

Dependencies:
    pip3 install playwright
    python3 -m playwright install chromium
"""

import argparse
import asyncio
import json
import csv
import sys
import os
import re
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Playwright not installed. Run:")
    print("   pip3 install playwright")
    print("   python3 -m playwright install chromium")
    sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────────────

BASE_URL = "https://www.flashscore.in"
FOOTBALL_URL = f"{BASE_URL}/football/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Timeouts (ms)
PAGE_TIMEOUT = 30000
SEARCH_TIMEOUT = 10000
NAV_TIMEOUT = 15000
ELEMENT_TIMEOUT = 8000


# ─── Scraper Class ────────────────────────────────────────────────────────────

class FlashScoreScraper:
    """Scrapes recent football match results from FlashScore.in."""

    def __init__(self, headless=True, slow_mo=0):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        """Launch browser and create page context."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )
        self.context = await self.browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1440, "height": 900},
            locale="en-IN",
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(PAGE_TIMEOUT)

    async def close(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def search_team(self, team_name: str) -> dict | None:
        """
        Search for a team on FlashScore and return the team info + URL.
        Returns dict with keys: name, country, url, slug, team_id
        """
        print(f"🔍 Searching for '{team_name}'...")

        # Navigate to FlashScore football page
        await self.page.goto(FOOTBALL_URL, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(2000)

        # Handle cookie consent if present
        try:
            consent_btn = self.page.locator("#onetrust-accept-btn-handler")
            if await consent_btn.is_visible(timeout=3000):
                await consent_btn.click()
                await self.page.wait_for_timeout(500)
        except Exception:
            pass

        # Click on the search icon
        search_icon = self.page.locator('button.searchIcon, .header__logo + div button, [class*="searchIcon"], a[class*="search"], button[aria-label*="search"], .header__button--search')
        
        # Try multiple selectors for search
        clicked = False
        for selector in [
            'button[class*="search"]',
            'div[class*="search"] button',
            '.header__button--search',
            'svg[class*="search"]',
            '#search-button',
            'a[href*="search"]',
        ]:
            try:
                el = self.page.locator(selector).first
                if await el.is_visible(timeout=2000):
                    await el.click()
                    clicked = True
                    break
            except Exception:
                continue

        # If standard selectors failed, try clicking the magnifying glass area
        if not clicked:
            try:
                # The search icon is typically in the top-right header area
                header = self.page.locator('header, .header, #header, [class*="header"]').first
                search_area = header.locator('[class*="search"], [class*="Search"], svg').first
                await search_area.click()
                clicked = True
            except Exception:
                pass

        if not clicked:
            # Last resort: try keyboard shortcut or direct navigation
            try:
                await self.page.keyboard.press("Control+f")
                await self.page.wait_for_timeout(500)
            except Exception:
                print("⚠️  Could not find search button, trying direct URL approach...")
                return await self._search_via_url(team_name)

        await self.page.wait_for_timeout(1000)

        # Type team name in search input
        search_input = self.page.locator('input[type="text"], input[type="search"], input[placeholder*="search" i], input[class*="search" i]').first
        try:
            await search_input.wait_for(state="visible", timeout=SEARCH_TIMEOUT)
            await search_input.fill("")
            await search_input.type(team_name, delay=80)
        except Exception:
            print("⚠️  Search input not found, trying direct URL approach...")
            return await self._search_via_url(team_name)

        await self.page.wait_for_timeout(2000)

        # Find the first SOCCER result matching the team name
        result = await self._pick_search_result(team_name)
        return result

    async def _pick_search_result(self, team_name: str) -> dict | None:
        """Pick the best match from search results (prefer SOCCER category)."""
        # Look for search result items
        results_selectors = [
            '[class*="searchResult"]',
            '[class*="search-result"]',
            '[class*="SearchResult"]',
            'div[class*="participant"]',
            'a[class*="participant"]',
        ]

        for selector in results_selectors:
            items = self.page.locator(selector)
            count = await items.count()
            if count > 0:
                # Find the first soccer/football result
                for i in range(min(count, 10)):
                    item = items.nth(i)
                    text = await item.inner_text()
                    text_lower = text.lower()

                    # Check if it's a soccer/football result and matches team name
                    is_soccer = "soccer" in text_lower or "football" in text_lower
                    name_match = team_name.lower() in text_lower

                    if name_match and is_soccer:
                        # Extract team info
                        lines = [l.strip() for l in text.split("\n") if l.strip()]
                        team_info = {
                            "name": lines[0] if lines else team_name,
                            "country": "",
                            "url": "",
                        }
                        # Extract country from "SOCCER, COUNTRY" pattern
                        for line in lines:
                            if "soccer" in line.lower() or "football" in line.lower():
                                parts = line.split(",")
                                if len(parts) > 1:
                                    team_info["country"] = parts[-1].strip()

                        # Click on the result
                        await item.click()
                        await self.page.wait_for_timeout(2000)
                        await self.page.wait_for_load_state("domcontentloaded")

                        team_info["url"] = self.page.url
                        # Extract slug and ID from URL
                        url_match = re.search(r'/team/([^/]+)/([^/]+)', self.page.url)
                        if url_match:
                            team_info["slug"] = url_match.group(1)
                            team_info["team_id"] = url_match.group(2)

                        print(f"✅ Found: {team_info['name']} ({team_info.get('country', 'Unknown')})")
                        return team_info

        # Fallback: click the first result
        try:
            first_result = self.page.locator('[class*="searchResult"] a, [class*="search-result"] a, [class*="participant"]').first
            await first_result.click()
            await self.page.wait_for_timeout(2000)
            await self.page.wait_for_load_state("domcontentloaded")

            url = self.page.url
            url_match = re.search(r'/team/([^/]+)/([^/]+)', url)
            if url_match:
                return {
                    "name": team_name,
                    "url": url,
                    "slug": url_match.group(1),
                    "team_id": url_match.group(2),
                    "country": "",
                }
        except Exception:
            pass

        return await self._search_via_url(team_name)

    async def _search_via_url(self, team_name: str) -> dict | None:
        """Fallback: construct team URL from common team mappings."""
        from team_config import TEAM_MAPPINGS

        key = team_name.lower().strip()
        if key in TEAM_MAPPINGS:
            mapping = TEAM_MAPPINGS[key]
            url = f"{BASE_URL}/team/{mapping['slug']}/{mapping['id']}/"
            return {
                "name": mapping.get("name", team_name),
                "url": url,
                "slug": mapping["slug"],
                "team_id": mapping["id"],
                "country": mapping.get("country", ""),
            }

        print(f"❌ Could not find team '{team_name}'. Try using the exact FlashScore name.")
        return None

    async def get_results(self, team_info: dict, show_more_clicks: int = 0) -> list[dict]:
        """
        Navigate to team results page and scrape match data.
        
        Args:
            team_info: Dict from search_team() with url/slug/team_id
            show_more_clicks: Number of times to click "Show more" for older results
            
        Returns:
            List of match result dicts
        """
        results_url = team_info["url"]
        if not results_url.endswith("/results/"):
            # Ensure we're on the results tab
            if results_url.endswith("/"):
                results_url += "results/"
            else:
                results_url += "/results/"

        print(f"📊 Loading results from: {results_url}")
        await self.page.goto(results_url, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(3000)

        # Click "Show more results" button if requested
        for i in range(show_more_clicks):
            try:
                show_more = self.page.locator('a[class*="showMore"], a[class*="show-more"], [class*="event__more"], a.event__more--static')
                if await show_more.is_visible(timeout=3000):
                    await show_more.click()
                    print(f"   📄 Loading more results ({i+1}/{show_more_clicks})...")
                    await self.page.wait_for_timeout(2000)
                else:
                    print(f"   ⚠️  No more results to load after {i} clicks")
                    break
            except Exception:
                break

        # Scrape the results
        matches = await self._extract_results(team_info.get("name", ""))
        print(f"📋 Scraped {len(matches)} match results")
        return matches

    async def _extract_results(self, team_name: str) -> list[dict]:
        """Extract match results from the current page."""
        matches = []
        current_league = ""

        # Strategy: Read all event rows from the page
        # FlashScore uses div-based rows with classes like event__match
        
        # First, try to get league headers and match rows
        # The page structure groups results under league headers
        
        content = await self.page.content()
        
        # Use page.evaluate for more reliable extraction
        data = await self.page.evaluate("""
        () => {
            const results = [];
            let currentLeague = '';
            
            // FlashScore uses these specific classes:
            // - headerLeague__wrapper = league/competition header row
            // - headerLeague__category-text = country name (e.g. "ENGLAND")
            // - headerLeague__title = league name (e.g. "EPL")
            // - event__match = individual match row
            
            // Get the main container
            const container = document.querySelector('.sportName.soccer')
                || document.querySelector('[class*="sportName"]')
                || document.querySelector('#teamPage')
                || document.body;
            
            // Walk ALL children in document order to capture headers before their matches
            const allElements = container.querySelectorAll(
                '[class*="headerLeague__wrapper"], [class*="event__match"], [class*="event__round"]'
            );
            
            for (const el of allElements) {
                const className = el.className || '';
                
                // ── League/competition header ──
                if (className.includes('headerLeague__wrapper') || className.includes('headerLeague')) {
                    let country = '';
                    let league = '';
                    
                    // Get country: "ENGLAND", "EUROPE", "SPAIN" etc
                    const catEl = el.querySelector('[class*="headerLeague__category-text"]');
                    if (catEl) {
                        country = catEl.textContent.trim();
                    }
                    
                    // Get league name: "EPL", "Champions League", "La Liga" etc
                    const titleEl = el.querySelector('a[class*="headerLeague__title"], span[class*="headerLeague__title"]');
                    if (titleEl) {
                        league = titleEl.textContent.trim();
                    }
                    
                    if (country || league) {
                        currentLeague = country && league 
                            ? country + ': ' + league 
                            : (country || league);
                    }
                    continue;
                }
                
                // Skip round headers
                if (className.includes('event__round')) {
                    continue;
                }
                
                // ── Match row ──
                if (className.includes('event__match')) {
                    const match = {};
                    match.league = currentLeague;
                    
                    // Date and time - clean out extra markers
                    const timeEl = el.querySelector('[class*="event__time"]');
                    if (timeEl) {
                        let dt = timeEl.textContent.trim();
                        // Remove "Pen", "Agg", "FRO" etc suffixes
                        dt = dt.replace(/(Pen|Agg|FRO|AET|WO|AOT|Postp\.?|Canc\.?|Abd\.?)$/gi, '').trim();
                        match.datetime = dt;
                        // Capture any match status tag
                        const rawDt = timeEl.textContent.trim();
                        const statusMatch = rawDt.match(/(Pen|Agg|AET|WO|AOT)$/i);
                        if (statusMatch) {
                            match.match_status = statusMatch[1];
                        }
                    }
                    
                    // Home team - get only the team name text
                    const homeEl = el.querySelector('[class*="event__homeParticipant"], [class*="event__participant--home"]');
                    if (homeEl) {
                        const nameLink = homeEl.querySelector('a, span');
                        match.home_team = nameLink 
                            ? nameLink.textContent.trim() 
                            : homeEl.textContent.trim();
                        match.home_team = match.home_team
                            .replace(/Advancing/gi, '')
                            .replace(/\\s*\\([A-Za-z]{2,4}\\)\\s*/g, '')
                            .trim();
                    }
                    
                    // Away team
                    const awayEl = el.querySelector('[class*="event__awayParticipant"], [class*="event__participant--away"]');
                    if (awayEl) {
                        const nameLink = awayEl.querySelector('a, span');
                        match.away_team = nameLink
                            ? nameLink.textContent.trim()
                            : awayEl.textContent.trim();
                        match.away_team = match.away_team
                            .replace(/Advancing/gi, '')
                            .replace(/\\s*\\([A-Za-z]{2,4}\\)\\s*/g, '')
                            .trim();
                    }
                    
                    // Scores - extract just the numeric value
                    const homeScore = el.querySelector('[class*="event__score--home"]');
                    const awayScore = el.querySelector('[class*="event__score--away"]');
                    if (homeScore) {
                        match.home_score = homeScore.textContent.trim().replace(/[^0-9]/g, '');
                    }
                    if (awayScore) {
                        match.away_score = awayScore.textContent.trim().replace(/[^0-9]/g, '');
                    }
                    
                    // Match ID
                    const id = el.id || el.getAttribute('id') || '';
                    match.match_id = id.replace(/^g_\\d+_/, '');
                    
                    // Stage info
                    const stageEl = el.querySelector('[class*="event__stage"]');
                    if (stageEl) {
                        match.stage = stageEl.textContent.trim();
                    }
                    
                    if (match.home_team || match.away_team) {
                        results.push(match);
                    }
                }
            }
            
            return results;
        }
        """)

        # If the above didn't work well, try alternative approach
        if not data or len(data) == 0:
            data = await self._extract_results_fallback()

        # Post-process results
        for match in data:
            # Determine result for the target team
            home = match.get("home_team", "")
            away = match.get("away_team", "")
            h_score = match.get("home_score", "")
            a_score = match.get("away_score", "")

            try:
                hs = int(h_score)
                as_ = int(a_score)
                match["score"] = f"{hs}-{as_}"
                match["total_goals"] = hs + as_

                # Determine result relative to the searched team
                is_home = team_name.lower() in home.lower()
                if is_home:
                    if hs > as_:
                        match["result"] = "W"
                    elif hs < as_:
                        match["result"] = "L"
                    else:
                        match["result"] = "D"
                    match["venue"] = "Home"
                else:
                    if as_ > hs:
                        match["result"] = "W"
                    elif as_ < hs:
                        match["result"] = "L"
                    else:
                        match["result"] = "D"
                    match["venue"] = "Away"
            except (ValueError, TypeError):
                match["score"] = f"{h_score}-{a_score}"
                match["result"] = "?"
                match["venue"] = "?"

            matches.append(match)

        return matches

    async def _extract_results_fallback(self) -> list[dict]:
        """Fallback extraction using broader selectors."""
        return await self.page.evaluate("""
        () => {
            const results = [];
            let currentLeague = '';
            
            // Try broader approach - get all divs in the main content area
            const container = document.querySelector('[class*="sportName"], [id*="live-table"], .leagues, main, [class*="content"]');
            if (!container) return results;
            
            const divs = container.querySelectorAll('div');
            
            for (const div of divs) {
                const cls = div.className || '';
                const text = div.textContent || '';
                
                // Detect league headers
                if (cls.includes('header') && !cls.includes('match')) {
                    const nameEl = div.querySelector('[class*="name"], [class*="title"]');
                    if (nameEl) currentLeague = nameEl.textContent.trim();
                    continue;
                }
                
                // Detect match rows - they typically have participant names and scores
                if (cls.includes('match') || cls.includes('event')) {
                    const participants = div.querySelectorAll('[class*="participant"], [class*="team"]');
                    const scores = div.querySelectorAll('[class*="score"]');
                    const timeEl = div.querySelector('[class*="time"], [class*="date"]');
                    
                    if (participants.length >= 2 && scores.length >= 2) {
                        results.push({
                            league: currentLeague,
                            home_team: participants[0].textContent.trim(),
                            away_team: participants[1].textContent.trim(),
                            home_score: scores[0].textContent.trim(),
                            away_score: scores[1].textContent.trim(),
                            datetime: timeEl ? timeEl.textContent.trim() : '',
                            match_id: div.id || '',
                        });
                    }
                }
            }
            
            return results;
        }
        """)

    async def scrape_team_results(
        self,
        team_name: str,
        show_more_clicks: int = 0,
    ) -> dict:
        """
        Full pipeline: search for team → navigate to results → scrape.
        
        Returns dict with team_info and matches.
        """
        # Search for the team
        team_info = await self.search_team(team_name)
        if not team_info:
            return {"error": f"Team '{team_name}' not found", "matches": []}

        # Get results
        matches = await self.get_results(team_info, show_more_clicks)

        return {
            "team": team_info,
            "scraped_at": datetime.now().isoformat(),
            "total_matches": len(matches),
            "matches": matches,
        }


# ─── Output Formatters ───────────────────────────────────────────────────────

def print_table(data: dict):
    """Print results as a formatted terminal table."""
    team = data.get("team", {})
    matches = data.get("matches", [])

    if not matches:
        print("No matches found.")
        return

    print(f"\n{'='*80}")
    print(f"  ⚽ {team.get('name', 'Unknown')}  |  {team.get('country', '')}  |  {len(matches)} results")
    print(f"{'='*80}")
    print(f"  {'Date':<15} {'League':<25} {'Home':<18} {'Score':^7} {'Away':<18} {'Result':>6}")
    print(f"  {'-'*13}   {'-'*23}   {'-'*16}   {'-'*5}   {'-'*16}   {'-'*4}")

    for m in matches:
        dt = m.get("datetime", "")[:14]
        league = m.get("league", "")[:23]
        home = m.get("home_team", "")[:16]
        away = m.get("away_team", "")[:16]
        score = m.get("score", "?-?")
        result = m.get("result", "?")

        # Color result
        if result == "W":
            res_display = "✅ W"
        elif result == "L":
            res_display = "❌ L"
        elif result == "D":
            res_display = "🟡 D"
        else:
            res_display = "  ?"

        print(f"  {dt:<15} {league:<25} {home:<18} {score:^7} {away:<18} {res_display:>6}")

    # Summary
    wins = sum(1 for m in matches if m.get("result") == "W")
    draws = sum(1 for m in matches if m.get("result") == "D")
    losses = sum(1 for m in matches if m.get("result") == "L")
    total_goals = sum(m.get("total_goals", 0) for m in matches)
    avg_goals = total_goals / len(matches) if matches else 0

    print(f"\n  📈 Form: {wins}W {draws}D {losses}L  |  Avg Goals: {avg_goals:.1f} per match")
    print(f"  🔗 {team.get('url', '')}")
    print(f"{'='*80}\n")


def save_json(data: dict, filepath: str):
    """Save results as JSON."""
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved JSON: {filepath}")


def save_csv(data: dict, filepath: str):
    """Save results as CSV."""
    matches = data.get("matches", [])
    if not matches:
        print("No matches to save.")
        return

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    fieldnames = [
        "datetime", "league", "home_team", "away_team",
        "home_score", "away_score", "score", "total_goals",
        "result", "venue", "match_id",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(matches)
    print(f"💾 Saved CSV: {filepath}")


# ─── Direct Team URL Method ──────────────────────────────────────────────────

async def scrape_by_direct_url(slug: str, team_id: str, team_name: str, show_more: int = 0, headless: bool = True):
    """Scrape results using a direct team URL (bypass search)."""
    scraper = FlashScoreScraper(headless=headless)
    await scraper.start()

    try:
        team_info = {
            "name": team_name,
            "slug": slug,
            "team_id": team_id,
            "url": f"{BASE_URL}/team/{slug}/{team_id}/",
            "country": "",
        }
        matches = await scraper.get_results(team_info, show_more)
        return {
            "team": team_info,
            "scraped_at": datetime.now().isoformat(),
            "total_matches": len(matches),
            "matches": matches,
        }
    finally:
        await scraper.close()


# ─── CLI Entry Point ─────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="🏟️  FlashScore Football Results Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 flashscore_scraper.py "Manchester United"
  python3 flashscore_scraper.py "Arsenal" --limit 10
  python3 flashscore_scraper.py "Real Madrid" --output json --save results/real_madrid.json
  python3 flashscore_scraper.py "Barcelona" --show-more 3 --output csv --save results/barca.csv
  python3 flashscore_scraper.py --slug manchester-united --id ppjDR086 --name "Manchester Utd"
        """,
    )
    parser.add_argument("team", nargs="?", help="Team name to search for")
    parser.add_argument("--slug", help="Direct team slug (bypass search)")
    parser.add_argument("--id", help="Direct team ID (bypass search)")
    parser.add_argument("--name", help="Team display name (use with --slug/--id)")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of results shown")
    parser.add_argument("--show-more", type=int, default=0, help="Click 'Show more' N times for older results")
    parser.add_argument("--output", choices=["table", "json", "csv"], default="table", help="Output format (default: table)")
    parser.add_argument("--save", help="Save results to file (JSON or CSV)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode (default)")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")

    args = parser.parse_args()

    if not args.team and not (args.slug and args.id):
        parser.error("Provide a team name or --slug and --id")

    headless = not args.no_headless

    if args.slug and args.id:
        # Direct URL mode
        name = args.name or args.slug.replace("-", " ").title()
        data = await scrape_by_direct_url(args.slug, args.id, name, args.show_more, headless)
    else:
        # Search mode
        scraper = FlashScoreScraper(headless=headless)
        await scraper.start()
        try:
            data = await scraper.scrape_team_results(args.team, args.show_more)
        finally:
            await scraper.close()

    if "error" in data:
        print(f"❌ {data['error']}")
        sys.exit(1)

    # Apply limit
    if args.limit > 0:
        data["matches"] = data["matches"][:args.limit]
        data["total_matches"] = len(data["matches"])

    # Output
    if args.output == "table":
        print_table(data)
    elif args.output == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.output == "csv":
        if args.save:
            save_csv(data, args.save)
        else:
            # Print CSV to stdout
            import io
            output = io.StringIO()
            fieldnames = ["datetime", "league", "home_team", "away_team", "home_score", "away_score", "score", "total_goals", "result", "venue"]
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data["matches"])
            print(output.getvalue())

    # Save if requested
    if args.save:
        if args.save.endswith(".csv"):
            save_csv(data, args.save)
        else:
            save_json(data, args.save)


if __name__ == "__main__":
    asyncio.run(main())
