"""
Process Complete IPL Matches Data (2008-2025)
Handles data with team IDs and specific column structure
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

MATCHES_FILE = Path("data/raw/ipl_2024/all_ipl_matches_data.csv")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_COUNTS = {
    '2008': 59, '2009': 59, '2010': 60, '2011': 74, '2012': 76,
    '2013': 76, '2014': 60, '2015': 60, '2016': 60, '2017': 60,
    '2018': 60, '2019': 60, '2020': 60, '2021': 60, '2022': 74,
    '2023': 74, '2024': 74, '2025': 74
}


def load_data():
    """Load the matches data"""
    logger.info("\n" + "="*70)
    logger.info("🏏 IPL COMPLETE DATA PROCESSOR (2008-2025)")
    logger.info("="*70)
    
    logger.info(f"\n📂 Loading: {MATCHES_FILE}")
    
    if not MATCHES_FILE.exists():
        logger.error(f"❌ File not found!")
        return None
    
    df = pd.read_csv(MATCHES_FILE)
    
    logger.info(f"✅ Loaded {len(df):,} matches")
    logger.info(f"📊 Columns: {len(df.columns)}")
    
    # Show structure
    logger.info(f"\n📋 Data Structure:")
    logger.info(f"  - match_id: {df['match_id'].dtype}")
    logger.info(f"  - season: {df['season'].dtype}")
    logger.info(f"  - match_date: {df['match_date'].dtype}")
    logger.info(f"  - team1/team2: {df['team1'].dtype} (appear to be IDs)")
    logger.info(f"  - venue: {df['venue'].dtype}")
    
    return df


def clean_data(df):
    """Clean and prepare data"""
    logger.info(f"\n🧹 Cleaning data...")
    
    # Convert season to string
    df['season'] = df['season'].astype(str)
    
    # Parse dates
    df['match_date'] = pd.to_datetime(df['match_date'], errors='coerce')
    
    # Remove duplicates based on match_id
    initial = len(df)
    df = df.drop_duplicates(subset='match_id', keep='first')
    removed = initial - len(df)
    
    if removed > 0:
        logger.info(f"  ⚠️ Removed {removed} duplicate match_ids")
    else:
        logger.info(f"  ✅ No duplicates found")
    
    # Filter valid seasons only
    valid_seasons = list(EXPECTED_COUNTS.keys())
    before = len(df)
    df = df[df['season'].isin(valid_seasons)]
    filtered = before - len(df)
    
    if filtered > 0:
        logger.info(f"  ⚠️ Filtered {filtered} matches from invalid seasons")
    
    logger.info(f"✅ Clean dataset: {len(df)} matches")
    
    return df


def validate_counts(df):
    """Validate match counts"""
    logger.info(f"\n" + "="*70)
    logger.info("📊 MATCH COUNT VALIDATION")
    logger.info("="*70)
    
    logger.info(f"\n{'Season':<10} {'Actual':<10} {'Expected':<10} {'Diff':<10} {'Status':<15} {'%'}")
    logger.info("-" * 70)
    
    total_actual = 0
    total_expected = 0
    complete_seasons = []
    issues = []
    
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
            issues.append(f"{season}: NO DATA")
        elif abs(diff) <= 3:
            status = '⚠️ Close'
        else:
            status = '❌ Off'
            issues.append(f"{season}: {actual}/{expected}")
        
        if actual > 0 or expected > 0:
            logger.info(f"{season:<10} {actual:<10} {expected:<10} {diff:+<10} {status:<15} {pct:.1f}%")
    
    logger.info("-" * 70)
    logger.info(f"{'TOTAL':<10} {total_actual:<10} {total_expected:<10} {total_actual-total_expected:+<10}")
    
    completeness = (total_actual / total_expected * 100) if total_expected > 0 else 0
    logger.info(f"\n📈 Data Completeness: {completeness:.1f}%")
    logger.info(f"✅ Complete seasons: {len(complete_seasons)}/18")
    
    if issues:
        logger.info(f"\n⚠️ Issues: {', '.join(issues)}")
    
    return completeness


def analyze_quality(df):
    """Analyze data quality"""
    logger.info(f"\n" + "="*70)
    logger.info("🔍 DATA QUALITY ANALYSIS")
    logger.info("="*70)
    
    # Missing data
    logger.info(f"\n📋 Missing Values:")
    missing_cols = ['city', 'match_number', 'win_by_runs', 'win_by_wickets', 'player_of_match']
    
    for col in missing_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            pct = (missing / len(df)) * 100
            if missing > 0:
                logger.info(f"  - {col:<25} {missing:4d} missing ({pct:.1f}%)")
    
    # Date range
    logger.info(f"\n📅 Date Coverage:")
    logger.info(f"  - First match: {df['match_date'].min().date()}")
    logger.info(f"  - Last match: {df['match_date'].max().date()}")
    logger.info(f"  - Total days: {(df['match_date'].max() - df['match_date'].min()).days}")
    
    # Venues
    logger.info(f"\n🏟️ Venues:")
    logger.info(f"  - Unique venues: {df['venue'].nunique()}")
    top_venues = df['venue'].value_counts().head(5)
    logger.info(f"  - Top 5:")
    for venue, count in top_venues.items():
        logger.info(f"    • {venue}: {count} matches")
    
    # Team IDs note
    logger.info(f"\n⚠️ IMPORTANT NOTE:")
    logger.info(f"  - team1, team2, toss_winner, match_winner are stored as IDs")
    logger.info(f"  - Unique team IDs: {len(set(df['team1'].tolist() + df['team2'].tolist()))}")
    logger.info(f"  - You may need a separate teams reference table to map IDs to names")
    
    # Toss decisions
    logger.info(f"\n🪙 Toss Decisions:")
    decisions = df['toss_decision'].value_counts()
    for decision, count in decisions.items():
        pct = (count / len(df)) * 100
        logger.info(f"  - {decision}: {count} ({pct:.1f}%)")
    
    # Results
    logger.info(f"\n🏆 Match Results:")
    logger.info(f"  - Wins by runs: {df['win_by_runs'].notna().sum()}")
    logger.info(f"  - Wins by wickets: {df['win_by_wickets'].notna().sum()}")


def season_stats(df):
    """Generate season-wise statistics"""
    logger.info(f"\n" + "="*70)
    logger.info("📊 SEASON-WISE BREAKDOWN")
    logger.info("="*70)
    
    logger.info(f"\n{'Season':<10} {'Matches':<10} {'Venues':<10} {'Cities':<10} {'Avg Runs':<12} {'Avg Wkts'}")
    logger.info("-" * 70)
    
    for season in sorted(df['season'].unique()):
        season_df = df[df['season'] == season]
        matches = len(season_df)
        venues = season_df['venue'].nunique()
        cities = season_df['city'].nunique()
        
        # Calculate averages for winning margins
        avg_runs = season_df['win_by_runs'].mean()
        avg_wkts = season_df['win_by_wickets'].mean()
        
        logger.info(
            f"{season:<10} {matches:<10} {venues:<10} {cities:<10} "
            f"{avg_runs if pd.notna(avg_runs) else 0:<12.1f} "
            f"{avg_wkts if pd.notna(avg_wkts) else 0:.1f}"
        )


def save_files(df):
    """Save processed files"""
    logger.info(f"\n💾 Saving files...")
    
    # Year-wise
    for season in sorted(df['season'].unique()):
        season_df = df[df['season'] == season]
        output_file = PROCESSED_DIR / f"ipl_{season}_matches.csv"
        season_df.to_csv(output_file, index=False)
        logger.info(f"  ✅ Saved: ipl_{season}_matches.csv ({len(season_df)} matches)")
    
    # Combined
    combined_file = PROCESSED_DIR / "ipl_all_years_combined.csv"
    df.to_csv(combined_file, index=False)
    logger.info(f"\n✅ Combined file: {combined_file.name} ({len(df)} matches)")


def final_report(df, completeness):
    """Generate final report"""
    logger.info(f"\n" + "="*70)
    logger.info("📋 FINAL REPORT")
    logger.info("="*70)
    
    logger.info(f"\n📊 Summary:")
    logger.info(f"  - Total matches: {len(df):,}")
    logger.info(f"  - Seasons: {df['season'].nunique()} ({df['season'].min()} - {df['season'].max()})")
    logger.info(f"  - Completeness: {completeness:.1f}%")
    
    # Grade
    if completeness >= 98:
        grade = "A+ (Excellent)"
    elif completeness >= 95:
        grade = "A (Very Good)"
    elif completeness >= 90:
        grade = "B (Good)"
    elif completeness >= 85:
        grade = "C (Fair)"
    else:
        grade = "D (Needs Work)"
    
    logger.info(f"\n🎯 Grade: {grade}")
    
    logger.info(f"\n✅ Files saved to: {PROCESSED_DIR}/")
    
    logger.info(f"\n⚠️ NEXT STEPS:")
    logger.info(f"  1. You need a teams reference file to map team IDs to names")
    logger.info(f"  2. Check ball-by-ball data: python scripts/explore_ball_by_ball_data.py")
    logger.info(f"  3. Create team ID mapping")
    logger.info(f"  4. Then ready for database load!")


def main():
    """Main execution"""
    df = load_data()
    if df is None:
        return
    
    df = clean_data(df)
    completeness = validate_counts(df)
    analyze_quality(df)
    season_stats(df)
    save_files(df)
    final_report(df, completeness)
    
    logger.info(f"\n" + "="*70)
    logger.info("🎉 PROCESSING COMPLETE!")
    logger.info("="*70)


if __name__ == "__main__":
    main()