"""
Complete IPL Data Processor (2008-2025)
Processes all_ipl_matches_data.csv with comprehensive quality checks
Creates year-wise files and validates completeness
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Paths
MATCHES_FILE = Path("data/raw/ipl_2024/all_ipl_matches_data.csv")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Expected counts
EXPECTED_COUNTS = {
    '2008': 59, '2009': 59, '2010': 60, '2011': 74, '2012': 76,
    '2013': 76, '2014': 60, '2015': 60, '2016': 60, '2017': 60,
    '2018': 60, '2019': 60, '2020': 60, '2021': 60, '2022': 74,
    '2023': 74, '2024': 74, '2025': 74
}


def load_and_explore_data():
    """Load matches file and explore structure"""
    logger.info("\n" + "="*70)
    logger.info("🏏 COMPLETE IPL DATA PROCESSOR (2008-2025)")
    logger.info("="*70)
    
    logger.info(f"\n📂 Loading: {MATCHES_FILE}")
    
    if not MATCHES_FILE.exists():
        logger.error(f"❌ File not found: {MATCHES_FILE}")
        logger.info("Please ensure file is at: data/raw/ipl_2024/all_ipl_matches_data.csv")
        return None
    
    # Load data
    df = pd.read_csv(MATCHES_FILE)
    
    logger.info(f"✅ Loaded successfully!")
    logger.info(f"\n📊 Initial Data Exploration:")
    logger.info(f"  - Total rows: {len(df):,}")
    logger.info(f"  - Total columns: {len(df.columns)}")
    logger.info(f"\n📋 Column names:")
    for i, col in enumerate(df.columns, 1):
        logger.info(f"  {i:2d}. {col}")
    
    # Basic info
    logger.info(f"\n📈 Data types:")
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        logger.info(f"  - {col:<30} {str(dtype):<15} (null: {null_count}, {null_count/len(df)*100:.1f}%)")
    
    return df


def standardize_columns(df):
    """Standardize column names and data"""
    logger.info(f"\n🔧 Standardizing data...")
    
    # Common column mappings
    column_mapping = {
        'ID': 'match_id',
        'id': 'match_id',
        'Season': 'season',
        'City': 'city', 
        'Date': 'date',
        'MatchNumber': 'match_number',
        'Team1': 'team1',
        'Team2': 'team2',
        'Venue': 'venue',
        'TossWinner': 'toss_winner',
        'TossDecision': 'toss_decision',
        'SuperOver': 'super_over',
        'WinningTeam': 'winner',
        'Winner': 'winner',
        'WonBy': 'margin_type',
        'Margin': 'margin_value',
        'method': 'dl_applied',
        'Player_of_Match': 'player_of_match',
        'Team1Players': 'team1_players',
        'Team2Players': 'team2_players',
        'Umpire1': 'umpire1',
        'Umpire2': 'umpire2'
    }
    
    # Rename
    df = df.rename(columns=column_mapping)
    
    # Standardize season
    if 'season' in df.columns:
        df['season'] = df['season'].astype(str)
        # Handle "2007/08" format
        df['season'] = df['season'].apply(lambda x: x.split('/')[-1] if '/' in str(x) else str(x))
    
    # Parse dates
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['match_date'] = df['date']
    
    # Add metadata
    df['tournament'] = 'Indian Premier League'
    df['tournament_type'] = 'ipl'
    df['match_type'] = 'T20'
    
    logger.info(f"✅ Standardized {len(df)} matches")
    
    return df


def clean_and_validate(df):
    """Clean data and remove duplicates"""
    logger.info(f"\n🧹 Cleaning and validating...")
    
    initial_count = len(df)
    
    # Remove duplicates
    df['match_signature'] = (
        df['date'].astype(str) + '|' +
        df[['team1', 'team2']].apply(
            lambda x: '|'.join(sorted([str(x['team1']), str(x['team2'])])),
            axis=1
        )
    )
    
    df = df.drop_duplicates(subset='match_signature', keep='first')
    duplicates = initial_count - len(df)
    
    if duplicates > 0:
        logger.info(f"  ⚠️ Removed {duplicates} duplicate matches")
    else:
        logger.info(f"  ✅ No duplicates found")
    
    df = df.drop('match_signature', axis=1)
    
    # Validate seasons
    valid_seasons = list(EXPECTED_COUNTS.keys())
    if 'season' in df.columns:
        before = len(df)
        df = df[df['season'].isin(valid_seasons)]
        removed = before - len(df)
        if removed > 0:
            logger.info(f"  ⚠️ Removed {removed} matches from invalid seasons")
    
    logger.info(f"✅ Clean dataset: {len(df)} matches")
    
    return df


def validate_match_counts(df):
    """Validate match counts against expected"""
    logger.info(f"\n" + "="*70)
    logger.info("📊 MATCH COUNT VALIDATION")
    logger.info("="*70)
    
    logger.info(f"\n{'Season':<10} {'Actual':<10} {'Expected':<10} {'Diff':<10} {'Status':<15} {'%':<10}")
    logger.info("-" * 70)
    
    total_actual = 0
    total_expected = 0
    complete_seasons = []
    close_seasons = []
    missing_seasons = []
    
    for season in sorted(EXPECTED_COUNTS.keys()):
        expected = EXPECTED_COUNTS[season]
        actual = len(df[df['season'] == season])
        diff = actual - expected
        pct = (actual / expected * 100) if expected > 0 else 0
        
        total_actual += actual
        total_expected += expected
        
        if actual == expected:
            status = '✅ Perfect'
            complete_seasons.append(season)
        elif actual == 0:
            status = '❌ MISSING'
            missing_seasons.append(season)
        elif abs(diff) <= 3:
            status = '⚠️ Close'
            close_seasons.append(season)
        else:
            status = '❌ Off'
            missing_seasons.append(season)
        
        logger.info(f"{season:<10} {actual:<10} {expected:<10} {diff:+<10} {status:<15} {pct:.1f}%")
    
    logger.info("-" * 70)
    logger.info(f"{'TOTAL':<10} {total_actual:<10} {total_expected:<10} {total_actual-total_expected:+<10}")
    
    completeness = (total_actual / total_expected * 100) if total_expected > 0 else 0
    
    logger.info(f"\n📈 Overall Completeness: {completeness:.1f}%")
    logger.info(f"  - Complete seasons: {len(complete_seasons)}/18")
    logger.info(f"  - Close (±3): {len(close_seasons)} seasons")
    logger.info(f"  - Missing/Off: {len(missing_seasons)} seasons")
    
    if missing_seasons:
        logger.info(f"\n⚠️ Problematic seasons: {', '.join(missing_seasons)}")
    
    return completeness


def analyze_data_quality(df):
    """Comprehensive data quality analysis"""
    logger.info(f"\n" + "="*70)
    logger.info("🔍 DATA QUALITY ANALYSIS")
    logger.info("="*70)
    
    # Missing data
    logger.info(f"\n📋 Missing Data Analysis:")
    critical_cols = ['season', 'date', 'team1', 'team2', 'venue', 'winner', 'toss_winner', 'toss_decision']
    
    all_complete = True
    for col in critical_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            pct = (missing / len(df)) * 100
            
            if missing == 0:
                logger.info(f"  ✅ {col:<20} Complete")
            elif pct < 1:
                logger.info(f"  ⚠️ {col:<20} {missing:4d} missing ({pct:.1f}%)")
            else:
                logger.info(f"  ❌ {col:<20} {missing:4d} missing ({pct:.1f}%)")
                all_complete = False
        else:
            logger.info(f"  ❌ {col:<20} Column not found")
    
    # Date range
    logger.info(f"\n📅 Date Range:")
    if 'date' in df.columns:
        logger.info(f"  - First match: {df['date'].min().date()}")
        logger.info(f"  - Last match: {df['date'].max().date()}")
        logger.info(f"  - Span: {(df['date'].max() - df['date'].min()).days} days")
    
    # Teams
    logger.info(f"\n🏏 Teams Analysis:")
    if 'team1' in df.columns and 'team2' in df.columns:
        all_teams = sorted(set(df['team1'].tolist() + df['team2'].tolist()))
        logger.info(f"  - Unique teams: {len(all_teams)}")
        logger.info(f"  - Teams: {', '.join(all_teams)}")
    
    # Venues
    logger.info(f"\n🏟️ Venues:")
    if 'venue' in df.columns:
        logger.info(f"  - Unique venues: {df['venue'].nunique()}")
        top_venues = df['venue'].value_counts().head(5)
        logger.info(f"  - Top 5:")
        for venue, count in top_venues.items():
            logger.info(f"    • {venue}: {count} matches")
    
    return all_complete


def generate_statistics(df):
    """Generate comprehensive statistics"""
    logger.info(f"\n" + "="*70)
    logger.info("📊 COMPREHENSIVE STATISTICS")
    logger.info("="*70)
    
    # Winners
    if 'winner' in df.columns:
        winners = df[df['winner'].notna()]['winner'].value_counts()
        logger.info(f"\n🏆 Top 10 Most Successful Teams:")
        for idx, (team, wins) in enumerate(winners.head(10).items(), 1):
            total_matches = len(df[(df['team1'] == team) | (df['team2'] == team)])
            win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
            logger.info(f"  {idx:2d}. {team:<35} {wins:3d} wins ({win_rate:.1f}% win rate)")
    
    # Toss impact
    if 'toss_winner' in df.columns and 'winner' in df.columns:
        toss_wins = df[df['toss_winner'] == df['winner']]
        total_decided = len(df[df['winner'].notna()])
        toss_impact = (len(toss_wins) / total_decided * 100) if total_decided > 0 else 0
        logger.info(f"\n🪙 Toss Impact:")
        logger.info(f"  - Toss winner won match: {len(toss_wins)}/{total_decided} ({toss_impact:.1f}%)")
    
    # Bat/Field decision
    if 'toss_decision' in df.columns:
        decisions = df['toss_decision'].value_counts()
        logger.info(f"\n🎯 Toss Decisions:")
        for decision, count in decisions.items():
            pct = (count / len(df)) * 100
            logger.info(f"  - {decision}: {count} ({pct:.1f}%)")
    
    # Season-wise stats
    logger.info(f"\n📅 Matches by Season:")
    season_counts = df['season'].value_counts().sort_index()
    for season, count in season_counts.items():
        logger.info(f"  - {season}: {count} matches")


def save_year_wise_files(df):
    """Save year-wise CSV files"""
    logger.info(f"\n💾 Saving year-wise files...")
    
    df['season'] = df['season'].astype(str)
    seasons = sorted(df['season'].unique())
    
    saved_files = []
    for season in seasons:
        season_data = df[df['season'] == season]
        output_file = PROCESSED_DIR / f"ipl_{season}_matches.csv"
        season_data.to_csv(output_file, index=False)
        saved_files.append((season, len(season_data)))
        logger.info(f"  ✅ Saved: ipl_{season}_matches.csv ({len(season_data)} matches)")
    
    # Save combined
    combined_file = PROCESSED_DIR / "ipl_all_years_combined.csv"
    df.to_csv(combined_file, index=False)
    logger.info(f"\n✅ Saved combined: {combined_file.name} ({len(df)} matches)")
    
    return saved_files


def generate_final_report(df, completeness):
    """Generate final quality report"""
    logger.info(f"\n" + "="*70)
    logger.info("📋 FINAL DATA QUALITY REPORT")
    logger.info("="*70)
    
    logger.info(f"\n📊 Dataset Overview:")
    logger.info(f"  - Total matches: {len(df):,}")
    logger.info(f"  - Seasons covered: {df['season'].nunique()}")
    logger.info(f"  - Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    logger.info(f"  - Unique teams: {len(set(df['team1'].tolist() + df['team2'].tolist()))}")
    logger.info(f"  - Unique venues: {df['venue'].nunique()}")
    
    logger.info(f"\n📈 Quality Metrics:")
    logger.info(f"  - Completeness: {completeness:.1f}%")
    
    # Data density
    non_null = df.notna().sum().sum()
    total_cells = len(df) * len(df.columns)
    density = (non_null / total_cells * 100)
    logger.info(f"  - Data density: {density:.1f}%")
    
    # Grade
    if completeness >= 98 and density >= 95:
        grade = "A+ (Excellent)"
    elif completeness >= 95 and density >= 90:
        grade = "A (Very Good)"
    elif completeness >= 90 and density >= 85:
        grade = "B (Good)"
    elif completeness >= 85:
        grade = "C (Fair)"
    else:
        grade = "D (Needs Improvement)"
    
    logger.info(f"\n🎯 Overall Grade: {grade}")
    
    logger.info(f"\n✅ Files saved to: {PROCESSED_DIR}")
    logger.info(f"\n🎯 Next Steps:")
    logger.info(f"  1. Review data in: {PROCESSED_DIR}")
    logger.info(f"  2. Check individual year files")
    logger.info(f"  3. Load into database")
    logger.info(f"  4. Start building dashboards!")
    
    return grade


def main():
    """Main execution"""
    # Load and explore
    df = load_and_explore_data()
    if df is None:
        return
    
    # Standardize
    df = standardize_columns(df)
    
    # Clean
    df = clean_and_validate(df)
    
    # Validate counts
    completeness = validate_match_counts(df)
    
    # Quality analysis
    analyze_data_quality(df)
    
    # Statistics
    generate_statistics(df)
    
    # Save files
    save_year_wise_files(df)
    
    # Final report
    grade = generate_final_report(df, completeness)
    
    logger.info(f"\n" + "="*70)
    logger.info(f"🎉 PROCESSING COMPLETE!")
    logger.info(f"="*70)


if __name__ == "__main__":
    main()