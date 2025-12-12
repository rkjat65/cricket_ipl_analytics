"""
Load ball-by-ball deliveries data into database
Run from TERMINAL only!
"""

import sqlite3
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import sys

def load_deliveries_data(skip_prompt=False, force_reload=False):
    """Load deliveries data from CSV to database"""
    
    print("🏏 Loading IPL Deliveries Data...")
    print("=" * 60)
    
    db_path = Path("data/cricket_analytics.db")
    deliveries_csv = Path("data/processed/deliveries_complete.csv")
    
    if not deliveries_csv.exists():
        print(f"❌ CSV not found: {deliveries_csv}")
        return False
    
    print(f"📂 Reading: {deliveries_csv}")
    
    try:
        df = pd.read_csv(deliveries_csv)
        print(f"✅ Loaded {len(df):,} deliveries")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM deliveries")
        current_count = cursor.fetchone()[0]
        print(f"📊 Current in DB: {current_count:,}")
        
        if current_count > 0:
            if skip_prompt:
                print("✅ Data exists. Skipping.")
                conn.close()
                return True
            elif force_reload:
                print("🗑️  Reloading...")
                cursor.execute("DELETE FROM deliveries")
                conn.commit()
            else:
                try:
                    response = input(f"\n⚠️  Reload {current_count:,} deliveries? (yes/no): ")
                    if response.lower() != 'yes':
                        print("❌ Cancelled.")
                        conn.close()
                        return False
                    cursor.execute("DELETE FROM deliveries")
                    conn.commit()
                except:
                    print("⚠️  Non-interactive. Skipping.")
                    conn.close()
                    return True
        
        print("\n🔄 Processing...")
        
        teams_df = pd.read_sql_query("SELECT team_id, team_name FROM teams", conn)
        team_map = dict(zip(teams_df['team_name'], teams_df['team_id']))
        
        if 'team_batting' in df.columns:
            if isinstance(df['team_batting'].iloc[0], str):
                df['team_batting_id'] = df['team_batting'].map(team_map).fillna(0)
            else:
                df['team_batting_id'] = df['team_batting']
            df = df.drop(columns=['team_batting'])
        
        if 'team_bowling' in df.columns:
            if isinstance(df['team_bowling'].iloc[0], str):
                df['team_bowling_id'] = df['team_bowling'].map(team_map).fillna(0)
            else:
                df['team_bowling_id'] = df['team_bowling']
            df = df.drop(columns=['team_bowling'])
        
        cols = [
            'match_id', 'innings', 'over_number', 'ball_number',
            'team_batting_id', 'team_bowling_id',
            'batter', 'non_striker', 'bowler',
            'batter_runs', 'total_runs', 'extras',
            'is_wicket', 'player_out', 'wicket_kind',
            'fielders_involved', 'is_super_over',
            'is_wide_ball', 'is_no_ball',
            'wide_ball_runs', 'no_ball_runs'
        ]
        
        df_insert = df[[c for c in cols if c in df.columns]].copy()
        
        for col in ['is_wicket', 'is_wide_ball', 'is_no_ball', 'is_super_over']:
            if col in df_insert.columns:
                df_insert[col] = df_insert[col].fillna(0).astype(int)
        
        df_insert = df_insert.fillna(0)
        
        print(f"📦 Inserting {len(df_insert):,} rows...")
        
        for i in tqdm(range(0, len(df_insert), 10000), desc="Loading"):
            df_insert.iloc[i:i+10000].to_sql('deliveries', conn, if_exists='append', index=False)
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM deliveries")
        final = cursor.fetchone()[0]
        print(f"\n✅ Loaded {final:,} deliveries!")
        
        print("\n🏏 Top 5 Scorers:")
        top = pd.read_sql_query("""
            SELECT batter, SUM(batter_runs) as runs
            FROM deliveries GROUP BY batter ORDER BY runs DESC LIMIT 5
        """, conn)
        for i, row in top.iterrows():
            print(f"   {i+1}. {row['batter']}: {row['runs']:,}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    skip = '--skip-prompt' in sys.argv
    force = '--force' in sys.argv
    
    if '--help' in sys.argv:
        print("Usage: python scripts/load_deliveries_data.py [--skip-prompt] [--force]")
    else:
        load_deliveries_data(skip_prompt=skip, force_reload=force)