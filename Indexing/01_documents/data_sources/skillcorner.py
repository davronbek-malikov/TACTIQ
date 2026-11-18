"""
SkillCorner Open Data -> matnli hujjatlar (tracking'dan olingan off-ball run, pressing, jismoniy ko'rsatkichlar).

Manba: https://github.com/SkillCorner/opendata  (MIT litsenziya; shart: "SkillCorner" deb ko'rsatish)
Tracking data: translyatsiya videosidan kompyuter ko'rish bilan olingan o'yinchi koordinatalari (10 fps).
Dynamic events: tracking'dan hisoblangan voqealar — off_ball_run (to'psiz yugurish), on_ball_engagement
(pressing), player_possession, passing_option.
Aggregates: A-League 2024/2025 mavsumi bo'yicha o'yinchi o'rtacha ko'rsatkichlari (CSV).

Ishga tushirish:
    python Indexing/01_documents/data_sources/skillcorner.py
"""

import csv
from collections import Counter, defaultdict

from common import download, load_json, pct, slug, write_document

BASE = "https://raw.githubusercontent.com/SkillCorner/opendata/master/data"
CREDIT = "Data source: SkillCorner Open Data (https://github.com/SkillCorner/opendata), broadcast tracking data."
SEASON = "A-League 2024/2025"
FOLDER = "skillcorner/a_league_2024_2025"


def read_csv(url: str, name: str) -> list[dict]:
    with download(url, name).open(encoding="utf-8") as file:
        return list(csv.DictReader(file))


def num(row: dict, key: str) -> float:
    value = row.get(key) or ""
    return float(value) if value not in {"", "nan"} else 0.0


def one_row_per_player(rows: list[dict], count_key: str) -> dict:
    """CSV'da bir o'yinchi bir necha pozitsiya bilan takrorlanadi -> eng ko'p o'yinli qatorni olamiz."""
    best = {}
    for row in rows:
        if row["player_id"] not in best or num(row, count_key) > num(best[row["player_id"]], count_key):
            best[row["player_id"]] = row
    return best


def is_true(value: str) -> bool:
    return value == "True"


# ------------------------------------------------------------------ o'yin hisobotlari

def match_report(mid: int) -> tuple[dict, str]:
    info = load_json(f"{BASE}/matches/{mid}/{mid}_match.json", f"skillcorner/{mid}_match.json")
    events = read_csv(f"{BASE}/matches/{mid}/{mid}_dynamic_events.csv", f"skillcorner/{mid}_dynamic_events.csv")
    home, away = info["home_team"]["name"], info["away_team"]["name"]
    names = {info["home_team"]["id"]: home, info["away_team"]["id"]: away}
    date = info["date_time"][:10]
    label = f"{SEASON}, {info['competition_round']['name']}, {date}"
    title = f"{home} {info['home_team_score']}-{info['away_team_score']} {away}"

    runs, engagements, phases = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    runners, pressers, line_breaks = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for e in events:
        team = names.get(int(e["team_id"])) if e["team_id"] else None
        if not team:
            continue
        kind = e["event_type"]
        if kind == "off_ball_run":
            runs[team][e["event_subtype"]] += 1
            runs[team]["_total"] += 1
            runs[team]["_dangerous"] += is_true(e["dangerous"])
            runs[team]["_targeted"] += is_true(e["targeted"])
            runs[team]["_received"] += is_true(e["received"])
            runs[team]["_shot"] += is_true(e["lead_to_shot"])
            runners[team][e["player_name"]] += 1
        elif kind == "on_ball_engagement":
            engagements[team][e["event_subtype"]] += 1
            engagements[team]["_total"] += 1
            engagements[team]["_stop_danger"] += is_true(e["stop_possession_danger"])
            pressers[team][e["player_name"]] += 1
        elif kind == "player_possession":
            phases[team][e["team_in_possession_phase_type"]] += 1
            if e["end_type"] == "pass" and e["pass_outcome"] == "successful":
                line_breaks[team]["_passes"] += 1
                line_breaks[team]["first"] += is_true(e["first_line_break"])
                line_breaks[team]["last"] += is_true(e["last_line_break"])

    lines = [
        f"# Match report: {title}",
        f"Competition: {label}. Stadium: {info['stadium']['name']}. {CREDIT}",
        "",
        "## Result",
        f"{title} ({label}).",
        "",
    ]
    for team in (home, away):
        opp = away if team == home else home
        r, g, ph, lb = runs[team], engagements[team], phases[team], line_breaks[team]
        types = ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in r.most_common() if not k.startswith("_"))
        presses = ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in g.most_common() if not k.startswith("_"))
        phase_total = sum(ph.values())
        phase_text = ", ".join(f"{k.replace('_', ' ')} {pct(v, phase_total)}" for k, v in ph.most_common())
        lines += [
            f"## {team} — off-ball runs and pressing",
            f"Off-ball runs of {team} against {opp} ({label}): {r['_total']} runs ({types}). "
            f"{r['_dangerous']} runs were dangerous, {r['_targeted']} were targeted by a pass, {r['_received']} received the ball, "
            f"{r['_shot']} led to a shot. Most active runners: "
            + ", ".join(f"{p} {c}" for p, c in runners[team].most_common(3)) + ".",
            f"Defensive engagements of {team} against {opp}: {g['_total']} on-ball engagements ({presses}); "
            f"{g['_stop_danger']} stopped a dangerous possession. Most engagements: "
            + ", ".join(f"{p} {c}" for p, c in pressers[team].most_common(3)) + ".",
            f"Phases of play of {team} in possession against {opp} (share of player possessions): {phase_text}. "
            f"Completed passes breaking the first defensive line: {lb['first']} of {lb['_passes']}; "
            f"breaking the last line: {lb['last']}.",
            "",
        ]
    meta = {"title": title, "home": home, "away": away}
    write_document(FOLDER + "/matches", f"{date}_{slug(home)}_vs_{slug(away)}", "\n".join(lines), {
        "document_type": "match_report", "topic": "a_league_2024_2025", "match_id": str(mid), "data_source": "skillcorner",
    })
    return meta, title


