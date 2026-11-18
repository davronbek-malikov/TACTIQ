"""
StatsBomb Open Data -> matnli hujjatlar (match report, team profile, player profile, leaderboard).

Manba: https://github.com/statsbomb/open-data  (bepul; shart: manbani "StatsBomb" deb ko'rsatish)
Event data: o'yindagi har bir harakat (pas, zarba, pressing ...) koordinata bilan. Maydon 120x80 yard,
har bir event o'sha jamoa chapdan o'ngga hujum qilayotgandek yoziladi.
360 data: har bir event paytida kameraga ko'ringan o'yinchilarning joylashuvi (freeze frame).

Ishga tushirish (loyiha ildizidan):
    python Indexing/01_documents/data_sources/statsbomb.py                 # barcha tanlangan turnirlar
    python Indexing/01_documents/data_sources/statsbomb.py --only 43/106   # faqat World Cup 2022
"""

import argparse
import math
from collections import Counter, defaultdict

from common import load_json, pct, slug, write_document

BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
CREDIT = "Data source: StatsBomb Open Data (https://github.com/statsbomb/open-data)."

# (competition_id, season_id, 360 tahlil qilinsinmi) — 360 fayllar katta (~9 MB/o'yin)
COMPETITIONS = [
    (43, 106, True),     # FIFA World Cup 2022
    (55, 282, False),    # UEFA Euro 2024
    (223, 282, False),   # Copa America 2024
    (1267, 107, False),  # African Cup of Nations 2023
    (9, 281, False),     # 1. Bundesliga 2023/2024 (faqat Bayer Leverkusen o'yinlari)
]

SHOT_ON_TARGET = {"Goal", "Saved", "Saved To Post"}
DEFENSIVE_ACTIONS = {"Interception", "Foul Committed"}   # + Duel(Tackle) — PPDA uchun


def name(item) -> str:
    return item["name"] if item else ""


def fmt_formation(value) -> str:
    """433 -> '4-3-3'."""
    return "-".join(str(value)) if value else "unknown"


# ------------------------------------------------------------------ bitta o'yin tahlili

def new_team_stats() -> dict:
    return defaultdict(float)


