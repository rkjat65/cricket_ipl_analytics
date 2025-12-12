"""
Ultra-Strict Cricket Data Processor
Extracts ONLY main IPL and T20 World Cup matches with exact filtering
Based on official match counts validation
"""

import pandas as pd
import json
import yaml
from pathlib import Path
import logging
from typing import Dict, List, Optional
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Paths
IPL_RAW_DIR = Path("data/raw/ipl_2024")
T20_RAW_DIR = Path("data/raw/t20wc")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Reference data for validation
EXPECTED_IPL_COUNTS = {
    '2008': 59, '2009': 59, '2010': 60, '2011': 74, '2012': 76,
    '2013': 76, '2014': 60, '2015': 60, '2016': 60, '2017': 60,
    '2018': 60, '2019': 60, '2020': 60, '2021': 60, '2022': 74,
    '2023': 74, '2024': 74, '2025': 74  # IPL 2025 concluded
}

EXPECTED_T20WC_COUNTS = {
    '2007': 27, '2009': 27, '2010': 27, '2012': 27, '2014': 35,
    '2016': 35, '2021': 45, '2022': 45, '2024': 55
    # Next T20 WC: 2026
}


def parse_match_file(file_path: Path) -> Optional[Dict]:
    """Parse single match file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix == '.json':
                data = json.load(f)
            elif file_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                return None
        return data
    except Exception:
        return None


def extract_season_year(season_str) -> Optional[str]:
    """Extract year from season, handling all formats"""
    if not season_str:
        return None
    
    season_str = str(season_str)
    
    if '/' in season_str:
        parts = season_str.split('/')
        year = parts[1]
        if len(year) == 2:
            year = '20' + year if int(year) < 50 else '19' + year
        return year
    
    return str(season_str)


def is_main_tournament_match(info: Dict, tournament_type: str) -> bool:
    """
    Ultra-strict validation for main tournament matches only
    """
    # Get basic info
    event = info.get('event', {})
    if isinstance(event, dict):
        tournament_name = event.get('name', '').lower()
    else:
        tournament_name = str(event).lower() if event else ''
    
    season = info.get('season', '')
    year = extract_season_year(season)
    
    if not year:
        return False
    
    # Check team type
    team_type = info.get('team_type', '')
    
    if tournament_type == 'ipl':
        # IPL validations
        if 'indian premier league' not in tournament_name:
            return False
        
        # Only years 2008-2024
        if year not in EXPECTED_IPL_COUNTS:
            return False
        
        # Must be club teams
        if team_type != 'club':
            return False
        
        return True
    
    elif tournament_type == 't20wc':
        # T20 World Cup - MAIN tournament only
        
        # Must be in valid WC year
        if year not in EXPECTED_T20WC_COUNTS:
            return False
        
        # Must be international teams
        if team_type != 'international':
            return False
        
        # Strict tournament name matching
        # Exclude qualifiers, regionals, women's, etc.
        exclude_keywords = [
            'qualifier', 'qualifying', 'regional', 'division',
            'women', 'female', 'associate', 'preliminary',
            'challenge', 'trophy', 'series', 'bilateral'
        ]
        
        if any(keyword in tournament_name for keyword in exclude_keywords):
            return False
        
        # Valid main tournament names only
        valid_names = [
            'icc world twenty20',
            'icc world t20',
            'icc men\'s t20 world cup',
            'icc men\'s world twenty20'
        ]
        
        if not any(name in tournament_name for name in valid_names):
            return False
        
        # Additional validation: Check teams are major cricket nations
        teams = info.get('teams', [])
        if len(teams) >= 2:
            # List of countries that play in main T20 WC (not qualifiers)
            major_nations = {
                'Afghanistan', 'Australia', 'Bangladesh', 'England',
                'India', 'Ireland', 'Netherlands', 'New Zealand',
                'Pakistan', 'Scotland', 'South Africa', 'Sri Lanka',
                'West Indies', 'Zimbabwe', 'Namibia', 'Oman',
                'Papua New Guinea', 'United Arab Emirates', 'USA',
                'Canada', 'Kenya', 'Hong Kong'
            }
            
            # At least one team should be from major nations
            team_valid = any(team in major_nations for team in teams)
            
            # Exclude obvious qualifier teams
            qualifier_only = {
                'Uganda', 'Tanzania', 'Rwanda', 'Nigeria',
                'Botswana', 'Mozambique', 'Lesotho', 'Malawi'
            }
            
            if all(team in qualifier_only for team in teams):
                return False
        
        return True
    
    return False


def extract_match_info(match_data: Dict, tournament_type: str) -> Optional[Dict]:
    """Extract match information with strict validation"""
    if not match_data or 'info' not in match_data:
        return None
    
    info = match_data['info']
    
    # Apply strict validation
    if not is_main_tournament_match(info, tournament_type):
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
    
    outcome = info.get('outcome', {})
    winner = outcome.get('winner', '')
    
    if 'result' in outcome:
        margin_type = 'no_result'
        margin_value = 0
    elif winner == '':
        margin_type = 'no_result'
        margin_value = 0
    elif 'by' in outcome:
        by_info = outcome['by']
        if 'runs' in by_info:
            margin_type = 'runs'
            margin_value = by_info['runs']
        elif 'wickets' in by_info:
            margin_type = 'wickets'
            margin_value = by_info['wickets']
        else:
            margin_type = 'unknown'
            margin_value = 0
    else:
        margin_type = 'unknown'
        margin_value = 0
    
    toss = info.get('toss', {})
    officials = info.get('officials', {})
    umpires = officials.get('umpires', []) if isinstance(officials, dict) else []
    pom = info.get('player_of_match', [])
    
    players_dict = info.get('players', {})
    team1_squad = players_dict.get(team1, []) if team1 else []
    team2_squad = players_dict.get(team2, []) if team2 else []
    
    return {
        'match_id': info.get('match_id', ''),
        'tournament': tournament,
        'tournament_type': tournament_type,
        'season': season,
        'year': year,
        'match_number': match_number,
        'match_date': match_date,
        'venue': info.get('venue', ''),
        'city': info.get('city', ''),
        'team1': team1,
        'team2': team2,
        'team1_squad_size': len(team1_squad),
        'team2_squad_size': len(team2_squad),
        'toss_winner': toss.get('winner', ''),
        'toss_decision': toss.get('decision', ''),
        'winner': winner,
        'margin_type': margin_type,
        'margin_value': margin_value,
        'player_of_match': pom[0] if pom else '',
        'umpire1': umpires[0] if len(umpires) > 0 else '',
        'umpire2': umpires[1] if len(umpires) > 1 else '',
        'match_type': info.get('match_type', ''),
        'gender': info.get('gender', 'male'),
        'team_type': info.get('team_type', ''),
        'overs': info.get('overs', 20),
    }


def process_tournament_data(raw_dir: Path, tournament_type: str, output_prefix: str) -> Dict[str, List[Dict]]:
    """Process tournament data with strict filtering"""
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing {tournament_type.upper()} Data")
    logger.info(f"{'='*60}")
    
    if not raw_dir.exists():
        logger.error(f"Directory not found: {raw_dir}")
        return {}
    
    all_files = list(raw_dir.glob("**/*.json")) + list(raw_dir.glob("**/*.yaml")) + list(raw_dir.glob("**/*.yml"))
    logger.info(f"Found {len(all_files)} total files")
    
    matches_by_year = defaultdict(list)
    total_processed = 0
    total_skipped = 0
    
    for file_path in all_files:
        match_data = parse_match_file(file_path)
        if not match_data:
            total_skipped += 1
            continue
        
        match_info = extract_match_info(match_data, tournament_type)
        if match_info and match_info['year']:
            year = match_info['year']
            matches_by_year[year].append(match_info)
            total_processed += 1
        else:
            total_skipped += 1
    
    logger.info(f"\n📊 Processing Summary:")
    logger.info(f"  - Processed: {total_processed} matches")
    logger.info(f"  - Skipped: {total_skipped} files")
    logger.info(f"  - Years: {sorted(matches_by_year.keys())}")
    
    # Validate counts
    logger.info(f"\n📋 Validation vs Expected:")
    expected_counts = EXPECTED_IPL_COUNTS if tournament_type == 'ipl' else EXPECTED_T20WC_COUNTS
    
    for year in sorted(matches_by_year.keys()):
        actual = len(matches_by_year[year])
        expected = expected_counts.get(year, '?')
        status = '✅' if actual == expected else '⚠️'
        logger.info(f"  {status} {year}: {actual} matches (expected: {expected})")
    
    # Save files
    logger.info(f"\n💾 Saving CSV files...")
    for year, matches in matches_by_year.items():
        df = pd.DataFrame(matches)
        output_file = PROCESSED_DIR / f"{output_prefix}_{year}_matches.csv"
        df.to_csv(output_file, index=False)
    
    # Save combined
    if matches_by_year:
        all_matches = []
        for matches in matches_by_year.values():
            all_matches.extend(matches)
        
        combined_df = pd.DataFrame(all_matches)
        combined_file = PROCESSED_DIR / f"{output_prefix}_all_years_combined.csv"
        combined_df.to_csv(combined_file, index=False)
        logger.info(f"\n✅ Saved: {combined_file.name} ({len(combined_df)} total matches)")
        
        if 'winner' in combined_df.columns:
            top_winners = combined_df[combined_df['winner'] != '']['winner'].value_counts().head(10)
            logger.info(f"\n🏆 Top 10 Winners:")
            for idx, (team, wins) in enumerate(top_winners.items(), 1):
                logger.info(f"  {idx}. {team}: {wins} wins")
    
    return matches_by_year


def main():
    """Main execution"""
    logger.info("\n" + "="*60)
    logger.info("🏏 ULTRA-STRICT CRICKET DATA PROCESSOR")
    logger.info("="*60)
    logger.info("Filtering for MAIN tournament matches only")
    logger.info("="*60 + "\n")
    
    # Process IPL
    ipl_data = process_tournament_data(IPL_RAW_DIR, 'ipl', 'ipl')
    
    # Process T20 WC
    t20_data = process_tournament_data(T20_RAW_DIR, 't20wc', 't20wc')
    
    logger.info("\n" + "="*60)
    logger.info("✅ PROCESSING COMPLETE!")
    logger.info("="*60 + "\n")


if __name__ == "__main__":
    main()