# ------------------------------------------------------------------ mavsum: o'yinchi va jamoa profillari

def player_profiles() -> int:
    physical = one_row_per_player(read_csv(f"{BASE}/aggregates/aus1league_physicalaggregates_20242025.csv", "skillcorner/physical.csv"), "count_match")
    runs = one_row_per_player(read_csv(f"{BASE}/aggregates/aus1league_obraggregates_20242025.csv", "skillcorner/obr.csv"), "performance_count")
    passing = one_row_per_player(read_csv(f"{BASE}/aggregates/aus1league_passingaggregates_20242025.csv", "skillcorner/passing.csv"), "performance_count")
    teams = defaultdict(list)
    count = 0

    for p in physical.values():
        pid, player, team = p["player_id"], p["player_name"], p["team_name"]
        r, s = runs.get(pid, {}), passing.get(pid, {})
        teams[team].append(p)
        text = [
            f"# Player profile: {player} ({team}) — {SEASON}",
            f"{CREDIT} Season averages per match, only performances above 60 minutes.",
            "",
            f"{player} ({p['position_group']}, {team}, born {p['player_birthdate']}) in {SEASON}: "
            f"{p['count_match']} matches in the physical data.",
            f"Physical output of {player} per match: total distance {num(p, 'total_distance_full_all'):.0f} m "
            f"({num(p, 'total_metersperminute_full_all'):.0f} m per minute), high-speed running {num(p, 'hsr_distance_full_all'):.0f} m, "
            f"sprint distance {num(p, 'sprint_distance_full_all'):.0f} m in {num(p, 'sprint_count_full_all'):.1f} sprints, "
            f"{num(p, 'highaccel_count_full_all'):.1f} high accelerations, {num(p, 'highdecel_count_full_all'):.1f} high decelerations. "
            f"Top speed (PSV-99) {num(p, 'psv99'):.1f} km/h.",
        ]
        if r:
            text.append(
                f"Off-ball runs of {player} per 30 minutes of team possession: {num(r, 'offballrun_count_p30tip'):.1f} runs — "
                f"runs in behind {num(r, 'behindrun_count_p30tip'):.1f}, runs ahead of the ball {num(r, 'aheadoftheballrun_count_p30tip'):.1f}, "
                f"coming short {num(r, 'comingshortrun_count_p30tip'):.1f}, cross receiver {num(r, 'crossreceiverrun_count_p30tip'):.1f}, "
                f"overlaps {num(r, 'overlaprun_count_p30tip'):.1f}, underlaps {num(r, 'underlaprun_count_p30tip'):.1f}, "
                f"support {num(r, 'supportrun_count_p30tip'):.1f}. Dangerous runs {num(r, 'offballrun_count_dangerous_p30tip'):.1f}, "
                f"runs into the penalty area {num(r, 'offballrun_count_penaltyarea_p30tip'):.1f}, "
                f"runs that received the ball {num(r, 'offballrun_count_received_p30tip'):.1f}.")
        if s:
            text.append(
                f"Passing of {player} per 30 minutes of team possession: {num(s, 'pass_count_attempted_p30tip'):.1f} passes attempted, "
                f"completion {num(s, 'pass_pct_completed'):.0f}%, line-breaking passes completed {num(s, 'pass_count_linebreak_completed_p30tip'):.1f}, "
                f"passes to a teammate's run completed {num(s, 'pass_count_torun_completed_p30tip'):.1f}, "
                f"dangerous passes completed {num(s, 'pass_count_dangerous_completed_p30tip'):.1f}.")
        write_document(FOLDER + "/players", f"{slug(player)}_{slug(team)}", "\n".join(text), {
            "document_type": "player_profile", "topic": "a_league_2024_2025", "team_id": team, "player_id": player,
            "data_source": "skillcorner",
        })
        count += 1

    for team, rows in teams.items():                           # jamoa: jismoniy liderlar
        top = lambda key, unit: ", ".join(f"{r['player_name']} {num(r, key):.1f}{unit}"
                                          for r in sorted(rows, key=lambda r: -num(r, key))[:5])
        text = "\n".join([
            f"# Team physical profile: {team} — {SEASON}",
            f"{CREDIT} {len(rows)} players with performances above 60 minutes.",
            "",
            f"Fastest players of {team} in {SEASON} by top speed (PSV-99): {top('psv99', ' km/h')}.",
            f"Most distance per match for {team}: {top('total_distance_full_all', ' m')}.",
            f"Most sprints per match for {team}: {top('sprint_count_full_all', '')}.",
            f"Most high-speed running per match for {team}: {top('hsr_distance_full_all', ' m')}.",
        ])
        write_document(FOLDER + "/teams", slug(team), text, {
            "document_type": "team_profile", "topic": "a_league_2024_2025", "team_id": team, "data_source": "skillcorner",
        })
        count += 1
    return count


if __name__ == "__main__":
    matches = load_json(f"{BASE}/matches.json", "skillcorner/matches.json")
    print(f"[SkillCorner] {len(matches)} matches")
    for m in matches:
        match_report(m["id"])
    total = len(matches) + player_profiles()
    print(f"[SkillCorner] {total} documents written")
