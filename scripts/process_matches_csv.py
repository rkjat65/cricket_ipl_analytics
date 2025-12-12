"""
Process Kaggle IPL matches.csv
Converts matches.csv to clean year-wise match data with all parameters
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Paths
MATCHES_FILE = Path("data/raw/ipl_2024/matches.csv")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Expected match counts for validation
EXPECTED_COUNTS = {
    '2008': 59, '2009': 59, '2010': 60, '2011': 74, '2012': 76,
    '2013': 76, '2014': 60, '2015': 60, '2016': 60, '2017': 60,
    '2018': 60, '2019': 60, '2020': 60, '2021': 60, '2022': 74,
    '2023': 74, '2024': 74
}


def load_matches_csv() -> pd.DataFrame:
    """Load matches.csv file"""
    logger.info("Loading matches.csv...")
    
    if not MATCHES_FILE.exists():
        logger.error(f"File not found: {MATCHES_FILE}")
        logger.info("Expected location: data/raw/ipl_2024/matches.csv")
        return None
    
    try:
        df = pd.read_csv(MATCHES_FILE)
        logger.info(f"✅ Loaded {len(df)} matches")
        logger.info(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"Failed to load file: {e}")
        return None


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names and data types"""
    logger.info("\n🔧 Standardizing data...")
    
    # Column name mapping (common variations)
    column_mapping = {
        'id': 'match_id',
        'Season': 'season',
        'Date': 'date',
        'Team1': 'team1',
        'Team2': 'team2',
        'Venue': 'venue',
        'City': 'city',
        'TossWinner': 'toss_winner',
        'TossDecision': 'toss_decision',
        'Winner': 'winner',
        'WonBy': 'result_margin',
        'Margin': 'result_margin',
        'Player_of_Match': 'player_of_match',
        'PlayerOfMatch': 'player_of_match',
        'Umpire1': 'umpire1',
        'Umpire2': 'umpire2'
    }
    
    # Rename columns if they exist
    df = df.rename(columns=column_mapping)
    
    # Ensure critical columns exist
    required_columns = ['match_id', 'season', 'date', 'team1', 'team2', 'venue', 'winner']
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        logger.warning(f"⚠️ Missing columns: {missing}")
        # Try to infer from alternative names
        for col in missing:
            if col == 'match_id' and 'id' in df.columns:
                df['match_id'] = df['id']
    
    # Convert season to string
    if 'season' in df.columns:
        df['season'] = df['season'].astype(str)
        # Handle formats like "2007/08" -> "2008"
        df['season'] = df['season'].apply(lambda x: x.split('/')[-1] if '/' in str(x) else str(x))
    
    # Convert date to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['match_date'] = df['date']
    
    # Add tournament info
    df['tournament'] = 'Indian Premier League'
    df['tournament_type'] = 'ipl'
    df['match_type'] = 'T20'
    
    # Calculate result margin and type
    if 'result' in df.columns and 'result_margin' not in df.columns:
        # Extract margin from result string
        def extract_margin(result_str):
            if pd.isna(result_str) or result_str == '':
                return 'unknown', 0
            result_str = str(result_str).lower()
            if 'run' in result_str:
                try:
                    margin = int(''.join(filter(str.isdigit, result_str.split('run')[0])))
                    return 'runs', margin
                except:
                    return 'runs', 0
            elif 'wicket' in result_str:
                try:
                    margin = int(''.join(filter(str.isdigit, result_str.split('wicket')[0])))
                    return 'wickets', margin
                except:
                    return 'wickets', 0
            elif 'tie' in result_str:
                return 'tie', 0
            else:
                return 'unknown', 0
        
        df[['margin_type', 'margin_value']] = df['result'].apply(
            lambda x: pd.Series(extract_margin(x))
        )
    
    # Fill missing values
    if 'margin_type' not in df.columns:
        df['margin_type'] = 'unknown'
    if 'margin_value' not in df.columns:
        df['margin_value'] = 0
    
    logger.info(f"✅ Standardized {len(df)} matches")
    
    return df


