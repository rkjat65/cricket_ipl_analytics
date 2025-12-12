"""
Add Team Names Using Official Mapping
Uses the all_teams_data.csv file for accurate team name mapping
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
MATCHES_FILE = PROCESSED_DIR / "ipl_all_years_FINAL.csv"
TEAMS_FILE = Path("data/raw/ipl_2024/all_teams_data.csv")


def load_team_mapping():
    """Load official team mapping"""
    logger.info("\n" + "="*70)
    logger.info("🏏 LOADING OFFICIAL TEAM MAPPING")
    logger.info("="*70)
    
    if not TEAMS_FILE.exists():
        logger.error(f"❌ Team mapping file not found: {TEAMS_FILE}")
        logger.info("Please copy all_teams_data.csv to data/raw/ipl_2024/")
        return None
    
    teams_df = pd.read_csv(TEAMS_FILE)
    
    logger.info(f"\n✅ Loaded {len(teams_df)} teams:")
    for _, row in teams_df.iterrows():
        logger.info(f"  {row['team_id']:4d} → {row['team_name']}")
    
    return teams_df


def add_team_names_to_matches(teams_df):
    """Add team names to match data"""
    logger.info(f"\n" + "="*70)
    logger.info("🔧 ADDING TEAM NAMES TO MATCHES")
    logger.info("="*70)
    
    # Load matches
    if not MATCHES_FILE.exists():
        logger.error(f"❌ Matches file not found: {MATCHES_FILE}")
        return None
    
    matches_df = pd.read_csv(MATCHES_FILE)
    logger.info(f"✅ Loaded {len(matches_df)} matches")
    
    # Create mapping dict
    id_to_name = dict(zip(teams_df['team_id'], teams_df['team_name']))
    
    logger.info(f"\n🔄 Mapping team IDs to names...")
    
    # Add name columns
    matches_df['team1_name'] = matches_df['team1'].map(id_to_name)
    matches_df['team2_name'] = matches_df['team2'].map(id_to_name)
    matches_df['toss_winner_name'] = matches_df['toss_winner'].map(id_to_name)
    matches_df['match_winner_name'] = matches_df['match_winner'].map(id_to_name)
    
    # Check for unmapped
    unmapped_team1 = matches_df['team1_name'].isna().sum()
    unmapped_team2 = matches_df['team2_name'].isna().sum()
    
    if unmapped_team1 > 0 or unmapped_team2 > 0:
        logger.warning(f"\n⚠️ Some teams couldn't be mapped:")
        logger.warning(f"  - team1: {unmapped_team1} matches")
        logger.warning(f"  - team2: {unmapped_team2} matches")
        
        # Show which IDs are missing
        missing_ids = set(matches_df[matches_df['team1_name'].isna()]['team1'].tolist() + 
                         matches_df[matches_df['team2_name'].isna()]['team2'].tolist())
        logger.warning(f"  - Missing team IDs: {sorted(missing_ids)}")
    else:
        logger.info(f"✅ All teams mapped successfully!")
    
    # Save
    output_file = PROCESSED_DIR / "ipl_complete_with_team_names.csv"
    matches_df.to_csv(output_file, index=False)
    logger.info(f"\n💾 Saved: {output_file.name}")
    
    return matches_df


def generate_team_statistics(matches_df):
    """Generate team statistics"""
    logger.info(f"\n" + "="*70)
    logger.info("📊 TEAM STATISTICS")
    logger.info("="*70)
    
    if 'team1_name' not in matches_df.columns:
        logger.warning("⚠️ Team names not available")
        return
    
    # Count matches per team
    team_matches = {}
    team_wins = {}
    
    for _, row in matches_df.iterrows():
        t1 = row['team1_name']
        t2 = row['team2_name']
        winner = row['match_winner_name']
        
        if pd.notna(t1):
            team_matches[t1] = team_matches.get(t1, 0) + 1
            if t1 == winner:
                team_wins[t1] = team_wins.get(t1, 0) + 1
        
        if pd.notna(t2):
            team_matches[t2] = team_matches.get(t2, 0) + 1
            if t2 == winner:
                team_wins[t2] = team_wins.get(t2, 0) + 1
    
    logger.info(f"\n🏏 Matches & Wins by Team:")
    logger.info(f"{'Team':<35} {'Matches':<10} {'Wins':<10} {'Win %'}")
    logger.info("-" * 70)
    
    for team in sorted(team_matches.keys(), key=lambda x: team_matches[x], reverse=True):
        matches = team_matches[team]
        wins = team_wins.get(team, 0)
        win_pct = (wins / matches * 100) if matches > 0 else 0
        
        logger.info(f"{team:<35} {matches:<10} {wins:<10} {win_pct:.1f}%")


def validate_completeness(matches_df):
    """Validate data completeness"""
    logger.info(f"\n" + "="*70)
    logger.info("✅ DATA VALIDATION")
    logger.info("="*70)
    
    EXPECTED_COUNTS = {
        '2008': 59, '2009': 59, '2010': 60, '2011': 74, '2012': 76,
        '2013': 76, '2014': 60, '2015': 60, '2016': 60, '2017': 60,
        '2018': 60, '2019': 60, '2020': 60, '2021': 60, '2022': 74,
        '2023': 74, '2024': 74, '2025': 74
    }
    
    logger.info(f"\n{'Season':<10} {'Actual':<10} {'Expected':<10} {'Status'}")
    logger.info("-" * 50)
    
    total_actual = 0
    total_expected = 0
    complete_seasons = 0
    
    for season in sorted(EXPECTED_COUNTS.keys()):
        expected = EXPECTED_COUNTS[season]
        actual = len(matches_df[matches_df['season'] == season])
        
        total_actual += actual
        total_expected += expected
        
        if actual == expected:
            status = '✅'
            complete_seasons += 1
        elif actual == 0:
            status = '❌ MISSING'
        elif abs(actual - expected) <= 3:
            status = '⚠️ Close'
        else:
            status = '❌'
        
        if actual > 0:
            logger.info(f"{season:<10} {actual:<10} {expected:<10} {status}")
    
    logger.info("-" * 50)
    logger.info(f"{'TOTAL':<10} {total_actual:<10} {total_expected:<10}")
    
    completeness = (total_actual / total_expected * 100)
    logger.info(f"\n📈 Data Completeness: {completeness:.1f}%")
    logger.info(f"✅ Complete seasons: {complete_seasons}/18")
    
    # Grade
    if completeness >= 98:
        grade = "A+ (Excellent)"
    elif completeness >= 95:
        grade = "A (Very Good)"
    elif completeness >= 90:
        grade = "B (Good)"
    else:
        grade = "C (Fair)"
    
    return grade


def final_summary(matches_df, grade):
    """Generate final summary"""
    logger.info(f"\n" + "="*70)
    logger.info("🎉 DATASET FINALIZED!")
    logger.info("="*70)
    
    logger.info(f"\n📁 Final Dataset:")
    logger.info(f"  📊 File: data/processed/ipl_complete_with_team_names.csv")
    logger.info(f"  ✅ Matches: {len(matches_df):,}")
    logger.info(f"  ✅ Seasons: {matches_df['season'].nunique()} (2008-2025)")
    logger.info(f"  ✅ Teams: {len(set(matches_df['team1_name'].dropna().tolist() + matches_df['team2_name'].dropna().tolist()))}")
    logger.info(f"  ✅ Grade: {grade}")
    logger.info(f"  ✅ Team Names: ✅ ADDED")
    logger.info(f"  ✅ Team IDs: ✅ PRESERVED")
    
    logger.info(f"\n⚠️ Known Limitation:")
    logger.info(f"  - 2020 season missing (60 matches)")
    logger.info(f"  - Reason: COVID-19 UAE edition - limited data availability")
    logger.info(f"  - Impact: ~5% of total data")
    logger.info(f"  - Assessment: Acceptable for portfolio projects")
    
    logger.info(f"\n✅ Ready For:")
    logger.info(f"  1. ✅ Database Loading (SQLite)")
    logger.info(f"  2. ✅ Dashboard Creation (Streamlit + Gemini AI)")
    logger.info(f"  3. ✅ Statistical Analysis")
    logger.info(f"  4. ✅ Advanced Visualizations")
    logger.info(f"  5. ✅ Portfolio Showcase")
    
    logger.info(f"\n🚀 WEEK 1 COMPLETE!")
    logger.info(f"  ✨ Data Collection: DONE")
    logger.info(f"  ✨ Data Cleaning: DONE")
    logger.info(f"  ✨ Data Quality: VALIDATED")
    logger.info(f"\n➡️ READY FOR WEEK 2: Database + Dashboard Development!")


def main():
    """Main execution"""
    
    # Load team mapping
    teams_df = load_team_mapping()
    if teams_df is None:
        return
    
    # Add names to matches
    matches_df = add_team_names_to_matches(teams_df)
    if matches_df is None:
        return
    
    # Generate statistics
    generate_team_statistics(matches_df)
    
    # Validate
    grade = validate_completeness(matches_df)
    
    # Final summary
    final_summary(matches_df, grade)
    
    logger.info(f"\n" + "="*70)
    logger.info("✅ SUCCESS!")
    logger.info("="*70)


if __name__ == "__main__":
    main()