def analyse_match(match: dict, events: list, frames: dict | None) -> dict:
    """Event'lardan jamoa va o'yinchi ko'rsatkichlarini hisoblaydi."""
    home, away = match["home_team"]["home_team_name"], match["away_team"]["away_team_name"]
    teams = {home: new_team_stats(), away: new_team_stats()}
    players = defaultdict(lambda: defaultdict(float))        # (player, team) -> ko'rsatkichlar
    positions = defaultdict(Counter)
    by_id = {e["id"]: e for e in events}
    formations, starters, goals, shootout, cards = {}, {}, [], Counter(), []
    on_minute, off_minute = {}, {}
    end_minute = max((e["minute"] for e in events if e["period"] < 5), default=90)

    for e in events:
        etype, team = e["type"]["name"], name(e.get("team"))
        if team not in teams:
            continue
        opp = away if team == home else home
        t, player = teams[team], name(e.get("player"))
        p = players[(player, team)] if player else None
        x = e.get("location", [0, 0])[0]

        if etype == "Starting XI":
            formations[team] = fmt_formation(e["tactics"]["formation"])
            starters[team] = [name(pl["player"]) for pl in e["tactics"]["lineup"]]
            for pl in e["tactics"]["lineup"]:
                on_minute[(name(pl["player"]), team)] = 0
                positions[(name(pl["player"]), team)][name(pl["position"])] += 1
            continue
        if etype == "Substitution":
            off_minute[(player, team)] = e["minute"]
            on_minute[(name(e["substitution"]["replacement"]), team)] = e["minute"]
            continue
        card = name(e.get("foul_committed", {}).get("card")) or name(e.get("bad_behaviour", {}).get("card"))
        if card:
            cards.append(f"{player} ({team}, {card}, {e['minute']}')")
            if card in {"Red Card", "Second Yellow"}:
                off_minute[(player, team)] = e["minute"]

        if e["period"] == 5:                                   # penaltilar seriyasi — alohida
            if etype == "Shot" and name(e["shot"].get("outcome")) == "Goal":
                shootout[team] += 1
            continue
        if e.get("possession_team"):
            teams[name(e["possession_team"])]["possession_time"] += e.get("duration") or 0
        if player and e.get("position"):
            positions[(player, team)][name(e["position"])] += 1

        if etype == "Shot":
            shot = e["shot"]
            xg, outcome = shot.get("statsbomb_xg", 0), name(shot.get("outcome"))
            t["shots"] += 1; t["xg"] += xg; p["shots"] += 1; p["xg"] += xg
            t["on_target"] += outcome in SHOT_ON_TARGET
            t["big_chances"] += xg >= 0.3
            if name(shot.get("type")) == "Penalty":
                p["penalties"] += 1
            key = by_id.get(shot.get("key_pass_id"))
            if key and key.get("player"):
                players[(name(key["player"]), team)]["xa"] += xg
            if outcome == "Goal":
                p["goals"] += 1
                assist = name(key["player"]) if key and key.get("pass", {}).get("goal_assist") else None
                if assist:
                    players[(assist, team)]["assists"] += 1
                kind = " (penalty)" if name(shot.get("type")) == "Penalty" else ""
                goals.append((e["period"], e["minute"], f"{e['minute']}' {player} ({team}){kind}"
                              + (f", assist {assist}" if assist else "") + f", xG {xg:.2f}"))
        elif etype == "Own Goal Against":
            goals.append((e["period"], e["minute"], f"{e['minute']}' own goal by {player} ({team}) for {opp}"))
        elif etype == "Pass":
            pas = e["pass"]
            done = pas.get("outcome") is None
            end_x, end_y = pas["end_location"]
            t["passes"] += 1; p["passes"] += 1
            t["passes_done"] += done; p["passes_done"] += done
            t["passes_under_pressure"] += bool(e.get("under_pressure"))
            if x <= 72:                                        # o'z maydonining 60% qismi — PPDA uchun
                teams[opp]["opp_passes_own_60"] += 1
            if done and end_x - x >= 10 and end_x > 60:
                t["progressive"] += 1; p["progressive"] += 1
            if done and end_x >= 102 and 18 <= end_y <= 62 and not (x >= 102 and 18 <= e["location"][1] <= 62):
                t["box_entries"] += 1
            if pas.get("cross"):
                t["crosses"] += 1
            if pas.get("through_ball") or name(pas.get("technique")) == "Through Ball":
                t["through_balls"] += 1
            if pas.get("shot_assist") or pas.get("goal_assist"):
                p["key_passes"] += 1; t["key_passes"] += 1
            if frames and done and e["id"] in frames:
                close, bypassed = analyse_360(e, frames[e["id"]])
                t["f360_passes"] += 1; t["f360_close"] += close; t["f360_bypassed"] += bypassed
        elif etype == "Pressure":
            t["pressures"] += 1; p["pressures"] += 1
            t["pressures_high"] += x >= 80
            if e.get("counterpress"):
                t["counterpresses"] += 1; p["counterpresses"] += 1
        elif etype == "Dribble":
            ok = name(e["dribble"].get("outcome")) == "Complete"
            t["dribbles"] += 1; t["dribbles_done"] += ok; p["dribbles_done"] += ok
        elif etype == "Ball Recovery" and not e.get("ball_recovery", {}).get("recovery_failure"):
            t["recoveries"] += 1; p["recoveries"] += 1
            t["high_regains"] += x >= 72
        elif etype == "Interception":
            t["interceptions"] += 1; p["interceptions"] += 1
            t["high_regains"] += x >= 72
        elif etype == "Duel" and name(e["duel"].get("type")) == "Tackle":
            won = name(e["duel"].get("outcome")) in {"Won", "Success In Play", "Success Out"}
            p["tackles_won"] += won
        elif etype == "Foul Committed":
            t["fouls"] += 1

        if x >= 48 and (etype in DEFENSIVE_ACTIONS or (etype == "Duel" and name(e["duel"].get("type")) == "Tackle")):
            t["def_actions_high_60"] += 1

    for key, start in on_minute.items():                       # daqiqalar: chiqdi - kirdi
        players[key]["minutes"] += max(0, off_minute.get(key, end_minute) - start)
        players[key]["matches"] += 1
        players[key]["starts"] += start == 0
    goals.sort()
    return {"home": home, "away": away, "teams": teams, "players": players, "positions": positions,
            "formations": formations, "starters": starters, "goals": [g[2] for g in goals],
            "shootout": shootout, "cards": cards}


def analyse_360(event: dict, frame: dict) -> tuple[int, int]:
    """360: pas paytida passer atrofidagi (5 yard) raqiblar va pas 'o'tkazib yuborgan' raqiblar soni."""
    x0, y0 = event["location"]
    end_x = event["pass"]["end_location"][0]
    opponents = [f["location"] for f in frame.get("freeze_frame", []) if not f["teammate"]]
    close = sum(math.dist((x0, y0), loc) <= 5 for loc in opponents)
    bypassed = sum(x0 < loc[0] < end_x for loc in opponents) if end_x > x0 else 0
    return close, bypassed


