"""
Complete Team ID Analysis
Analyzes EVERY team ID to identify them correctly
"""

import pandas as pd
from pathlib import Path
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
FINAL_FILE = PROCESSED_DIR / "ipl_all_years_FINAL.csv"


def analyze_all_teams():
    """Analyze every single team ID"""
    logger.info("\n" + "="*70)
    logger.info("🔍 COMPLETE TEAM ID ANALYSIS")
    logger.info("="*70)
    
    df = pd.read_csv(FINAL_FILE)
    
    # Get all unique team IDs
    all_ids = sorted(set(df['team1'].tolist() + df['team2'].tolist()))
    
    logger.info(f"\nAnalyzing ALL {len(all_ids)} team IDs...")
    logger.info("="*70)
    
    team_info = []
    
    for team_id in all_ids:
        # Get matches
        team_matches = df[(df['team1'] == team_id) | (df['team2'] == team_id)]
        
        # Basic stats
        total_matches = len(team_matches)
        seasons = sorted(team_matches['season'].unique())
        date_range = f"{team_matches['match_date'].min()} to {team_matches['match_date'].max()}"
        
        # Top venue
        top_venue = team_matches['venue'].value_counts().iloc[0] if len(team_matches) > 0 else ''
        venue_count = team_matches['venue'].value_counts().iloc[0] if len(team_matches) > 0 else 0
        
        # Top city
        city_data = team_matches['city'].dropna().value_counts()
        top_city = city_data.iloc[0] if len(city_data) > 0 else 'Unknown'
        city_count = city_data.iloc[0] if len(city_data) > 0 else 0
        
        # Win rate
        wins = len(team_matches[team_matches['match_winner'] == team_id])
        win_pct = (wins / total_matches * 100) if total_matches > 0 else 0
        
        team_info.append({
            'id': team_id,
            'matches': total_matches,
            'seasons': len(seasons),
            'season_list': seasons,
            'first_season': seasons[0] if seasons else None,
            'last_season': seasons[-1] if seasons else None,
            'top_city': top_city,
            'city_matches': city_count,
            'top_venue': top_venue,
            'venue_matches': venue_count,
            'wins': wins,
            'win_pct': win_pct,
            'date_range': date_range
        })
    
    # Sort by matches (most to least)
    team_info.sort(key=lambda x: x['matches'], reverse=True)
    
    # Display
    logger.info(f"\n{'ID':<5} {'Matches':<10} {'Seasons':<10} {'Years':<20} {'Top City':<20} {'Win%':<8} {'Likely Team'}")
    logger.info("-" * 130)
    
    for team in team_info:
        seasons_str = f"{team['first_season']}-{team['last_season']}"
        
        # Identify likely team
        likely_team = identify_team(team)
        
        logger.info(
            f"{team['id']:<5} "
            f"{team['matches']:<10} "
            f"{team['seasons']:<10} "
            f"{seasons_str:<20} "
            f"{team['top_city']:<20} "
            f"{team['win_pct']:<8.1f} "
            f"{likely_team}"
        )
    
    logger.info("\n" + "="*130)
    
    # Detailed breakdown
    logger.info("\n📋 DETAILED BREAKDOWN:")
    logger.info("="*70)
    
    for team in team_info:
        logger.info(f"\n{'='*70}")
        logger.info(f"TEAM ID: {team['id']}")
        logger.info(f"{'='*70}")
        logger.info(f"Matches: {team['matches']}")
        logger.info(f"Active Seasons: {team['season_list']}")
        logger.info(f"Date Range: {team['date_range']}")
        logger.info(f"Primary Home:")
        logger.info(f"  - City: {team['top_city']} ({team['city_matches']} home matches)")
        logger.info(f"  - Venue: {team['top_venue']} ({team['venue_matches']} matches)")
        logger.info(f"Performance: {team['wins']}/{team['matches']} wins ({team['win_pct']:.1f}%)")
        logger.info(f"\n🎯 LIKELY IDENTITY: {identify_team(team)}")


