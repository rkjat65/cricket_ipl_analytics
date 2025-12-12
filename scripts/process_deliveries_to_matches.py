"""
IPL Data Processor from Deliveries CSV
Processes ball-by-ball data to create comprehensive match-level dataset
Generates year-wise CSV files with all parameters
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Paths
DELIVERIES_FILE = Path("data/raw/ipl_2024/deliveries.csv")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_deliveries_data() -> pd.DataFrame:
    """Load deliveries CSV file"""
    logger.info("Loading deliveries.csv...")
    
    if not DELIVERIES_FILE.exists():
        logger.error(f"File not found: {DELIVERIES_FILE}")
        logger.info("Expected location: data/raw/ipl_2024/deliveries.csv")
        return None
    
    try:
        df = pd.read_csv(DELIVERIES_FILE)
        logger.info(f"✅ Loaded {len(df):,} deliveries")
        logger.info(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"Failed to load file: {e}")
        return None


def extract_match_info(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract match-level information from ball-by-ball data
    Aggregates deliveries into match summary with all key parameters
    """
    
    logger.info("\n📊 Extracting match-level data...")
    
    # Group by match_id to get unique matches
    match_groups = deliveries_df.groupby('match_id')
    
    matches = []
    
    for match_id, match_data in match_groups:
        try:
            # Basic match info (same for all rows in a match)
            first_row = match_data.iloc[0]
            
            # Get teams from batting_team column
            teams = match_data['batting_team'].unique().tolist()
            if len(teams) < 2:
                teams = match_data['bowling_team'].unique().tolist()
            
            team1 = teams[0] if len(teams) > 0 else ''
            team2 = teams[1] if len(teams) > 1 else ''
            
            # Calculate match statistics
            total_runs = match_data['total_runs'].sum()
            
            # Get innings-wise scores
            innings_scores = {}
            for inning in match_data['inning'].unique():
                inning_data = match_data[match_data['inning'] == inning]
                batting_team = inning_data['batting_team'].iloc[0]
                score = inning_data['total_runs'].sum()
                wickets = inning_data['is_wicket'].sum() if 'is_wicket' in inning_data.columns else 0
                overs = inning_data['over'].max() + 1
                innings_scores[inning] = {
                    'team': batting_team,
                    'score': score,
                    'wickets': wickets,
                    'overs': overs
                }
            
            # Determine winner (team with higher score)
            if len(innings_scores) >= 2:
                inning1_score = innings_scores.get(1, {}).get('score', 0)
                inning2_score = innings_scores.get(2, {}).get('score', 0)
                
                if inning1_score > inning2_score:
                    winner = innings_scores[1]['team']
                    margin_type = 'runs'
                    margin_value = inning1_score - inning2_score
                elif inning2_score > inning1_score:
                    winner = innings_scores[2]['team']
                    margin_type = 'wickets'
                    inning2_wickets = innings_scores[2].get('wickets', 0)
                    margin_value = 10 - inning2_wickets
                else:
                    winner = ''
                    margin_type = 'tie'
                    margin_value = 0
            else:
                winner = ''
                margin_type = 'unknown'
                margin_value = 0
            
            # Extract other info from columns if available
            match_info = {
                'match_id': match_id,
                'season': first_row.get('season', ''),
                'match_date': first_row.get('date', first_row.get('match_date', '')),
                'venue': first_row.get('venue', ''),
                'city': first_row.get('city', ''),
                'team1': team1,
                'team2': team2,
                'toss_winner': first_row.get('toss_winner', ''),
                'toss_decision': first_row.get('toss_decision', ''),
                'winner': winner,
                'result': first_row.get('result', ''),
                'result_margin': first_row.get('result_margin', margin_value),
                'margin_type': margin_type,
                'margin_value': margin_value,
                'player_of_match': first_row.get('player_of_match', ''),
                'umpire1': first_row.get('umpire1', ''),
                'umpire2': first_row.get('umpire2', ''),
                'match_type': 'T20',
                'tournament': 'Indian Premier League',
                'tournament_type': 'ipl',
                
                # Match statistics
                'total_runs': total_runs,
                'total_wickets': match_data['is_wicket'].sum() if 'is_wicket' in match_data.columns else 0,
                'total_fours': (match_data['batsman_runs'] == 4).sum() if 'batsman_runs' in match_data.columns else 0,
                'total_sixes': (match_data['batsman_runs'] == 6).sum() if 'batsman_runs' in match_data.columns else 0,
                'total_wides': match_data['wide_runs'].sum() if 'wide_runs' in match_data.columns else 0,
                'total_noballs': match_data['noball_runs'].sum() if 'noball_runs' in match_data.columns else 0,
            }
            
            # Add innings-wise data
            for inning, data in innings_scores.items():
                match_info[f'innings{inning}_team'] = data['team']
                match_info[f'innings{inning}_score'] = data['score']
                match_info[f'innings{inning}_wickets'] = data['wickets']
                match_info[f'innings{inning}_overs'] = data['overs']
            
            matches.append(match_info)
            
        except Exception as e:
            logger.warning(f"Error processing match {match_id}: {e}")
            continue
    
    matches_df = pd.DataFrame(matches)
    logger.info(f"✅ Extracted {len(matches_df)} unique matches")
    
    return matches_df