# ------------------------------------------------------------------ matnga aylantirish

def team_paragraph(label: str, team: str, opp: str, s: dict, total_time: float) -> str:
    """Bitta jamoaning o'yindagi ko'rsatkichlari — o'zi to'liq tushunarli abzats (chunking uchun)."""
    ppda = s["opp_passes_own_60"] / s["def_actions_high_60"] if s["def_actions_high_60"] else float("nan")
    text = (
        f"{team} against {opp} ({label}): xG {s['xg']:.2f} from {s['shots']:.0f} shots "
        f"({s['on_target']:.0f} on target, {s['big_chances']:.0f} big chances with xG >= 0.3). "
        f"Possession about {pct(s['possession_time'], total_time)}. "
        f"Passes {s['passes']:.0f}, completion {pct(s['passes_done'], s['passes'])}, "
        f"{s['passes_under_pressure']:.0f} passes under pressure, {s['progressive']:.0f} progressive passes, "
        f"{s['box_entries']:.0f} completed passes into the box, {s['crosses']:.0f} crosses, "
        f"{s['through_balls']:.0f} through balls, {s['key_passes']:.0f} key passes. "
        f"Pressing: {s['pressures']:.0f} pressures ({s['pressures_high']:.0f} in the attacking third), "
        f"{s['counterpresses']:.0f} counterpresses, PPDA {ppda:.1f} (lower = more intense pressing), "
        f"{s['high_regains']:.0f} ball regains in the opponent's 40% of the pitch. "
        f"Dribbles {s['dribbles_done']:.0f}/{s['dribbles']:.0f} completed, fouls committed {s['fouls']:.0f}."
    )
    if s["f360_passes"]:
        text += (f" StatsBomb 360 (visible area only): on average {s['f360_close'] / s['f360_passes']:.2f} "
                 f"opponents within 5 yards of the passer, and each completed pass bypassed "
                 f"{s['f360_bypassed'] / s['f360_passes']:.2f} opponents on average.")
    return text


def match_report(match: dict, a: dict, comp: str) -> tuple[str, str]:
    home, away = a["home"], a["away"]
    stage = name(match.get("competition_stage"))
    label = f"{comp}, {stage}, {match['match_date']}"
    title = f"{home} {match['home_score']}-{match['away_score']} {away}"
    if a["shootout"]:
        title += f" ({home} won on penalties)" if a["shootout"][home] > a["shootout"][away] else f" ({away} won on penalties)"
        title += f", shootout {a['shootout'][home]:.0f}-{a['shootout'][away]:.0f}"
    total = a["teams"][home]["possession_time"] + a["teams"][away]["possession_time"]
    stadium = name(match.get("stadium"))

    lines = [
        f"# Match report: {title}",
        f"Competition: {label}. Stadium: {stadium or 'unknown'}. Referee: {name(match.get('referee')) or 'unknown'}. {CREDIT}",
        "",
        "## Result and goals",
        f"{title} ({label}). Goals: " + ("; ".join(a["goals"]) if a["goals"] else "no goals") + ".",
        "",
        "## Line-ups and formations",
    ]
    for team in (home, away):
        lines.append(f"{team} started in a {a['formations'].get(team, 'unknown')} against "
                     f"{away if team == home else home} ({label}): {', '.join(a['starters'].get(team, []))}.")
    lines += ["", "## Team statistics"]
    for team in (home, away):
        lines += [team_paragraph(label, team, away if team == home else home, a["teams"][team], total), ""]

    lines.append("## Key players")
    ranked = lambda stat: sorted(((k, v[stat]) for k, v in a["players"].items() if v[stat] > 0), key=lambda kv: -kv[1])[:3]
    for stat, text in [("xg", "highest xG"), ("key_passes", "most key passes"), ("pressures", "most pressures"),
                       ("progressive", "most progressive passes"), ("recoveries", "most ball recoveries")]:
        top = ", ".join(f"{k[0]} ({k[1]}, {v:.2f})" if stat == "xg" else f"{k[0]} ({k[1]}, {v:.0f})" for k, v in ranked(stat))
        if top:
            lines.append(f"In {home} vs {away} ({label}), {text}: {top}.")
    if a["cards"]:
        lines.append(f"Cards in {home} vs {away}: {'; '.join(a['cards'])}.")
    return title, "\n".join(lines)


# ------------------------------------------------------------------ turnir bo'yicha jamlash

