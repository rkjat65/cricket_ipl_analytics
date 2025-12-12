"""
IPL Data Quality Checker
Comprehensive validation of match data completeness and quality
Checks for missing matches, duplicates, anomalies, and data consistency
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")

# Reference: Expected IPL match counts by season
EXPECTED_COUNTS = {
    '2008': 59, '2009': 59, '2010': 60, '2011': 74, '2012': 76,
    '2013': 76, '2014': 60, '2015': 60, '2016': 60, '2017': 60,
    '2018': 60, '2019': 60, '2020': 60, '2021': 60, '2022': 74,
    '2023': 74, '2024': 74, '2025': 74
}

# Known IPL teams by era
IPL_TEAMS = {
    '2008-2010': ['Chennai Super Kings', 'Deccan Chargers', 'Delhi Daredevils', 
                  'Kings XI Punjab', 'Kolkata Knight Riders', 'Mumbai Indians',
                  'Rajasthan Royals', 'Royal Challengers Bangalore'],
    '2011-2012': ['Chennai Super Kings', 'Deccan Chargers', 'Delhi Daredevils',
                  'Kings XI Punjab', 'Kolkata Knight Riders', 'Mumbai Indians',
                  'Pune Warriors', 'Rajasthan Royals', 'Royal Challengers Bangalore',
                  'Kochi Tuskers Kerala'],
    '2013-2015': ['Chennai Super Kings', 'Delhi Daredevils', 'Kings XI Punjab',
                  'Kolkata Knight Riders', 'Mumbai Indians', 'Rajasthan Royals',
                  'Royal Challengers Bangalore', 'Sunrisers Hyderabad'],
    '2016-2017': ['Delhi Daredevils', 'Gujarat Lions', 'Kings XI Punjab',
                  'Kolkata Knight Riders', 'Mumbai Indians', 'Rising Pune Supergiant',
                  'Royal Challengers Bangalore', 'Sunrisers Hyderabad'],
    '2018-2021': ['Chennai Super Kings', 'Delhi Capitals', 'Kings XI Punjab',
                  'Kolkata Knight Riders', 'Mumbai Indians', 'Rajasthan Royals',
                  'Royal Challengers Bangalore', 'Sunrisers Hyderabad'],
    '2022-2025': ['Chennai Super Kings', 'Delhi Capitals', 'Gujarat Titans',
                  'Kolkata Knight Riders', 'Lucknow Super Giants', 'Mumbai Indians',
                  'Punjab Kings', 'Rajasthan Royals', 'Royal Challengers Bangalore',
                  'Sunrisers Hyderabad']
}


def load_data() -> pd.DataFrame:
    """Load combined IPL data"""
    combined_file = PROCESSED_DIR / "ipl_all_years_combined.csv"
    
    if not combined_file.exists():
        logger.error(f"File not found: {combined_file}")
        logger.info("Please run process_deliveries_to_matches.py first")
        return None
    
    df = pd.read_csv(combined_file)
    logger.info(f"✅ Loaded {len(df)} matches from {combined_file.name}")
    return df


def check_match_counts(df: pd.DataFrame):
    """Check if match counts match expected values"""
    
    logger.info("\n" + "="*60)
    logger.info("📊 MATCH COUNT VALIDATION")
    logger.info("="*60)
    
    df['season'] = df['season'].astype(str)
    actual_counts = df['season'].value_counts().sort_index()
    
    total_expected = 0
    total_actual = 0
    issues = []
    
    logger.info(f"\n{'Season':<10} {'Actual':<10} {'Expected':<10} {'Diff':<10} {'Status'}")
    logger.info("-" * 60)
    
    for season in sorted(EXPECTED_COUNTS.keys()):
        expected = EXPECTED_COUNTS[season]
        actual = actual_counts.get(season, 0)
        diff = actual - expected
        
        total_expected += expected
        total_actual += actual
        
        if actual == expected:
            status = '✅'
        elif actual == 0:
            status = '❌ MISSING'
            issues.append(f"Season {season}: No data found!")
        elif abs(diff) <= 3:
            status = '⚠️ Close'
        else:
            status = '❌ Off'
            issues.append(f"Season {season}: {actual} matches (expected {expected}, diff: {diff:+d})")
        
        logger.info(f"{season:<10} {actual:<10} {expected:<10} {diff:+<10} {status}")
    
    logger.info("-" * 60)
    logger.info(f"{'TOTAL':<10} {total_actual:<10} {total_expected:<10} {total_actual-total_expected:+<10}")
    
    accuracy = (total_actual / total_expected * 100) if total_expected > 0 else 0
    logger.info(f"\n📈 Data Completeness: {accuracy:.1f}%")
    
    if issues:
        logger.info(f"\n⚠️ Issues Found:")
        for issue in issues:
            logger.info(f"  - {issue}")
    else:
        logger.info(f"\n✅ All seasons have correct match counts!")
    
    return len(issues) == 0


def check_duplicates(df: pd.DataFrame):
    """Check for duplicate matches"""
    
    logger.info("\n" + "="*60)
    logger.info("🔍 DUPLICATE CHECK")
    logger.info("="*60)
    
    # Create match signature for duplicate detection
    df['match_signature'] = (
        df['match_date'].astype(str) + '|' +
        df[['team1', 'team2']].apply(lambda x: '|'.join(sorted([str(x['team1']), str(x['team2'])])), axis=1) + '|' +
        df['venue'].astype(str)
    )
    
    duplicates = df[df.duplicated(subset='match_signature', keep=False)]
    
    if len(duplicates) > 0:
        logger.info(f"❌ Found {len(duplicates)} duplicate matches!")
        logger.info(f"\nDuplicate groups:")
        
        for sig in duplicates['match_signature'].unique():
            dup_group = duplicates[duplicates['match_signature'] == sig]
            logger.info(f"\n  Match: {dup_group.iloc[0]['match_date']} - {dup_group.iloc[0]['team1']} vs {dup_group.iloc[0]['team2']}")
            logger.info(f"  Appears {len(dup_group)} times with match_ids: {dup_group['match_id'].tolist()}")
        
        return False
    else:
        logger.info(f"✅ No duplicates found!")
        return True


def check_team_consistency(df: pd.DataFrame):
    """Check if team names are consistent"""
    
    logger.info("\n" + "="*60)
    logger.info("🏏 TEAM CONSISTENCY CHECK")
    logger.info("="*60)
    
    all_teams = pd.concat([df['team1'], df['team2']]).unique()
    all_teams = sorted([t for t in all_teams if pd.notna(t)])
    
    logger.info(f"\n📋 Found {len(all_teams)} unique teams:")
    for team in all_teams:
        team_matches = len(df[(df['team1'] == team) | (df['team2'] == team)])
        logger.info(f"  - {team}: {team_matches} matches")
    
    # Check for potential name variations
    variations = []
    for i, team1 in enumerate(all_teams):
        for team2 in all_teams[i+1:]:
            # Check for similar names (potential duplicates)
            if team1.lower()[:10] == team2.lower()[:10]:
                variations.append((team1, team2))
    
    if variations:
        logger.info(f"\n⚠️ Potential name variations detected:")
        for t1, t2 in variations:
            logger.info(f"  - '{t1}' vs '{t2}'")
    else:
        logger.info(f"\n✅ No obvious team name variations")
    
    return len(variations) == 0


def check_missing_data(df: pd.DataFrame):
    """Check for missing critical data"""
    
    logger.info("\n" + "="*60)
    logger.info("⚠️ MISSING DATA CHECK")
    logger.info("="*60)
    
    critical_columns = [
        'match_date', 'team1', 'team2', 'venue', 'winner',
        'toss_winner', 'toss_decision'
    ]
    
    issues = []
    
    for col in critical_columns:
        if col not in df.columns:
            logger.info(f"❌ Column '{col}' not found in dataset!")
            issues.append(col)
            continue
        
        missing_count = df[col].isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        
        if missing_count > 0:
            status = '❌' if missing_pct > 5 else '⚠️'
            logger.info(f"{status} {col}: {missing_count} missing ({missing_pct:.1f}%)")
            if missing_pct > 5:
                issues.append(col)
        else:
            logger.info(f"✅ {col}: Complete")
    
    if issues:
        logger.info(f"\n❌ Critical columns with >5% missing data: {', '.join(issues)}")
        return False
    else:
        logger.info(f"\n✅ All critical columns are sufficiently complete!")
        return True


def check_date_consistency(df: pd.DataFrame):
    """Check if dates are valid and consistent"""
    
    logger.info("\n" + "="*60)
    logger.info("📅 DATE CONSISTENCY CHECK")
    logger.info("="*60)
    
    df['match_date'] = pd.to_datetime(df['match_date'], errors='coerce')
    
    # Check for invalid dates
    invalid_dates = df[df['match_date'].isna()]
    if len(invalid_dates) > 0:
        logger.info(f"❌ Found {len(invalid_dates)} matches with invalid dates")
        return False
    
    # Check date range
    min_date = df['match_date'].min()
    max_date = df['match_date'].max()
    logger.info(f"\n📊 Date range: {min_date.date()} to {max_date.date()}")
    
    # Check if dates align with seasons
    df['year_from_date'] = df['match_date'].dt.year
    df['season'] = df['season'].astype(str)
    
    mismatches = df[df['year_from_date'].astype(str) != df['season']]
    
    # Allow year+1 for seasons that span years (e.g., 2007/08)
    mismatches = mismatches[
        (mismatches['year_from_date'] - mismatches['season'].astype(int)).abs() > 1
    ]
    
    if len(mismatches) > 0:
        logger.info(f"\n⚠️ Found {len(mismatches)} matches with season/date mismatches:")
        for _, row in mismatches.head(5).iterrows():
            logger.info(f"  - Match {row['match_id']}: Season {row['season']}, Date {row['match_date'].date()}")
    else:
        logger.info(f"\n✅ All dates align with seasons")
    
    return len(mismatches) == 0


def check_result_consistency(df: pd.DataFrame):
    """Check if match results are consistent"""
    
    logger.info("\n" + "="*60)
    logger.info("🏆 RESULT CONSISTENCY CHECK")
    logger.info("="*60)
    
    # Check if winner is one of the playing teams
    if 'winner' in df.columns:
        invalid_winners = df[
            (df['winner'].notna()) &
            (df['winner'] != '') &
            (df['winner'] != df['team1']) &
            (df['winner'] != df['team2'])
        ]
        
        if len(invalid_winners) > 0:
            logger.info(f"❌ Found {len(invalid_winners)} matches where winner is not team1 or team2:")
            for _, row in invalid_winners.head(5).iterrows():
                logger.info(f"  - Match {row['match_id']}: {row['team1']} vs {row['team2']}, Winner: {row['winner']}")
            return False
        else:
            logger.info(f"✅ All winners are valid (team1 or team2)")
    
    # Check for matches without results
    no_result = df[df['winner'].isna() | (df['winner'] == '')]
    if len(no_result) > 0:
        logger.info(f"\n📊 Matches without result: {len(no_result)} ({len(no_result)/len(df)*100:.1f}%)")
    
    return True


def check_venue_consistency(df: pd.DataFrame):
    """Check venue data quality"""
    
    logger.info("\n" + "="*60)
    logger.info("🏟️ VENUE DATA CHECK")
    logger.info("="*60)
    
    venue_counts = df['venue'].value_counts()
    logger.info(f"\n📊 Total unique venues: {len(venue_counts)}")
    logger.info(f"\nTop 10 most used venues:")
    for venue, count in venue_counts.head(10).items():
        logger.info(f"  - {venue}: {count} matches")
    
    # Check for venues with very few matches (might be typos)
    rare_venues = venue_counts[venue_counts <= 2]
    if len(rare_venues) > 0:
        logger.info(f"\n⚠️ Venues with ≤2 matches (possible data issues):")
        for venue, count in rare_venues.head(10).items():
            logger.info(f"  - {venue}: {count} match(es)")
    
    return True


def generate_overall_report(df: pd.DataFrame):
    """Generate overall data quality report"""
    
    logger.info("\n" + "="*60)
    logger.info("📋 OVERALL DATA QUALITY REPORT")
    logger.info("="*60)
    
    df['season'] = df['season'].astype(str)
    
    logger.info(f"\n📊 Dataset Overview:")
    logger.info(f"  - Total matches: {len(df):,}")
    logger.info(f"  - Seasons covered: {df['season'].nunique()}")
    logger.info(f"  - Date range: {df['match_date'].min()} to {df['match_date'].max()}")
    logger.info(f"  - Unique teams: {pd.concat([df['team1'], df['team2']]).nunique()}")
    logger.info(f"  - Unique venues: {df['venue'].nunique()}")
    
    # Calculate completeness score
    expected_total = sum(EXPECTED_COUNTS.values())
    completeness = (len(df) / expected_total * 100)
    
    logger.info(f"\n📈 Data Quality Metrics:")
    logger.info(f"  - Completeness: {completeness:.1f}% ({len(df)}/{expected_total} matches)")
    
    # Missing data percentage
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    logger.info(f"  - Data density: {100-missing_pct:.1f}% (non-null values)")
    
    # Seasons with complete data
    complete_seasons = []
    for season, expected in EXPECTED_COUNTS.items():
        actual = len(df[df['season'] == season])
        if actual == expected:
            complete_seasons.append(season)
    
    logger.info(f"  - Complete seasons: {len(complete_seasons)}/{len(EXPECTED_COUNTS)}")
    logger.info(f"    ({', '.join(complete_seasons[:5])}{'...' if len(complete_seasons) > 5 else ''})")
    
    # Overall grade
    if completeness >= 98 and missing_pct < 2:
        grade = "A+ (Excellent)"
    elif completeness >= 95 and missing_pct < 5:
        grade = "A (Very Good)"
    elif completeness >= 90 and missing_pct < 10:
        grade = "B (Good)"
    elif completeness >= 80:
        grade = "C (Fair)"
    else:
        grade = "D (Needs Work)"
    
    logger.info(f"\n🎯 Overall Data Quality Grade: {grade}")


def main():
    """Run all data quality checks"""
    
    logger.info("\n" + "="*70)
    logger.info("🔍 IPL DATA QUALITY CHECKER")
    logger.info("="*70)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Run all checks
    checks_passed = []
    
    checks_passed.append(check_match_counts(df))
    checks_passed.append(check_duplicates(df))
    checks_passed.append(check_team_consistency(df))
    checks_passed.append(check_missing_data(df))
    checks_passed.append(check_date_consistency(df))
    checks_passed.append(check_result_consistency(df))
    check_venue_consistency(df)  # Informational only
    
    # Generate overall report
    generate_overall_report(df)
    
    # Final summary
    logger.info("\n" + "="*70)
    logger.info("✅ QUALITY CHECK COMPLETE")
    logger.info("="*70)
    
    passed = sum(checks_passed)
    total = len(checks_passed)
    
    logger.info(f"\n📊 Checks passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All quality checks passed! Data is ready for analysis.")
    elif passed >= total * 0.8:
        logger.info("⚠️ Most checks passed. Minor issues detected - review above.")
    else:
        logger.info("❌ Several issues detected. Please review and fix before proceeding.")


if __name__ == "__main__":
    main()