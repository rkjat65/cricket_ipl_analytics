"""
Add IPL 2025 Data from Cricsheet
Merges 2025 matches from Cricsheet JSON files with existing Kaggle dataset
Creates complete IPL dataset (2008-2025)
"""

import pandas as pd
import json
from pathlib import Path
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Paths
CRICSHEET_DIR = Path("data/raw/ipl_2024")  # Contains all IPL JSON files
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def parse_cricsheet_match(file_path: Path) -> Optional[Dict]:
    """Parse single Cricsheet JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception:
        return None


def extract_season_year(season_str) -> Optional[str]:
    """Extract year from season string"""
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


def is_valid_ipl_match(info: Dict, target_year: str = '2025') -> bool:
    """Check if match is valid IPL match for target year"""
    
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


def extract_match_data(match_json: Dict) -> Optional[Dict]:
    """Extract match-level data from Cricsheet JSON"""
    
    if not match_json or 'info' not in match_json:
        return None
    
    info = match_json['info']
    
    # Validate
    if not is_valid_ipl_match(info, '2025'):
        return None
    
    # Extract basic info
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
    
    # Toss
    toss = info.get('toss', {})
    
    # Officials
    officials = info.get('officials', {})
    umpires = officials.get('umpires', []) if isinstance(officials, dict) else []
    
    # Player of match
    pom = info.get('player_of_match', [])
    
    # Calculate total runs/wickets from innings if available
    total_runs = 0
    total_wickets = 0
    innings_data = {}
    
    if 'innings' in match_json:
        for idx, inning in enumerate(match_json['innings'], 1):
            runs = 0
            wickets = 0
            
            if 'overs' in inning:
                for over in inning['overs']:
                    for delivery in over.get('deliveries', []):
                        runs += delivery.get('runs', {}).get('total', 0)
                        if 'wickets' in delivery:
                            wickets += len(delivery['wickets'])
            
            total_runs += runs
            total_wickets += wickets
            
            innings_data[f'innings{idx}_team'] = inning.get('team', '')
            innings_data[f'innings{idx}_score'] = runs
            innings_data[f'innings{idx}_wickets'] = wickets
    
    match_info = {
        'match_id': info.get('match_id', ''),
        'season': year,
        'match_date': match_date,
        'venue': info.get('venue', ''),
        'city': info.get('city', ''),
        'team1': team1,
        'team2': team2,
        'toss_winner': toss.get('winner', ''),
        'toss_decision': toss.get('decision', ''),
        'winner': winner,
        'result': outcome.get('result', ''),
        'result_margin': margin_value,
        'margin_type': margin_type,
        'margin_value': margin_value,
        'player_of_match': pom[0] if pom else '',
        'umpire1': umpires[0] if len(umpires) > 0 else '',
        'umpire2': umpires[1] if len(umpires) > 1 else '',
        'match_type': 'T20',
        'tournament': tournament,
        'tournament_type': 'ipl',
        'total_runs': total_runs,
        'total_wickets': total_wickets,
    }
    
    # Add innings data
    match_info.update(innings_data)
    
    return match_info


def extract_2025_matches() -> pd.DataFrame:
    """Extract all 2025 matches from Cricsheet JSON files"""
    
    logger.info("\n🔍 Scanning for IPL 2025 matches in Cricsheet data...")
    
    if not CRICSHEET_DIR.exists():
        logger.error(f"Directory not found: {CRICSHEET_DIR}")
        return pd.DataFrame()
    
    json_files = list(CRICSHEET_DIR.glob("**/*.json"))
    logger.info(f"Found {len(json_files)} JSON files to process")
    
    matches_2025 = []
    
    for file_path in json_files:
        match_data = parse_cricsheet_match(file_path)
        if not match_data:
            continue
        
        match_info = extract_match_data(match_data)
        if match_info:
            matches_2025.append(match_info)
    
    if len(matches_2025) > 0:
        df = pd.DataFrame(matches_2025)
        logger.info(f"✅ Found {len(df)} IPL 2025 matches")
        return df
    else:
        logger.warning("⚠️ No IPL 2025 matches found")
        return pd.DataFrame()


def merge_with_existing_data(df_2025: pd.DataFrame):
    """Merge 2025 data with existing dataset"""
    
    logger.info("\n🔄 Merging with existing data...")
    
    combined_file = PROCESSED_DIR / "ipl_all_years_combined.csv"
    
    if not combined_file.exists():
        logger.warning("⚠️ No existing data found. 2025 data will be saved standalone.")
        return df_2025
    
    # Load existing data
    df_existing = pd.read_csv(combined_file)
    logger.info(f"Loaded {len(df_existing)} existing matches")
    
    # Remove any existing 2025 data
    df_existing = df_existing[df_existing['season'].astype(str) != '2025']
    logger.info(f"After removing existing 2025: {len(df_existing)} matches")
    
    # Align columns
    # Get common columns
    common_cols = list(set(df_existing.columns) & set(df_2025.columns))
    
    # Add missing columns with NaN
    for col in df_existing.columns:
        if col not in df_2025.columns:
            df_2025[col] = np.nan
    
    for col in df_2025.columns:
        if col not in df_existing.columns:
            df_existing[col] = np.nan
    
    # Ensure same column order
    df_2025 = df_2025[df_existing.columns]
    
    # Merge
    df_combined = pd.concat([df_existing, df_2025], ignore_index=True)
    
    logger.info(f"✅ Merged dataset: {len(df_combined)} total matches")
    logger.info(f"  - 2008-2024: {len(df_existing)} matches")
    logger.info(f"  - 2025: {len(df_2025)} matches")
    
    return df_combined


def save_complete_dataset(df: pd.DataFrame):
    """Save complete dataset with 2025 data"""
    
    logger.info("\n💾 Saving complete dataset...")
    
    # Ensure season is string
    df['season'] = df['season'].astype(str)
    
    # Save combined file
    combined_file = PROCESSED_DIR / "ipl_all_years_combined.csv"
    df.to_csv(combined_file, index=False)
    logger.info(f"✅ Saved: {combined_file.name} ({len(df)} matches)")
    
    # Save 2025 separately
    df_2025 = df[df['season'] == '2025']
    if len(df_2025) > 0:
        file_2025 = PROCESSED_DIR / "ipl_2025_matches.csv"
        df_2025.to_csv(file_2025, index=False)
        logger.info(f"✅ Saved: {file_2025.name} ({len(df_2025)} matches)")
    
    # Show summary by year
    logger.info(f"\n📊 Complete dataset by season:")
    season_counts = df['season'].value_counts().sort_index()
    for season, count in season_counts.items():
        logger.info(f"  - {season}: {count} matches")
    
    logger.info(f"\n📈 Total: {len(df)} matches across {df['season'].nunique()} seasons")


def main():
    """Main execution"""
    
    logger.info("\n" + "="*60)
    logger.info("🏏 IPL 2025 DATA MERGER")
    logger.info("="*60)
    logger.info("Adding 2025 matches from Cricsheet to complete dataset")
    logger.info("="*60)
    
    # Extract 2025 matches
    df_2025 = extract_2025_matches()
    
    if len(df_2025) == 0:
        logger.error("❌ No 2025 matches found. Please check Cricsheet data.")
        return
    
    # Merge with existing data
    df_complete = merge_with_existing_data(df_2025)
    
    # Save complete dataset
    save_complete_dataset(df_complete)
    
    logger.info("\n" + "="*60)
    logger.info("✅ MERGE COMPLETE!")
    logger.info("="*60)
    logger.info("\n🎯 Next steps:")
    logger.info("  1. Run quality check: python scripts/check_data_quality.py")
    logger.info("  2. Review year-wise files in data/processed/")
    logger.info("  3. Load into database")


if __name__ == "__main__":
    import numpy as np
    main()