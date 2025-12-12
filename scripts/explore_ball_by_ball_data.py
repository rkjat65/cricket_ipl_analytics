"""
Ball-by-Ball Data Explorer
Analyzes all_ball_by_ball_data.csv to understand data structure and quality
Generates summary statistics and insights
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

BALL_DATA_FILE = Path("data/raw/ipl_2024/all_ball_by_ball_data.csv")


def load_ball_data():
    """Load and explore ball-by-ball data"""
    logger.info("\n" + "="*70)
    logger.info("🏏 BALL-BY-BALL DATA EXPLORER")
    logger.info("="*70)
    
    logger.info(f"\n📂 Loading: {BALL_DATA_FILE}")
    
    if not BALL_DATA_FILE.exists():
        logger.error(f"❌ File not found: {BALL_DATA_FILE}")
        return None
    
    df = pd.read_csv(BALL_DATA_FILE)
    
    logger.info(f"✅ Loaded successfully!")
    logger.info(f"\n📊 Dataset Size:")
    logger.info(f"  - Total deliveries: {len(df):,}")
    logger.info(f"  - Columns: {len(df.columns)}")
    logger.info(f"  - Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    
    logger.info(f"\n📋 Columns:")
    for i, col in enumerate(df.columns, 1):
        logger.info(f"  {i:2d}. {col}")
    
    logger.info(f"\n📈 Sample Data (first 5 rows):")
    logger.info(df.head().to_string())
    
    return df


def analyze_structure(df):
    """Analyze data structure"""
    logger.info(f"\n" + "="*70)
    logger.info("🔍 DATA STRUCTURE ANALYSIS")
    logger.info("="*70)
    
    # Match count
    if 'ID' in df.columns or 'match_id' in df.columns:
        match_col = 'ID' if 'ID' in df.columns else 'match_id'
        unique_matches = df[match_col].nunique()
        logger.info(f"\n📊 Matches:")
        logger.info(f"  - Unique matches: {unique_matches:,}")
        logger.info(f"  - Deliveries per match (avg): {len(df)/unique_matches:.1f}")
    
    # Seasons
    season_cols = ['Season', 'season']
    season_col = next((col for col in season_cols if col in df.columns), None)
    
    if season_col:
        seasons = sorted(df[season_col].unique())
        logger.info(f"\n📅 Seasons:")
        logger.info(f"  - Seasons covered: {seasons}")
        logger.info(f"  - Years: {len(seasons)}")
        
        logger.info(f"\n  Deliveries by season:")
        season_counts = df[season_col].value_counts().sort_index()
        for season, count in season_counts.items():
            logger.info(f"    {season}: {count:,} deliveries")
    
    # Innings
    if 'innings' in df.columns:
        logger.info(f"\n🏏 Innings:")
        innings_counts = df['innings'].value_counts().sort_index()
        for inning, count in innings_counts.items():
            logger.info(f"  - Inning {inning}: {count:,} deliveries")
    
    return True


def analyze_batting(df):
    """Analyze batting data"""
    logger.info(f"\n" + "="*70)
    logger.info("🏏 BATTING ANALYSIS")
    logger.info("="*70)
    
    # Find columns
    batter_col = next((col for col in ['batter', 'batsman', 'striker'] if col in df.columns), None)
    runs_col = next((col for col in ['batsman_run', 'batsman_runs', 'batter_runs'] if col in df.columns), None)
    
    if not batter_col or not runs_col:
        logger.warning("⚠️ Batting columns not found")
        return
    
    # Top run scorers
    logger.info(f"\n🏆 Top 10 Run Scorers (All Time):")
    top_scorers = df.groupby(batter_col)[runs_col].sum().sort_values(ascending=False).head(10)
    for idx, (batter, runs) in enumerate(top_scorers.items(), 1):
        balls = len(df[df[batter_col] == batter])
        sr = (runs / balls * 100) if balls > 0 else 0
        logger.info(f"  {idx:2d}. {batter:<30} {int(runs):5d} runs ({balls:4d} balls, SR: {sr:.1f})")
    
    # Boundaries
    if runs_col in df.columns:
        fours = len(df[df[runs_col] == 4])
        sixes = len(df[df[runs_col] == 6])
        logger.info(f"\n🎯 Boundaries:")
        logger.info(f"  - Total fours: {fours:,}")
        logger.info(f"  - Total sixes: {sixes:,}")
        logger.info(f"  - Boundary %: {(fours + sixes)/len(df)*100:.1f}%")


def analyze_bowling(df):
    """Analyze bowling data"""
    logger.info(f"\n" + "="*70)
    logger.info("🎯 BOWLING ANALYSIS")
    logger.info("="*70)
    
    bowler_col = next((col for col in ['bowler', 'bowling_team'] if col in df.columns), None)
    wicket_col = next((col for col in ['isWicketDelivery', 'is_wicket', 'wicket'] if col in df.columns), None)
    runs_col = next((col for col in ['total_run', 'total_runs'] if col in df.columns), None)
    
    if not bowler_col:
        logger.warning("⚠️ Bowling columns not found")
        return
    
    # Top wicket takers
    if wicket_col:
        logger.info(f"\n🏅 Top 10 Wicket Takers (All Time):")
        top_wickets = df[df[wicket_col] == 1].groupby(bowler_col).size().sort_values(ascending=False).head(10)
        for idx, (bowler, wickets) in enumerate(top_wickets.items(), 1):
            balls = len(df[df[bowler_col] == bowler])
            if runs_col:
                runs = df[df[bowler_col] == bowler][runs_col].sum()
                economy = (runs / (balls / 6)) if balls > 0 else 0
                logger.info(f"  {idx:2d}. {bowler:<30} {int(wickets):3d} wickets (Econ: {economy:.2f})")
            else:
                logger.info(f"  {idx:2d}. {bowler:<30} {int(wickets):3d} wickets")
    
    # Extras
    extras_cols = ['wides', 'noballs', 'legbyes', 'byes', 'penalty']
    logger.info(f"\n📊 Extras Analysis:")
    for col in extras_cols:
        if col in df.columns:
            count = df[col].sum()
            logger.info(f"  - {col.capitalize()}: {int(count):,}")


def analyze_teams(df):
    """Analyze team data"""
    logger.info(f"\n" + "="*70)
    logger.info("🏏 TEAM ANALYSIS")
    logger.info("="*70)
    
    batting_team_col = next((col for col in ['BattingTeam', 'batting_team'] if col in df.columns), None)
    
    if batting_team_col:
        teams = sorted(df[batting_team_col].unique())
        logger.info(f"\n📋 Teams:")
        logger.info(f"  - Unique teams: {len(teams)}")
        logger.info(f"  - Teams: {', '.join(teams)}")
        
        logger.info(f"\n📊 Deliveries faced by team:")
        team_balls = df[batting_team_col].value_counts().sort_values(ascending=False).head(10)
        for team, balls in team_balls.items():
            logger.info(f"  - {team:<35} {balls:,} deliveries")


def data_quality_check(df):
    """Check data quality"""
    logger.info(f"\n" + "="*70)
    logger.info("✅ DATA QUALITY CHECK")
    logger.info("="*70)
    
    logger.info(f"\n📋 Missing Data:")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    
    if len(missing) > 0:
        for col, count in missing.items():
            pct = (count / len(df)) * 100
            logger.info(f"  - {col:<30} {count:,} missing ({pct:.2f}%)")
    else:
        logger.info(f"  ✅ No missing values!")
    
    logger.info(f"\n📊 Data Types:")
    for col in df.columns:
        logger.info(f"  - {col:<30} {str(df[col].dtype)}")


def main():
    """Main execution"""
    df = load_ball_data()
    if df is None:
        return
    
    analyze_structure(df)
    analyze_batting(df)
    analyze_bowling(df)
    analyze_teams(df)
    data_quality_check(df)
    
    logger.info(f"\n" + "="*70)
    logger.info("🎉 BALL-BY-BALL ANALYSIS COMPLETE!")
    logger.info("="*70)
    logger.info(f"\n📊 Summary:")
    logger.info(f"  - Total deliveries: {len(df):,}")
    logger.info(f"  - Can be used for:")
    logger.info(f"    • Detailed player statistics")
    logger.info(f"    • Over-by-over analysis")
    logger.info(f"    • Scoring patterns")
    logger.info(f"    • Bowling analysis")
    logger.info(f"    • Partnership analysis")


if __name__ == "__main__":
    main()