def build_competition(cid: int, sid: int, use_360: bool) -> int:
    matches = load_json(f"{BASE}/matches/{cid}/{sid}.json", f"statsbomb/matches_{cid}_{sid}.json")
    comp = f"{matches[0]['competition']['competition_name']} {matches[0]['season']['season_name']}"
    folder = f"statsbomb/{slug(comp)}"
    print(f"[StatsBomb] {comp}: {len(matches)} matches")

    team_totals = defaultdict(lambda: defaultdict(float))
    team_meta = defaultdict(lambda: {"results": Counter(), "formations": Counter(), "matches": []})
    player_totals = defaultdict(lambda: defaultdict(float))
    player_pos = defaultdict(Counter)
    count = 0

    for match in sorted(matches, key=lambda m: m["match_date"]):
        mid = match["match_id"]
        events = load_json(f"{BASE}/events/{mid}.json", f"statsbomb/events/{mid}.json")
        frames = None
        if use_360 and match.get("match_status_360") == "available":
            raw = load_json(f"{BASE}/three-sixty/{mid}.json", f"statsbomb/three-sixty/{mid}.json")
            frames = {f["event_uuid"]: f for f in raw}
        a = analyse_match(match, events, frames)
        title, text = match_report(match, a, comp)
        write_document(folder + "/matches", f"{match['match_date']}_{slug(a['home'])}_vs_{slug(a['away'])}", text, {
            "document_type": "match_report", "topic": slug(comp), "match_id": str(mid),
            "data_source": "statsbomb", "competition": comp,
        })
        count += 1

        for team, goals_for, goals_against in [(a["home"], match["home_score"], match["away_score"]),
                                                (a["away"], match["away_score"], match["home_score"])]:
            for k, v in a["teams"][team].items():
                team_totals[team][k] += v
            team_totals[team]["goals_for"] += goals_for
            team_totals[team]["goals_against"] += goals_against
            opp = a["away"] if team == a["home"] else a["home"]
            team_totals[team]["xg_against"] += a["teams"][opp]["xg"]
            team_totals[team]["possession_total"] += a["teams"][team]["possession_time"] + a["teams"][opp]["possession_time"]
            meta = team_meta[team]
            meta["results"]["W" if goals_for > goals_against else "L" if goals_for < goals_against else "D"] += 1
            meta["formations"][a["formations"].get(team, "unknown")] += 1
            meta["matches"].append(f"{title} ({name(match.get('competition_stage'))})")
        for key, stats in a["players"].items():
            for k, v in stats.items():
                player_totals[key][k] += v
            player_pos[key].update(a["positions"][key])

    count += write_team_profiles(folder, comp, team_totals, team_meta, player_totals)
    count += write_player_profiles(folder, comp, player_totals, player_pos)
    count += write_leaderboards(folder, comp, len(matches), player_totals)
    return count


def write_team_profiles(folder, comp, totals, meta, players) -> int:
    count = 0
    for team, s in totals.items():
        n = len(meta[team]["matches"])
        if n < 3:                                              # 1-2 o'yin — profil uchun juda kam
            continue
        r = meta[team]["results"]
        ppda = s["opp_passes_own_60"] / s["def_actions_high_60"] if s["def_actions_high_60"] else float("nan")
        scorers = sorted(((k[0], v["goals"]) for k, v in players.items() if k[1] == team and v["goals"]), key=lambda kv: -kv[1])
        used = sorted(((k[0], v["minutes"]) for k, v in players.items() if k[1] == team), key=lambda kv: -kv[1])[:11]
        text = "\n".join([
            f"# Team profile: {team} at {comp}",
            f"{CREDIT} Based on {n} matches of {team} in the StatsBomb data for {comp}.",
            "",
            "## Results",
            f"{team} at {comp}: {r['W']} wins, {r['D']} draws, {r['L']} losses; goals {s['goals_for']:.0f} scored, "
            f"{s['goals_against']:.0f} conceded. Matches: {'; '.join(meta[team]['matches'])}.",
            "",
            "## Playing style (per match averages)",
            f"{team} at {comp} averaged xG {s['xg'] / n:.2f} for and {s['xg_against'] / n:.2f} against, "
            f"{s['shots'] / n:.1f} shots, possession about {pct(s['possession_time'], s['possession_total'])}, "
            f"{s['passes'] / n:.0f} passes with {pct(s['passes_done'], s['passes'])} completion, "
            f"{s['progressive'] / n:.1f} progressive passes, {s['box_entries'] / n:.1f} passes into the box, "
            f"{s['crosses'] / n:.1f} crosses per match.",
            f"Pressing profile of {team} at {comp}: {s['pressures'] / n:.0f} pressures per match "
            f"({s['pressures_high'] / n:.0f} in the attacking third), {s['counterpresses'] / n:.0f} counterpresses per match, "
            f"PPDA {ppda:.1f}, {s['high_regains'] / n:.1f} high regains per match.",
            f"Formations used by {team} at {comp}: " + ", ".join(f"{f} ({c} matches)" for f, c in meta[team]["formations"].most_common()) + ".",
            "",
            "## Players",
            f"Top scorers for {team} at {comp}: " + (", ".join(f"{p} {g:.0f}" for p, g in scorers) or "none") + ".",
            f"Most minutes for {team} at {comp}: " + ", ".join(f"{p} {m:.0f}" for p, m in used) + ".",
        ])
        write_document(folder + "/teams", slug(team), text, {
            "document_type": "team_profile", "topic": slug(comp), "team_id": team,
            "data_source": "statsbomb", "competition": comp,
        })
        count += 1
    return count


