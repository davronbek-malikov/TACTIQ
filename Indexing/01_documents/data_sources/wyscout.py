"""
Wyscout public dataset (Pappalardo et al., 2019, Scientific Data) -> matnli hujjatlar.

Manba: https://figshare.com/collections/Soccer_match_event_dataset/4415000  (CC BY 4.0 — manbani ko'rsatish shart)
Event data: World Cup 2018, Euro 2016 va 5 ta top liganing 2017/2018 mavsumi. Koordinata 0-100 (%),
har bir event o'sha jamoa chapdan o'ngga hujum qilayotgandek. xG yo'q (Wyscout bu datasetda bermagan).
Tag'lar: 101 gol, 301 assist, 302 key pass, 1801 aniq (accurate), 703 duel yutildi, 1401 interception.

Ishga tushirish:
    python Indexing/01_documents/data_sources/wyscout.py
"""

import json
import re
import zipfile
from collections import Counter, defaultdict

from common import CACHE_DIR, download, pct, slug, write_document

FILES = "https://ndownloader.figshare.com/files"
CREDIT = ("Data source: Wyscout public soccer-logs dataset (Pappalardo et al., 2019, Scientific Data, CC BY 4.0, "
          "https://figshare.com/collections/Soccer_match_event_dataset/4415000).")
TOURNAMENTS = {"World_Cup": "FIFA World Cup 2018", "European_Championship": "UEFA Euro 2016"}
LEAGUES = {"England": "Premier League 2017/2018", "Spain": "La Liga 2017/2018", "Italy": "Serie A 2017/2018",
           "Germany": "Bundesliga 2017/2018", "France": "Ligue 1 2017/2018"}


def fix(text: str) -> str:
    """Datasetda harflar '\\u00e9' ko'rinishida saqlangan -> 'é'."""
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text or "")


def tags(event: dict) -> set:
    return {t["id"] for t in event["tags"]}


def load_reference():
    download(f"{FILES}/14464685", "wyscout/events.zip")
    download(f"{FILES}/14464622", "wyscout/matches.zip")
    players = {p["wyId"]: p for p in json.loads(download(f"{FILES}/15073721", "wyscout/players.json").read_text(encoding="utf-8"))}
    teams = {t["wyId"]: fix(t["name"]) for t in json.loads(download(f"{FILES}/15073697", "wyscout/teams.json").read_text(encoding="utf-8"))}
    return players, teams


def read_zip(name: str, member: str):
    with zipfile.ZipFile(CACHE_DIR / "wyscout" / name) as archive:
        return json.loads(archive.read(member))


# ------------------------------------------------------------------ turnirlar: event'lar bilan

