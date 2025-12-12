"""
Extract 2020 IPL Matches from Cricsheet
Also creates team ID to name mapping from Cricsheet data
"""

import pandas as pd
import json
from pathlib import Path
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

CRICSHEET_DIR = Path("data/raw/ipl_2024")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def extract_season_year(season_str) -> Optional[str]:
    """Extract year from season"""
    if not season_str:
        return None
    
    season_str = str(season_str)
    
    if '/' in season_str:
        parts = season_str.split('/')
        year = parts[1] if len(parts) > 1 else parts[0]
        if len(year) == 2:
            year = '20' + year if int(year) < 50 else '19' + year
        return year
    
    return str(season_str)


def is_valid_ipl_match(info: Dict, target_year: str = '2020') -> bool:
    """Check if valid IPL match for target year"""
    
    event = info.get('event', {})
    if isinstance(event, dict):
        tournament = event.get('name', '')
    else:
        tournament = str(event) if event else ''
    
    # Must be IPL
    if 'Indian Premier League' not in tournament:
        return False
    
    # Must be from target year
    season = info.get('season', '')
    year = extract_season_year(season)
    
    if year != target_year:
        return False
    
    # Must be club teams
    if info.get('team_type') != 'club':
        return False
    
    return True


def extract_match_data(match_json: Dict, target_year: str = '2020') -> Optional[Dict]:
    """Extract match data from Cricsheet JSON"""
    
    if not match_json or 'info' not in match_json:
        return None
    
    info = match_json['info']
    
    if not is_valid_ipl_match(info, target_year):
        return None
    
    # Extract data
    event = info.get('event', {})
    if isinstance(event, dict):
        tournament = event.get('name', '')
        match_number = event.get('match_number', '')
    else:
        tournament = str(event) if event else ''
        match_number = ''
    
    season = info.get('season', '')
    year = extract_season_year(season)
    
    teams = info.get('teams', [])
    team1 = teams[0] if len(teams) > 0 else ''
    team2 = teams[1] if len(teams) > 1 else ''
    
    dates = info.get('dates', [''])
    match_date = dates[0] if dates else ''
    
    # Outcome
    outcome = info.get('outcome', {})
    winner = outcome.get('winner', '')
    
    if 'by' in outcome:
        by_info = outcome['by']
        if 'runs' in by_info:
            win_by_runs = by_info['runs']
            win_by_wickets = None
        elif 'wickets' in by_info:
            win_by_runs = None
            win_by_wickets = by_info['wickets']
        else:
            win_by_runs = None
            win_by_wickets = None
    else:
        win_by_runs = None
        win_by_wickets = None
    
    # Toss
    toss = info.get('toss', {})
    toss_winner = toss.get('winner', '')
    toss_decision = toss.get('decision', '')
    
    # Officials
    officials = info.get('officials', {})
    umpires = officials.get('umpires', []) if isinstance(officials, dict) else []
    
    # Player of match
    pom = info.get('player_of_match', [])
    
    match_info = {
        'match_id': info.get('match_id', ''),
        'season': year,
        'match_date': match_date,
        'venue': info.get('venue', ''),
        'city': info.get('city', ''),
        'team1': team1,
        'team2': team2,
        'toss_winner': toss_winner,
        'toss_decision': toss_decision,
        'match_winner': winner,
        'win_by_runs': win_by_runs,
        'win_by_wickets': win_by_wickets,
        'player_of_match': pom[0] if pom else '',
        'umpire1': umpires[0] if len(umpires) > 0 else '',
        'umpire2': umpires[1] if len(umpires) > 1 else '',
        'match_type': 'T20',
        'event_name': tournament,
        'team_type': 'club',
        'result': outcome.get('result', ''),
    }
    
    return match_info


def extract_2020_matches() -> pd.DataFrame:
    """Extract all 2020 matches from Cricsheet"""
    logger.info("\n" + "="*70)
    logger.info("🏏 EXTRACTING 2020 IPL MATCHES FROM CRICSHEET")
    logger.info("="*70)
    
    logger.info(f"\n🔍 Scanning: {CRICSHEET_DIR}")
    
    if not CRICSHEET_DIR.exists():
        logger.error(f"❌ Directory not found!")
        return pd.DataFrame()
    
    json_files = list(CRICSHEET_DIR.glob("**/*.json"))
    logger.info(f"Found {len(json_files)} JSON files to scan")
    
    matches_2020 = []
    all_teams = set()
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                match_data = json.load(f)
            
            match_info = extract_match_data(match_data, '2020')
            if match_info:
                matches_2020.append(match_info)
                all_teams.add(match_info['team1'])
                all_teams.add(match_info['team2'])
                
        except Exception as e:
            continue
    
    if len(matches_2020) > 0:
        df = pd.DataFrame(matches_2020)
        logger.info(f"✅ Found {len(df)} matches from 2020")
        logger.info(f"✅ Found {len(all_teams)} unique teams")
        
        return df, sorted(all_teams)
    else:
        logger.warning("⚠️ No 2020 matches found in Cricsheet data")
        return pd.DataFrame(), []