def write_player_profiles(folder, comp, totals, positions, min_minutes: int = 180) -> int:
    count = 0
    for (player, team), s in totals.items():
        if s["minutes"] < min_minutes or not player:
            continue
        per90 = lambda k: 90 * s[k] / s["minutes"]
        position = positions[(player, team)].most_common(1)[0][0] if positions[(player, team)] else "unknown"
        text = "\n".join([
            f"# Player profile: {player} ({team}) at {comp}",
            f"{CREDIT}",
            "",
            f"{player} played for {team} at {comp}, mostly as {position}: {s['matches']:.0f} matches "
            f"({s['starts']:.0f} starts), about {s['minutes']:.0f} minutes.",
            f"Attack: {s['goals']:.0f} goals ({s['penalties']:.0f} penalty shots taken), {s['assists']:.0f} assists, "
            f"{s['shots']:.0f} shots, xG {s['xg']:.2f}, xA {s['xa']:.2f}, {s['key_passes']:.0f} key passes, "
            f"{s['dribbles_done']:.0f} completed dribbles.",
            f"Passing: {s['passes']:.0f} passes, completion {pct(s['passes_done'], s['passes'])}, "
            f"{s['progressive']:.0f} progressive passes ({per90('progressive'):.1f} per 90).",
            f"Defending and pressing: {s['pressures']:.0f} pressures ({per90('pressures'):.1f} per 90), "
            f"{s['counterpresses']:.0f} counterpresses, {s['recoveries']:.0f} ball recoveries, "
            f"{s['interceptions']:.0f} interceptions, {s['tackles_won']:.0f} tackles won.",
        ])
        write_document(folder + "/players", f"{slug(player)}_{slug(team)}", text, {
            "document_type": "player_profile", "topic": slug(comp), "team_id": team, "player_id": player,
            "data_source": "statsbomb", "competition": comp,
        })
        count += 1
    return count


def write_leaderboards(folder, comp, n_matches, totals) -> int:
    boards = [("goals", "Goals"), ("assists", "Assists"), ("xg", "Expected goals (xG)"), ("xa", "Expected assists (xA)"),
              ("key_passes", "Key passes"), ("progressive", "Progressive passes"), ("dribbles_done", "Completed dribbles"),
              ("pressures", "Pressures"), ("counterpresses", "Counterpresses"), ("recoveries", "Ball recoveries"),
              ("interceptions", "Interceptions"), ("minutes", "Minutes played")]
    lines = [f"# Leaderboards: {comp}", f"{CREDIT} Covers {n_matches} matches of {comp} available in StatsBomb open data.", ""]
    for stat, label in boards:
        top = sorted(((k, v[stat]) for k, v in totals.items() if v[stat] > 0 and k[0]), key=lambda kv: -kv[1])[:10]
        values = ", ".join(f"{i}. {k[0]} ({k[1]}) {v:.2f}" if stat in {"xg", "xa"} else f"{i}. {k[0]} ({k[1]}) {v:.0f}"
                           for i, (k, v) in enumerate(top, 1))
        lines += [f"## {label} — {comp}", f"Top 10 players by {label.lower()} at {comp}: {values}.", ""]
    write_document(folder, "leaderboards", "\n".join(lines), {
        "document_type": "leaderboard", "topic": slug(comp), "data_source": "statsbomb", "competition": comp,
    })
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StatsBomb Open Data -> TACTIQ hujjatlari")
    parser.add_argument("--only", help="masalan 43/106 (competition_id/season_id)")
    args = parser.parse_args()
    selected = [c for c in COMPETITIONS if not args.only or f"{c[0]}/{c[1]}" == args.only]
    total = sum(build_competition(*c) for c in selected)
    print(f"[StatsBomb] {total} documents written")