def analyse(match: dict, events: list, teams: dict, players: dict) -> dict:
    team_ids = [int(t) for t in match["teamsData"]]
    stats = {t: defaultdict(float) for t in team_ids}
    pstats = defaultdict(lambda: defaultdict(float))
    goals = []
    for e in events:
        if e["matchPeriod"] == "P" or e["teamId"] not in stats:   # penaltilar seriyasi hisobga olinmaydi
            continue
        t, tg, name, sub = stats[e["teamId"]], tags(e), e["eventName"], e["subEventName"]
        opp = team_ids[1] if e["teamId"] == team_ids[0] else team_ids[0]
        p = pstats[(e["playerId"], e["teamId"])]
        x = e["positions"][0]["x"] if e["positions"] else 0
        minute = int(e["eventSec"] // 60) + {"1H": 0, "2H": 45, "E1": 90, "E2": 105}.get(e["matchPeriod"], 0)

        if name == "Shot" or sub in {"Penalty", "Free kick shot"}:
            t["shots"] += 1; p["shots"] += 1
            t["on_target"] += 1801 in tg
            if 101 in tg:
                p["goals"] += 1
                goals.append((minute, f"{minute}' {player_name(players, e['playerId'])} ({teams[e['teamId']]})"
                              + (" (penalty)" if sub == "Penalty" else "")))
        if 102 in tg:                                          # o'z darvozasiga gol
            goals.append((minute, f"{minute}' own goal by {player_name(players, e['playerId'])} "
                                  f"({teams[e['teamId']]}) for {teams[opp]}"))
        if name == "Pass":
            t["passes"] += 1; p["passes"] += 1
            t["passes_done"] += 1801 in tg; p["passes_done"] += 1801 in tg
            t["crosses"] += sub == "Cross"
            t["smart_passes"] += sub == "Smart pass"
            t["long_balls"] += sub in {"High pass", "Launch"}
            if 302 in tg:
                t["key_passes"] += 1; p["key_passes"] += 1
            if x <= 60:
                stats[opp]["opp_passes_own_60"] += 1
        if 301 in tg:
            p["assists"] += 1
        if name == "Duel":
            t["duels"] += 1; t["duels_won"] += 703 in tg; p["duels_won"] += 703 in tg
            if sub == "Air duel":
                t["aerials"] += 1; t["aerials_won"] += 703 in tg
        if 1401 in tg:
            t["interceptions"] += 1; p["interceptions"] += 1
        if name == "Foul":
            t["fouls"] += 1
        if x >= 40 and (sub == "Ground defending duel" or name == "Foul" or 1401 in tg):
            t["def_actions_high_60"] += 1
    goals.sort()
    return {"teams": stats, "players": pstats, "goals": [g[1] for g in goals]}


def player_name(players: dict, pid: int) -> str:
    return fix(players.get(pid, {}).get("shortName", f"player {pid}"))


def minutes_played(match: dict) -> dict:
    """Lineup + almashtirishlardan taxminiy daqiqalar."""
    end = 120 if match["duration"] in {"ExtraTime", "Penalties"} else 90
    result = {}
    for tid, td in match["teamsData"].items():
        on = {p["playerId"]: 0 for p in td["formation"]["lineup"]}
        off = {}
        for s in td["formation"].get("substitutions") or []:
            off[s["playerOut"]] = s["minute"]; on[s["playerIn"]] = s["minute"]
        for pid, start in on.items():
            result[(pid, int(tid))] = max(0, off.get(pid, end) - start)
    return result


def team_text(team: str, opp: str, label: str, s: dict) -> str:
    ppda = s["opp_passes_own_60"] / s["def_actions_high_60"] if s["def_actions_high_60"] else float("nan")
    return (f"{team} against {opp} ({label}): {s['shots']:.0f} shots ({s['on_target']:.0f} on target), "
            f"{s['passes']:.0f} passes with {pct(s['passes_done'], s['passes'])} accuracy, {s['key_passes']:.0f} key passes, "
            f"{s['smart_passes']:.0f} smart passes, {s['crosses']:.0f} crosses, {s['long_balls']:.0f} long or high passes. "
            f"Duels won {pct(s['duels_won'], s['duels'])} ({s['duels_won']:.0f}/{s['duels']:.0f}), aerial duels won "
            f"{pct(s['aerials_won'], s['aerials'])}, {s['interceptions']:.0f} interceptions, {s['fouls']:.0f} fouls, "
            f"PPDA {ppda:.1f} (lower = more intense pressing).")


def build_tournament(key: str, comp: str, players: dict, teams: dict) -> int:
    matches = read_zip("matches.zip", f"matches_{key}.json")
    events_by_match = defaultdict(list)
    for e in read_zip("events.zip", f"events_{key}.json"):
        events_by_match[e["matchId"]].append(e)
    folder = f"wyscout/{slug(comp)}"
    totals = defaultdict(lambda: defaultdict(float))
    record = defaultdict(lambda: {"res": Counter(), "matches": []})
    ptotals = defaultdict(lambda: defaultdict(float))
    print(f"[Wyscout] {comp}: {len(matches)} matches")

    for m in sorted(matches, key=lambda m: m["dateutc"]):
        a = analyse(m, events_by_match[m["wyId"]], teams, players)
        side = {td["side"]: (int(tid), td) for tid, td in m["teamsData"].items()}
        (hid, hd), (aid, ad) = side["home"], side["away"]
        home, away, date = teams[hid], teams[aid], m["dateutc"][:10]
        label = f"{comp}, {date}, {fix(m['venue'])}"
        title = f"{home} {hd['score']}-{ad['score']} {away}"
        if hd.get("scoreP") or ad.get("scoreP"):
            title += f" (penalties {hd['scoreP']}-{ad['scoreP']})"
        lineups = []
        for tid, td in ((hid, hd), (aid, ad)):
            names = ", ".join(player_name(players, p["playerId"]) for p in td["formation"]["lineup"])
            lineups.append(f"{teams[tid]} starting XI against {away if tid == hid else home} ({label}): {names}.")
        text = "\n".join([
            f"# Match report: {title}", f"Competition: {label}. {CREDIT}", "",
            "## Result and goals",
            f"{title} ({label}). Half-time {hd['scoreHT']}-{ad['scoreHT']}. Goals: " + ("; ".join(a["goals"]) or "no goals") + ".",
            "", "## Line-ups", *lineups, "", "## Team statistics",
            team_text(home, away, label, a["teams"][hid]), "", team_text(away, home, label, a["teams"][aid]),
        ])
        write_document(folder + "/matches", f"{date}_{slug(home)}_vs_{slug(away)}", text, {
            "document_type": "match_report", "topic": slug(comp), "match_id": str(m["wyId"]), "data_source": "wyscout"})

        for tid, td, od in ((hid, hd, ad), (aid, ad, hd)):
            for k, v in a["teams"][tid].items():
                totals[tid][k] += v
            gf, ga = td["score"] + td["scoreET"], od["score"] + od["scoreET"]
            totals[tid]["gf"] += td["score"]; totals[tid]["ga"] += od["score"]
            record[tid]["res"]["W" if m["winner"] == tid else "D" if m["winner"] == 0 else "L"] += 1
            record[tid]["matches"].append(title)
        for key2, mins in minutes_played(m).items():
            ptotals[key2]["minutes"] += mins; ptotals[key2]["matches"] += 1
        for key2, s in a["players"].items():
            for k, v in s.items():
                ptotals[key2][k] += v

    count = len(matches)
    for tid, s in totals.items():
        n, r = len(record[tid]["matches"]), record[tid]["res"]
        team = teams[tid]
        scorers = sorted(((player_name(players, k[0]), v["goals"]) for k, v in ptotals.items() if k[1] == tid and v["goals"]), key=lambda kv: -kv[1])
        text = "\n".join([
            f"# Team profile: {team} at {comp}", f"{CREDIT} Based on {n} matches.", "",
            f"{team} at {comp}: {r['W']} wins, {r['D']} draws, {r['L']} losses (a penalty shootout counts as a draw); "
            f"goals {s['gf']:.0f} scored and {s['ga']:.0f} conceded. Matches: {'; '.join(record[tid]['matches'])}.",
            f"Style of {team} at {comp} per match: {s['shots'] / n:.1f} shots, {s['passes'] / n:.0f} passes with "
            f"{pct(s['passes_done'], s['passes'])} accuracy, {s['key_passes'] / n:.1f} key passes, {s['crosses'] / n:.1f} crosses, "
            f"{s['smart_passes'] / n:.1f} smart passes, duels won {pct(s['duels_won'], s['duels'])}.",
            f"Top scorers for {team} at {comp}: " + (", ".join(f"{p} {g:.0f}" for p, g in scorers) or "none") + ".",
        ])
        write_document(folder + "/teams", slug(team), text, {
            "document_type": "team_profile", "topic": slug(comp), "team_id": team, "data_source": "wyscout"})
        count += 1

    lines = [f"# Leaderboards: {comp}", f"{CREDIT} Covers {len(matches)} matches.", ""]
    for stat, label in [("goals", "Goals"), ("assists", "Assists"), ("key_passes", "Key passes"), ("shots", "Shots"),
                        ("duels_won", "Duels won"), ("interceptions", "Interceptions"), ("minutes", "Minutes played")]:
        top = sorted(((k, v[stat]) for k, v in ptotals.items() if v[stat] > 0), key=lambda kv: -kv[1])[:10]
        lines += [f"## {label} — {comp}", f"Top 10 players by {label.lower()} at {comp}: " + ", ".join(
            f"{i}. {player_name(players, k[0])} ({teams.get(k[1], '')}) {v:.0f}" for i, (k, v) in enumerate(top, 1)) + ".", ""]
    write_document(folder, "leaderboards", "\n".join(lines), {
        "document_type": "leaderboard", "topic": slug(comp), "data_source": "wyscout"})
    return count + 1


# ------------------------------------------------------------------ ligalar: faqat natijalar (event fayllari juda katta)

def build_league_table(key: str, comp: str, players: dict, teams: dict) -> int:
    matches = read_zip("matches.zip", f"matches_{key}.json")
    table = defaultdict(lambda: Counter())
    scorers = Counter()
    for m in matches:
        (t1, d1), (t2, d2) = [(int(k), v) for k, v in m["teamsData"].items()]
        for tid, d, o in ((t1, d1, d2), (t2, d2, d1)):
            row = table[tid]
            row["P"] += 1; row["GF"] += d["score"]; row["GA"] += o["score"]
            row["W" if d["score"] > o["score"] else "D" if d["score"] == o["score"] else "L"] += 1
            for p in d["formation"]["lineup"] + d["formation"]["bench"]:
                if p.get("goals") not in (None, "null", "0"):
                    scorers[(p["playerId"], tid)] += int(p["goals"])
    ranked = sorted(table.items(), key=lambda kv: (-(3 * kv[1]["W"] + kv[1]["D"]), -(kv[1]["GF"] - kv[1]["GA"]), -kv[1]["GF"]))
    rows = [f"{i}. {teams[tid]}: {r['P']} played, {r['W']} won, {r['D']} drawn, {r['L']} lost, goals {r['GF']}-{r['GA']}, "
            f"{3 * r['W'] + r['D']} points." for i, (tid, r) in enumerate(ranked, 1)]
    text = "\n".join([
        f"# Final league table: {comp}", f"{CREDIT} Computed from {len(matches)} match results.", "",
        f"## {comp} — table", *rows, "",
        f"## {comp} — top scorers",
        f"Top scorers in {comp}: " + ", ".join(f"{player_name(players, p)} ({teams[t]}) {g}" for (p, t), g in scorers.most_common(15)) + ".",
    ])
    write_document(f"wyscout/{slug(comp)}", "league_table", text, {
        "document_type": "league_table", "topic": slug(comp), "data_source": "wyscout"})
    return 1


if __name__ == "__main__":
    players, teams = load_reference()
    total = sum(build_tournament(k, c, players, teams) for k, c in TOURNAMENTS.items())
    total += sum(build_league_table(k, c, players, teams) for k, c in LEAGUES.items())
    print(f"[Wyscout] {total} documents written")
