"""
Quick Data Explorer
Analyzes processed IPL and T20 World Cup CSV files
Shows summary statistics and insights
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")


def explore_csv_file(csv_path: Path):
    """Explore a single CSV file and show key statistics"""
    
    if not csv_path.exists():
        logger.warning(f"❌ File not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 {csv_path.name}")
    logger.info(f"{'='*60}")
    
    logger.info(f"\n📈 Basic Stats:")
    logger.info(f"  - Total matches: {len(df)}")
    logger.info(f"  - Columns: {len(df.columns)}")
    logger.info(f"  - Date range: {df['match_date'].min()} to {df['match_date'].max()}")
    
    if 'year' in df.columns:
        logger.info(f"  - Years: {sorted(df['year'].unique().tolist())}")
    
    # Venues
    if 'venue' in df.columns:
        top_venues = df['venue'].value_counts().head(5)
        logger.info(f"\n🏟️ Top 5 Venues:")
        for venue, count in top_venues.items():
            logger.info(f"  - {venue}: {count} matches")
    
    # Teams
    if 'team1' in df.columns and 'team2' in df.columns:
        all_teams = set(df['team1'].tolist() + df['team2'].tolist())
        logger.info(f"\n🏏 Teams: {len(all_teams)} unique teams")
    
    # Winners
    if 'winner' in df.columns:
        winners = df[df['winner'] != '']['winner'].value_counts().head(10)
        logger.info(f"\n🏆 Top Winners:")
        for idx, (team, wins) in enumerate(winners.items(), 1):
            total_matches = len(df[(df['team1'] == team) | (df['team2'] == team)])
            win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
            logger.info(f"  {idx}. {team}: {wins} wins ({win_rate:.1f}% win rate)")
    
    # Toss impact
    if 'toss_winner' in df.columns and 'winner' in df.columns:
        toss_wins = df[df['toss_winner'] == df['winner']]
        toss_impact = len(toss_wins) / len(df) * 100
        logger.info(f"\n🪙 Toss Impact:")
        logger.info(f"  - Toss winner also won match: {len(toss_wins)}/{len(df)} ({toss_impact:.1f}%)")
    
    # Margin analysis
    if 'margin_type' in df.columns and 'margin_value' in df.columns:
        runs_wins = df[df['margin_type'] == 'runs']
        wickets_wins = df[df['margin_type'] == 'wickets']
        
        logger.info(f"\n📊 Winning Margins:")
        logger.info(f"  - By runs: {len(runs_wins)} matches")
        if len(runs_wins) > 0:
            logger.info(f"    Average margin: {runs_wins['margin_value'].mean():.1f} runs")
        logger.info(f"  - By wickets: {len(wickets_wins)} matches")
        if len(wickets_wins) > 0:
            logger.info(f"    Average margin: {wickets_wins['margin_value'].mean():.1f} wickets")
    
    # Missing data
    logger.info(f"\n⚠️ Data Quality:")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        logger.info(f"  Columns with missing values:")
        for col, count in missing.items():
            pct = count / len(df) * 100
            logger.info(f"  - {col}: {count} ({pct:.1f}%)")
    else:
        logger.info(f"  ✅ No missing values!")


def compare_tournaments():
    """Compare IPL vs T20 World Cup"""
    
    ipl_combined = PROCESSED_DIR / "ipl_all_years_combined.csv"
    t20_combined = PROCESSED_DIR / "t20wc_all_years_combined.csv"
    
    if not ipl_combined.exists() or not t20_combined.exists():
        logger.warning("Combined files not found. Run process_all_cricket_data.py first.")
        return
    
    ipl_df = pd.read_csv(ipl_combined)
    t20_df = pd.read_csv(t20_combined)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🏏 IPL vs T20 World Cup Comparison")
    logger.info(f"{'='*60}")
    
    logger.info(f"\n📊 Dataset Size:")
    logger.info(f"  IPL: {len(ipl_df)} matches")
    logger.info(f"  T20 WC: {len(t20_df)} matches")
    
    logger.info(f"\n📅 Time Span:")
    logger.info(f"  IPL: {ipl_df['match_date'].min()} to {ipl_df['match_date'].max()}")
    logger.info(f"  T20 WC: {t20_df['match_date'].min()} to {t20_df['match_date'].max()}")
    
    logger.info(f"\n🏏 Teams:")
    ipl_teams = set(ipl_df['team1'].tolist() + ipl_df['team2'].tolist())
    t20_teams = set(t20_df['team1'].tolist() + t20_df['team2'].tolist())
    logger.info(f"  IPL: {len(ipl_teams)} teams")
    logger.info(f"  T20 WC: {len(t20_teams)} teams")
    
    # Most successful teams
    logger.info(f"\n🏆 Most Successful:")
    ipl_champ = ipl_df['winner'].value_counts().index[0]
    ipl_wins = ipl_df['winner'].value_counts().iloc[0]
    logger.info(f"  IPL: {ipl_champ} ({ipl_wins} wins)")
    
    t20_champ = t20_df['winner'].value_counts().index[0]
    t20_wins = t20_df['winner'].value_counts().iloc[0]
    logger.info(f"  T20 WC: {t20_champ} ({t20_wins} wins)")


def main():
    """Main exploration function"""
    
    logger.info("\n" + "="*60)
    logger.info("🔍 CRICKET DATA EXPLORER")
    logger.info("="*60)
    
    if not PROCESSED_DIR.exists():
        logger.error(f"❌ Processed directory not found: {PROCESSED_DIR}")
        logger.info("Please run process_all_cricket_data.py first!")
        return
    
    csv_files = list(PROCESSED_DIR.glob("*.csv"))
    
    if len(csv_files) == 0:
        logger.error(f"❌ No CSV files found in {PROCESSED_DIR}")
        logger.info("Please run process_all_cricket_data.py first!")
        return
    
    logger.info(f"\nFound {len(csv_files)} CSV files\n")
    
    # Explore combined files first
    ipl_combined = PROCESSED_DIR / "ipl_all_years_combined.csv"
    t20_combined = PROCESSED_DIR / "t20wc_all_years_combined.csv"
    
    if ipl_combined.exists():
        explore_csv_file(ipl_combined)
    
    if t20_combined.exists():
        explore_csv_file(t20_combined)
    
    # Compare tournaments
    if ipl_combined.exists() and t20_combined.exists():
        compare_tournaments()
    
    # Show available year-wise files
    logger.info(f"\n{'='*60}")
    logger.info("📁 Available Year-wise Files:")
    logger.info(f"{'='*60}")
    
    ipl_yearly = sorted([f for f in csv_files if 'ipl' in f.name and 'combined' not in f.name])
    t20_yearly = sorted([f for f in csv_files if 't20wc' in f.name and 'combined' not in f.name])
    
    if ipl_yearly:
        logger.info(f"\n🏏 IPL Year-wise ({len(ipl_yearly)} files):")
        for f in ipl_yearly:
            logger.info(f"  - {f.name}")
    
    if t20_yearly:
        logger.info(f"\n🌍 T20 WC Year-wise ({len(t20_yearly)} files):")
        for f in t20_yearly:
            logger.info(f"  - {f.name}")
    
    logger.info(f"\n{'='*60}")
    logger.info("✅ Exploration Complete!")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()