def identify_team(team_info):
    """Identify team based on patterns"""
    matches = team_info['matches']
    seasons = team_info['seasons']
    first = team_info['first_season']
    last = team_info['last_season']
    city = str(team_info['top_city'])
    venue = str(team_info['top_venue'])
    
    # Major franchises (200+ matches, active since 2008)
    if matches >= 200 and first == 2008:
        if 'Mumbai' in city or 'Wankhede' in venue:
            return "Mumbai Indians"
        elif 'Chennai' in city or 'Chepauk' in venue:
            return "Chennai Super Kings"
        elif 'Kolkata' in city or 'Eden' in venue:
            return "Kolkata Knight Riders"
        elif 'Bangalore' in city or 'Chinnaswamy' in venue:
            return "Royal Challengers Bangalore"
        elif 'Jaipur' in city:
            return "Rajasthan Royals"
        elif 'Delhi' in city or 'Kotla' in venue or 'Feroz Shah' in venue:
            return "Delhi Capitals (formerly Delhi Daredevils)"
        elif 'Punjab' in city or 'Mohali' in city or 'Chandigarh' in city:
            return "Kings XI Punjab / Punjab Kings"
    
    # Sunrisers Hyderabad (2013+)
    if matches >= 150 and first >= 2013 and 'Hyderabad' in city:
        return "Sunrisers Hyderabad"
    
    # New teams (2022+)
    if first >= 2022:
        if 'Lucknow' in city:
            return "Lucknow Super Giants"
        elif 'Ahmedabad' in city or 'Gujarat' in city:
            return "Gujarat Titans"
    
    # Defunct teams
    if last <= 2012 and 'Hyderabad' in city:
        return "Deccan Chargers (defunct)"
    
    if first == 2011 and last == 2011 and matches <= 15:
        return "Kochi Tuskers Kerala (defunct, 2011 only)"
    
    if first == 2011 and last <= 2013 and 'Pune' in city:
        return "Pune Warriors (defunct, 2011-2013)"
    
    if first == 2016 and last == 2017:
        if 'Pune' in city:
            return "Rising Pune Supergiant (defunct, 2016-2017)"
        else:
            return "Gujarat Lions (defunct, 2016-2017)"
    
    return "UNKNOWN - Need more analysis"


def generate_final_mapping():
    """Generate the correct mapping"""
    logger.info("\n" + "="*70)
    logger.info("🎯 GENERATING CORRECT MAPPING")
    logger.info("="*70)
    
    df = pd.read_csv(FINAL_FILE)
    all_ids = sorted(set(df['team1'].tolist() + df['team2'].tolist()))
    
    logger.info("\nBased on the analysis above, here's the suggested mapping:")
    logger.info("\nteam_mapping = {")
    
    for team_id in all_ids:
        team_matches = df[(df['team1'] == team_id) | (df['team2'] == team_id)]
        
        city_data = team_matches['city'].dropna().value_counts()
        venue_data = team_matches['venue'].value_counts()
        
        team_info = {
            'matches': len(team_matches),
            'seasons': len(team_matches['season'].unique()),
            'season_list': sorted(team_matches['season'].unique()),
            'first_season': team_matches['season'].min(),
            'last_season': team_matches['season'].max(),
            'top_city': city_data.iloc[0] if len(city_data) > 0 else 'Unknown',
            'city_matches': city_data.iloc[0] if len(city_data) > 0 else 0,
            'top_venue': venue_data.iloc[0] if len(venue_data) > 0 else '',
            'venue_matches': venue_data.iloc[0] if len(venue_data) > 0 else 0,
            'wins': len(team_matches[team_matches['match_winner'] == team_id]),
            'win_pct': 0
        }
        
        likely = identify_team(team_info)
        logger.info(f"    {team_id}: '{likely}',")
    
    logger.info("}")


def main():
    """Main execution"""
    analyze_all_teams()
    generate_final_mapping()
    
    logger.info("\n" + "="*70)
    logger.info("✅ ANALYSIS COMPLETE")
    logger.info("="*70)
    logger.info("\nUse the mapping above to update the script!")


if __name__ == "__main__":
    main()