def create_team_mapping(teams_from_cricsheet: List[str]) -> pd.DataFrame:
    """Create team ID to name mapping"""
    logger.info(f"\n" + "="*70)
    logger.info("🔧 CREATING TEAM ID MAPPING")
    logger.info("="*70)
    
    # Load existing processed data to get team IDs
    existing_file = PROCESSED_DIR / "ipl_all_years_combined.csv"
    
    if not existing_file.exists():
        logger.error("❌ Existing processed data not found!")
        return None
    
    existing_df = pd.read_csv(existing_file)
    
    # Get unique team IDs
    team_ids = sorted(set(existing_df['team1'].tolist() + existing_df['team2'].tolist()))
    
    logger.info(f"📊 Found {len(team_ids)} unique team IDs in existing data")
    logger.info(f"📊 Found {len(teams_from_cricsheet)} team names from Cricsheet")
    
    # If counts match, create mapping
    if len(team_ids) == len(teams_from_cricsheet):
        mapping_df = pd.DataFrame({
            'team_id': team_ids,
            'team_name': teams_from_cricsheet
        })
        
        logger.info(f"\n✅ Created team mapping:")
        for _, row in mapping_df.iterrows():
            logger.info(f"  {row['team_id']:2d} → {row['team_name']}")
        
        # Save mapping
        mapping_file = PROCESSED_DIR / "team_mapping.csv"
        mapping_df.to_csv(mapping_file, index=False)
        logger.info(f"\n💾 Saved: {mapping_file}")
        
        return mapping_df
    else:
        logger.warning(f"⚠️ Team count mismatch: {len(team_ids)} IDs vs {len(teams_from_cricsheet)} names")
        
        # Still save what we have from Cricsheet
        mapping_df = pd.DataFrame({
            'team_name': teams_from_cricsheet
        })
        mapping_file = PROCESSED_DIR / "team_names_from_cricsheet.csv"
        mapping_df.to_csv(mapping_file, index=False)
        logger.info(f"💾 Saved team names to: {mapping_file}")
        
        return None


def save_2020_matches(df: pd.DataFrame):
    """Save 2020 matches"""
    if len(df) == 0:
        return
    
    logger.info(f"\n💾 Saving 2020 matches...")
    
    output_file = PROCESSED_DIR / "ipl_2020_matches_cricsheet.csv"
    df.to_csv(output_file, index=False)
    
    logger.info(f"✅ Saved: {output_file.name} ({len(df)} matches)")
    logger.info(f"\n📊 2020 Season Summary:")
    logger.info(f"  - Matches: {len(df)}")
    logger.info(f"  - Date range: {df['match_date'].min()} to {df['match_date'].max()}")
    logger.info(f"  - Venues: {df['venue'].nunique()}")
    logger.info(f"  - Cities: {df['city'].nunique()}")


def main():
    """Main execution"""
    
    # Extract 2020 matches
    df_2020, teams = extract_2020_matches()
    
    if len(df_2020) == 0:
        logger.error("\n❌ Could not find 2020 matches in Cricsheet data")
        logger.info("This might mean:")
        logger.info("  1. Cricsheet doesn't have 2020 data")
        logger.info("  2. JSON files are in different location")
        logger.info("  3. Need to download 2020 data separately")
        return
    
    # Save 2020 matches
    save_2020_matches(df_2020)
    
    # Create team mapping
    if teams:
        mapping = create_team_mapping(teams)
    
    logger.info(f"\n" + "="*70)
    logger.info("🎉 EXTRACTION COMPLETE!")
    logger.info("="*70)
    
    logger.info(f"\n📊 Summary:")
    logger.info(f"  - 2020 matches extracted: {len(df_2020)}")
    logger.info(f"  - Teams identified: {len(teams)}")
    
    logger.info(f"\n🎯 Next Steps:")
    logger.info(f"  1. Review: data/processed/ipl_2020_matches_cricsheet.csv")
    logger.info(f"  2. If 60 matches found, merge with existing data")
    logger.info(f"  3. Use team mapping to add names")
    logger.info(f"  4. Final dataset will be 97%+ complete!")


if __name__ == "__main__":
    main()