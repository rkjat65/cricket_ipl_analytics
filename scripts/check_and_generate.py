"""
Run quick SQL checks for sample players and generate chart images for Home and Player Records
Saves images to generated_images/ and prints SQL results to stdout.
"""
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pathlib import Path
import os

OUTPUT_DIR = Path('generated_images')
OUTPUT_DIR.mkdir(exist_ok=True)

DB_PATH = Path('data/cricket_analytics.db')
if not DB_PATH.exists():
    print(f"ERROR: database not found at {DB_PATH}")
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)

# Helper to save fig to png (fallback to html)
def save_fig(fig, name):
    out_png = OUTPUT_DIR / f"{name}.png"
    out_html = OUTPUT_DIR / f"{name}.html"
    try:
        pio.to_image(fig, file=str(out_png), format='png', engine='kaleido')
        print(f"Saved image: {out_png}")
        return str(out_png)
    except Exception as e:
        print(f"Could not save PNG (kaleido missing): {e}. Saving HTML instead.")
        fig.write_html(str(out_html))
        print(f"Saved html: {out_html}")
        return str(out_html)

# 1) Top 10 Run Scorers
q_runs = """
SELECT batter as player,
       SUM(batter_runs) as total_runs,
       COUNT(DISTINCT match_id) as matches
FROM deliveries
WHERE batter IS NOT NULL
GROUP BY batter
ORDER BY total_runs DESC
LIMIT 10
"""
print('\nTop 10 Run Scorers SQL:')
runs_df = pd.read_sql_query(q_runs, conn)
print(runs_df.to_string(index=False))
fig = px.bar(runs_df, x='total_runs', y='player', orientation='h',
             title='Top 10 Run Scorers (All-Time)', color='total_runs', color_continuous_scale='Oranges')
fig.update_layout(yaxis={'title':''}, xaxis_title='Total Runs')
fig.update_layout(yaxis=dict(autorange='reversed'))
save_fig(fig, 'top10_run_scorers')

# 2) Top 10 Wicket Takers (use is_wicket)
q_wkts = """
SELECT bowler as player,
       SUM(CASE WHEN is_wicket = 1 AND wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as total_wickets,
       COUNT(DISTINCT match_id) as matches
FROM deliveries
WHERE bowler IS NOT NULL
GROUP BY bowler
ORDER BY total_wickets DESC
LIMIT 10
"""
print('\nTop 10 Wicket Takers SQL:')
wkts_df = pd.read_sql_query(q_wkts, conn)
print(wkts_df.to_string(index=False))
fig = px.bar(wkts_df, x='total_wickets', y='player', orientation='h',
             title='Top 10 Wicket Takers (All-Time)', color='total_wickets', color_continuous_scale='Reds')
fig.update_layout(yaxis={'title':''}, xaxis_title='Total Wickets')
fig.update_layout(yaxis=dict(autorange='reversed'))
save_fig(fig, 'top10_wicket_takers')

# 3) Hall of Fame: Highest Innings, Best Bowling, Most Sixes
q_highest = """
SELECT batter as player, SUM(batter_runs) as runs
FROM deliveries
GROUP BY match_id, innings, batter
ORDER BY runs DESC
LIMIT 5
"""
print('\nTop Innings (Highest Scores):')
high_df = pd.read_sql_query(q_highest, conn)
print(high_df.to_string(index=False))
fig = px.bar(high_df, x='runs', y='player', orientation='h', title='Top Innings - Highest Scores', color='runs', color_continuous_scale='Oranges')
fig.update_layout(yaxis=dict(autorange='reversed'))
save_fig(fig, 'hall_highest_scores')

q_best_bowling = """
SELECT bowler as player, 
       SUM(CASE WHEN is_wicket = 1 AND wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
       SUM(batter_runs + wide_ball_runs + no_ball_runs) as runs
FROM deliveries
GROUP BY match_id, innings, bowler
ORDER BY wickets DESC, runs ASC
LIMIT 5
"""
print('\nBest Bowling (innings):')
bow_df = pd.read_sql_query(q_best_bowling, conn)
print(bow_df.to_string(index=False))
fig = px.bar(bow_df, x='wickets', y='player', orientation='h', title='Best Bowling Performances', color='wickets', color_continuous_scale='Reds')
fig.update_layout(yaxis=dict(autorange='reversed'))
save_fig(fig, 'hall_best_bowling')

q_sixes = """
SELECT batter as player, COUNT(*) as total_sixes
FROM deliveries
WHERE batter_runs = 6
GROUP BY batter
ORDER BY total_sixes DESC
LIMIT 5
"""
print('\nMost Sixes (players):')
sx_df = pd.read_sql_query(q_sixes, conn)
print(sx_df.to_string(index=False))
fig = px.bar(sx_df, x='total_sixes', y='player', orientation='h', title='Most Sixes', color='total_sixes', color_continuous_scale='Purples')
fig.update_layout(yaxis=dict(autorange='reversed'))
save_fig(fig, 'hall_most_sixes')

# 4) Check sample players
sample_players = ['V Kohli', 'YS Chahal']
for p in sample_players:
    qb = f"SELECT SUM(batter_runs) as runs, COUNT(DISTINCT match_id) as matches FROM deliveries WHERE batter = '{p}'"
    rb = pd.read_sql_query(qb, conn)
    print(f"\nSample Player (bat) - {p}: ")
    print(rb.to_string(index=False))

    qw = f"SELECT SUM(CASE WHEN is_wicket = 1 AND wicket_kind NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as wickets, COUNT(DISTINCT match_id) as matches FROM deliveries WHERE bowler = '{p}'"
    rw = pd.read_sql_query(qw, conn)
    print(f"Sample Player (bowl) - {p}: ")
    print(rw.to_string(index=False))

print('\nVerification script finished.')
