"""
Process Raw Ball-by-Ball Deliveries Data
Cleans, standardizes, and prepares data for database loading
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sqlite3

def process_deliveries_data():
    """Process raw deliveries CSV and create clean version"""
    
    print("🏏 IPL Deliveries Data Processing")
    print("=" * 60)
    
    # Input/Output paths
    raw_csv = Path("data/raw/ipl_2024/all_ball_by_ball_data.csv")
    processed_csv = Path("data/processed/deliveries_complete.csv")
    db_path = Path("data/cricket_analytics.db")
    
    # Create processed directory if doesn't exist
    processed_csv.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if raw file exists
    if not raw_csv.exists():
        print(f"❌ Raw CSV not found: {raw_csv}")
        print("\n💡 Available files:")
        if Path("data/raw").exists():
            for f in Path("data/raw").rglob("*.csv"):
                print(f"   {f}")
        return False
    
    print(f"📂 Reading raw CSV: {raw_csv}")
    
    # Read raw data
    df = pd.read_csv(raw_csv)
    print(f"✅ Loaded {len(df):,} raw deliveries")
    print(f"📊 Raw columns: {list(df.columns)}")
    
    # Get team name to ID mapping from database
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        teams_df = pd.read_sql_query("SELECT team_id, team_name FROM teams", conn)
        team_name_to_id = dict(zip(teams_df['team_name'], teams_df['team_id']))
        conn.close()
        print(f"\n📋 Loaded {len(team_name_to_id)} team mappings from database")
    else:
        print(f"⚠️  Database not found, will use team names as-is")
        team_name_to_id = {}
    
    print("\n🔄 Processing data...")
    
    # 1. Standardize column names
    print("   1️⃣  Standardizing column names...")
    
    column_renames = {
        'season_id': 'season',
        'inning': 'innings',
        'batsman': 'batter',
        'batting_team': 'team_batting',
        'bowling_team': 'team_bowling',
        'over': 'over_number',
        'ball': 'ball_number',
        'batsman_runs': 'batter_runs',
        'extra_runs': 'extras',
        'dismissal_kind': 'wicket_kind',
        'player_dismissed': 'player_out',
        'fielder': 'fielders_involved'
    }
    
    df = df.rename(columns=column_renames)
    
    # 2. Map team names to IDs
    if team_name_to_id:
        print("   2️⃣  Mapping team names to IDs...")
        
        if 'team_batting' in df.columns:
            df['team_batting_id'] = df['team_batting'].map(team_name_to_id)
            
            # Check for unmapped teams
            unmapped_batting = df[df['team_batting_id'].isna()]['team_batting'].unique()
            if len(unmapped_batting) > 0:
                print(f"      ⚠️  {len(unmapped_batting)} batting teams not mapped:")
                for team in unmapped_batting[:5]:
                    print(f"         - {team}")
                print(f"      💡 Using default ID 0 for unmapped teams")
                df['team_batting_id'] = df['team_batting_id'].fillna(0).astype(int)
        
        if 'team_bowling' in df.columns:
            df['team_bowling_id'] = df['team_bowling'].map(team_name_to_id)
            
            unmapped_bowling = df[df['team_bowling_id'].isna()]['team_bowling'].unique()
            if len(unmapped_bowling) > 0:
                print(f"      ⚠️  {len(unmapped_bowling)} bowling teams not mapped")
                df['team_bowling_id'] = df['team_bowling_id'].fillna(0).astype(int)
    else:
        # No mapping available, keep team names
        print("   2️⃣  Keeping team names (no ID mapping available)")
        if 'team_batting' in df.columns:
            df['team_batting_id'] = df['team_batting']
        if 'team_bowling' in df.columns:
            df['team_bowling_id'] = df['team_bowling']
    
    # 3. Handle boolean columns
    print("   3️⃣  Processing boolean columns...")
    
    boolean_cols = ['is_wicket', 'is_wide_ball', 'is_no_ball', 'is_super_over']
    for col in boolean_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    
    # 4. Handle numeric columns
    print("   4️⃣  Processing numeric columns...")
    
    numeric_cols = [
        'over_number', 'ball_number', 'batter_runs', 'total_runs', 
        'extras', 'wide_ball_runs', 'no_ball_runs'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # 5. Handle text columns
    print("   5️⃣  Cleaning text columns...")
    
    text_cols = ['batter', 'bowler', 'non_striker', 'player_out', 'wicket_kind', 'fielders_involved']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('')
            # Clean player names (remove extra spaces)
            df[col] = df[col].str.strip()
    
    # 6. Select final columns for database
    print("   6️⃣  Selecting columns for database...")
    
    database_columns = [
        'match_id', 'innings', 'over_number', 'ball_number',
        'team_batting_id', 'team_bowling_id',
        'batter', 'non_striker', 'bowler',
        'batter_runs', 'total_runs', 'extras',
        'is_wicket', 'player_out', 'wicket_kind',
        'fielders_involved', 'is_super_over',
        'is_wide_ball', 'is_no_ball',
        'wide_ball_runs', 'no_ball_runs'
    ]
    
    # Keep only columns that exist
    available_cols = [col for col in database_columns if col in df.columns]
    df_clean = df[available_cols].copy()
    
    print(f"   ✅ Final columns: {len(available_cols)} columns")
    print(f"      {', '.join(available_cols)}")
    
    # 7. Data quality checks
    print("\n📊 Data Quality Checks:")
    
    print(f"   Total deliveries: {len(df_clean):,}")
    print(f"   Unique matches: {df_clean['match_id'].nunique():,}")
    print(f"   Unique batters: {df_clean['batter'].nunique():,}")
    print(f"   Unique bowlers: {df_clean['bowler'].nunique():,}")
    print(f"   Total runs: {df_clean['total_runs'].sum():,}")
    print(f"   Total wickets: {df_clean['is_wicket'].sum():,}")
    
    # Check for missing values
    missing_important = df_clean[['match_id', 'batter', 'bowler']].isna().sum()
    if missing_important.sum() > 0:
        print(f"\n   ⚠️  Missing values detected:")
        print(missing_important[missing_important > 0])
    
    # 8. Save processed CSV
    print(f"\n💾 Saving processed CSV to: {processed_csv}")
    
    df_clean.to_csv(processed_csv, index=False)
    
    file_size = processed_csv.stat().st_size / (1024 * 1024)  # MB
    print(f"✅ Saved! File size: {file_size:.2f} MB")
    
    # 9. Show sample data
    print("\n📋 Sample Data (first 3 rows):")
    print(df_clean.head(3).to_string())
    
    print("\n" + "=" * 60)
    print("✅ PROCESSING COMPLETE!")
    print(f"📁 Processed file: {processed_csv}")
    print("🎯 Ready to load into database!")
    print("\n💡 Next step: Run load_deliveries_data.py")
    
    return True

if __name__ == "__main__":
    success = process_deliveries_data()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Data is ready!")
        print("\nNext steps:")
        print("1. Review the processed CSV")
        print("2. Run: python scripts/load_deliveries_data.py")
        print("3. Start querying player statistics!")
    else:
        print("\n❌ Processing failed. Check errors above.")