def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate data and remove duplicates"""
    logger.info("\n🔍 Validating data...")
    
    # Remove duplicates based on match signature
    initial_count = len(df)
    
    df['match_signature'] = (
        df['date'].astype(str) + '|' +
        df[['team1', 'team2']].apply(
            lambda x: '|'.join(sorted([str(x['team1']), str(x['team2'])])),
            axis=1
        ) + '|' +
        df['venue'].astype(str)
    )
    
    df = df.drop_duplicates(subset='match_signature', keep='first')
    duplicates_removed = initial_count - len(df)
    
    if duplicates_removed > 0:
        logger.info(f"⚠️ Removed {duplicates_removed} duplicate matches")
    else:
        logger.info(f"✅ No duplicates found")
    
    df = df.drop('match_signature', axis=1)
    
    # Validate seasons
    if 'season' in df.columns:
        seasons = sorted(df['season'].unique())
        logger.info(f"Seasons found: {seasons}")
        
        # Remove any non-IPL years or future years
        df = df[df['season'].isin(EXPECTED_COUNTS.keys())]
        logger.info(f"After filtering valid seasons: {len(df)} matches")
    
    return df


def save_year_wise_data(df: pd.DataFrame):
    """Save data year-wise and combined"""
    logger.info("\n💾 Saving year-wise CSV files...")
    
    # Ensure season is string
    df['season'] = df['season'].astype(str)
    
    # Get seasons
    seasons = sorted(df['season'].unique())
    
    # Validation summary
    logger.info(f"\n📊 Match Count Validation:")
    logger.info(f"{'Season':<10} {'Actual':<10} {'Expected':<10} {'Diff':<10} {'Status'}")
    logger.info("-" * 60)
    
    total_actual = 0
    total_expected = 0
    
    for season in sorted(EXPECTED_COUNTS.keys()):
        expected = EXPECTED_COUNTS.get(season, 0)
        actual = len(df[df['season'] == season])
        diff = actual - expected
        
        total_actual += actual
        total_expected += expected
        
        if actual == expected:
            status = '✅'
        elif actual == 0:
            status = '❌ MISSING'
        elif abs(diff) <= 3:
            status = '⚠️ Close'
        else:
            status = '❌ Off'
        
        if actual > 0:
            logger.info(f"{season:<10} {actual:<10} {expected:<10} {diff:+<10} {status}")
    
    logger.info("-" * 60)
    logger.info(f"{'TOTAL':<10} {total_actual:<10} {total_expected:<10} {total_actual-total_expected:+<10}")
    
    completeness = (total_actual / total_expected * 100) if total_expected > 0 else 0
    logger.info(f"\n📈 Data Completeness: {completeness:.1f}%")
    
    # Save year-wise files
    logger.info(f"\n💾 Saving individual year files...")
    for season in seasons:
        season_data = df[df['season'] == season]
        if len(season_data) > 0:
            output_file = PROCESSED_DIR / f"ipl_{season}_matches.csv"
            season_data.to_csv(output_file, index=False)
            logger.info(f"  ✅ Saved: {output_file.name} ({len(season_data)} matches)")
    
    # Save combined file
    combined_file = PROCESSED_DIR / "ipl_all_years_combined.csv"
    df.to_csv(combined_file, index=False)
    logger.info(f"\n✅ Saved combined: {combined_file.name} ({len(df)} matches)")
    
    return seasons


def generate_summary_stats(df: pd.DataFrame):
    """Generate comprehensive summary statistics"""
    logger.info("\n" + "="*60)
    logger.info("📊 DATA SUMMARY STATISTICS")
    logger.info("="*60)
    
    # Basic stats
    logger.info(f"\n📈 Overall Statistics:")
    logger.info(f"  - Total matches: {len(df)}")
    logger.info(f"  - Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    logger.info(f"  - Seasons: {df['season'].nunique()}")
    
    # Matches by season
    logger.info(f"\n📅 Matches by Season:")
    season_counts = df['season'].value_counts().sort_index()
    for season, count in season_counts.items():
        logger.info(f"  - {season}: {count} matches")
    
    # Venue stats
    logger.info(f"\n🏟️ Venue Statistics:")
    logger.info(f"  - Unique venues: {df['venue'].nunique()}")
    top_venues = df['venue'].value_counts().head(5)
    logger.info(f"  - Top 5 venues:")
    for venue, count in top_venues.items():
        logger.info(f"    • {venue}: {count} matches")
    
    # Team stats
    all_teams = pd.concat([df['team1'], df['team2']]).unique()
    logger.info(f"\n🏏 Teams:")
    logger.info(f"  - Unique teams: {len(all_teams)}")
    
    # Winner stats
    if 'winner' in df.columns:
        winners = df[df['winner'].notna()]['winner'].value_counts()
        logger.info(f"\n🏆 Top 10 Winners (All Time):")
        for idx, (team, wins) in enumerate(winners.head(10).items(), 1):
            total_matches = len(df[(df['team1'] == team) | (df['team2'] == team)])
            win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
            logger.info(f"  {idx}. {team}: {wins} wins ({win_rate:.1f}% win rate)")
    
    # Toss impact
    if 'toss_winner' in df.columns and 'winner' in df.columns:
        toss_wins = df[df['toss_winner'] == df['winner']]
        toss_impact = len(toss_wins) / len(df) * 100
        logger.info(f"\n🪙 Toss Impact:")
        logger.info(f"  - Toss winner won match: {len(toss_wins)}/{len(df)} ({toss_impact:.1f}%)")
    
    # Data completeness
    logger.info(f"\n⚠️ Data Completeness:")
    critical_cols = ['date', 'team1', 'team2', 'venue', 'winner', 'toss_winner']
    
    all_complete = True
    for col in critical_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                pct = (missing / len(df)) * 100
                logger.info(f"  - {col}: {missing} missing ({pct:.1f}%)")
                all_complete = False
    
    if all_complete:
        logger.info(f"  ✅ All critical fields complete!")


def main():
    """Main processing pipeline"""
    logger.info("\n" + "="*60)
    logger.info("🏏 IPL MATCHES.CSV PROCESSOR")
    logger.info("="*60)
    
    # Load data
    df = load_matches_csv()
    if df is None:
        return
    
    # Standardize
    df = standardize_columns(df)
    
    # Validate and clean
    df = validate_and_clean(df)
    
    # Save year-wise
    seasons = save_year_wise_data(df)
    
    # Generate stats
    generate_summary_stats(df)
    
    logger.info("\n" + "="*60)
    logger.info("✅ PROCESSING COMPLETE!")
    logger.info("="*60)
    logger.info(f"\n📁 Output: {PROCESSED_DIR}")
    logger.info(f"📊 Seasons: {', '.join(seasons)}")
    logger.info(f"📈 Total: {len(df)} matches")
    
    logger.info("\n🎯 Next steps:")
    logger.info("  1. Add 2025 data: python scripts/add_2025_data.py")
    logger.info("  2. Run quality check: python scripts/check_data_quality.py")
    logger.info("  3. Load into database")


if __name__ == "__main__":
    main()