def save_year_wise_data(matches_df: pd.DataFrame, prefix: str = 'ipl'):
    """Save data year-wise and combined"""
    
    logger.info("\n💾 Saving year-wise CSV files...")
    
    # Ensure season column is string
    matches_df['season'] = matches_df['season'].astype(str)
    
    # Get unique years
    years = sorted(matches_df['season'].unique())
    logger.info(f"Years found: {years}")
    
    # Save year-wise
    for year in years:
        year_data = matches_df[matches_df['season'] == year]
        output_file = PROCESSED_DIR / f"{prefix}_{year}_matches.csv"
        year_data.to_csv(output_file, index=False)
        logger.info(f"  ✅ Saved: {output_file.name} ({len(year_data)} matches)")
    
    # Save combined
    combined_file = PROCESSED_DIR / f"{prefix}_all_years_combined.csv"
    matches_df.to_csv(combined_file, index=False)
    logger.info(f"\n✅ Saved combined: {combined_file.name} ({len(matches_df)} total matches)")
    
    return years


def generate_summary_statistics(matches_df: pd.DataFrame):
    """Generate and display summary statistics"""
    
    logger.info("\n" + "="*60)
    logger.info("📊 DATA SUMMARY STATISTICS")
    logger.info("="*60)
    
    # Basic stats
    logger.info(f"\n📈 Overall Statistics:")
    logger.info(f"  - Total matches: {len(matches_df)}")
    logger.info(f"  - Date range: {matches_df['match_date'].min()} to {matches_df['match_date'].max()}")
    logger.info(f"  - Total seasons: {matches_df['season'].nunique()}")
    
    # Matches by year
    logger.info(f"\n📅 Matches by Season:")
    season_counts = matches_df['season'].value_counts().sort_index()
    for season, count in season_counts.items():
        logger.info(f"  - {season}: {count} matches")
    
    # Venue statistics
    logger.info(f"\n🏟️ Venue Statistics:")
    logger.info(f"  - Unique venues: {matches_df['venue'].nunique()}")
    top_venues = matches_df['venue'].value_counts().head(5)
    logger.info(f"  - Top 5 venues:")
    for venue, count in top_venues.items():
        logger.info(f"    • {venue}: {count} matches")
    
    # Team statistics
    logger.info(f"\n🏏 Team Statistics:")
    all_teams = pd.concat([matches_df['team1'], matches_df['team2']]).unique()
    logger.info(f"  - Unique teams: {len(all_teams)}")
    
    # Winner statistics
    if 'winner' in matches_df.columns:
        winners = matches_df[matches_df['winner'] != '']['winner'].value_counts()
        logger.info(f"\n🏆 Top 10 Winners (All Time):")
        for idx, (team, wins) in enumerate(winners.head(10).items(), 1):
            total_matches = len(matches_df[(matches_df['team1'] == team) | (matches_df['team2'] == team)])
            win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
            logger.info(f"  {idx}. {team}: {wins} wins ({win_rate:.1f}% win rate)")
    
    # Toss impact
    if 'toss_winner' in matches_df.columns and 'winner' in matches_df.columns:
        toss_wins = matches_df[matches_df['toss_winner'] == matches_df['winner']]
        toss_impact = len(toss_wins) / len(matches_df) * 100
        logger.info(f"\n🪙 Toss Impact:")
        logger.info(f"  - Toss winner also won match: {len(toss_wins)}/{len(matches_df)} ({toss_impact:.1f}%)")
    
    # Missing data check
    logger.info(f"\n⚠️ Data Completeness:")
    missing_data = matches_df.isnull().sum()
    missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
    
    if len(missing_data) > 0:
        logger.info(f"  Columns with missing values:")
        for col, count in missing_data.items():
            pct = (count / len(matches_df)) * 100
            logger.info(f"    - {col}: {count} ({pct:.1f}%)")
    else:
        logger.info(f"  ✅ No missing values in key columns!")


def main():
    """Main processing pipeline"""
    
    logger.info("\n" + "="*60)
    logger.info("🏏 IPL DATA PROCESSOR - Deliveries to Matches")
    logger.info("="*60)
    
    # Load deliveries data
    deliveries_df = load_deliveries_data()
    if deliveries_df is None:
        return
    
    # Show deliveries info
    logger.info(f"\n📋 Deliveries Data Info:")
    logger.info(f"  - Total deliveries: {len(deliveries_df):,}")
    logger.info(f"  - Unique matches: {deliveries_df['match_id'].nunique()}")
    logger.info(f"  - Seasons: {sorted(deliveries_df['season'].unique()) if 'season' in deliveries_df.columns else 'N/A'}")
    
    # Extract match-level data
    matches_df = extract_match_info(deliveries_df)
    if matches_df is None or len(matches_df) == 0:
        logger.error("No matches extracted!")
        return
    
    # Save year-wise data
    years = save_year_wise_data(matches_df)
    
    # Generate statistics
    generate_summary_statistics(matches_df)
    
    logger.info("\n" + "="*60)
    logger.info("✅ PROCESSING COMPLETE!")
    logger.info("="*60)
    logger.info(f"\n📁 Output location: {PROCESSED_DIR}")
    logger.info(f"📊 Years processed: {', '.join(years)}")
    logger.info(f"📈 Total matches: {len(matches_df)}")
    
    logger.info("\n🎯 Next steps:")
    logger.info("  1. Run data quality check: python scripts/check_data_quality.py")
    logger.info("  2. Add 2025 data if needed")
    logger.info("  3. Load into database")
    logger.info("  4. Start building dashboard")


if __name__ == "__main__":
    main()