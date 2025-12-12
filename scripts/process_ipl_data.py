"""
Process manually downloaded IPL 2024 data
Reads JSON files from data/raw/ipl_2024/ and creates processed CSV
"""

import pandas as pd
import json
import yaml
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
IPL_RAW_DIR = Path("data/raw/ipl_2024")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def parse_match_file(file_path):
    """Parse single match file (JSON or YAML)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix == '.json':
                data = json.load(f)
            elif file_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                return None
        return data
    except Exception as e:
        logger.warning(f"Failed to parse {file_path.name}: {e}")
        return None


def extract_match_info(match_data):
    """Extract basic match information"""
    if not match_data or 'info' not in match_data:
        return None
    
    info = match_data['info']
    
    # Check if it's IPL 2024
    event = info.get('event', {})
    if isinstance(event, dict):
        tournament = event.get('name', '')
    else:
        tournament = str(event) if event else ''
    
    # Filter for IPL 2024
    if 'Indian Premier League' not in tournament:
        return None
    
    season = info.get('season', '')
    if season != '2024':
        return None
    
    teams = info.get('teams', [])
    dates = info.get('dates', [''])
    
    # Get outcome
    outcome = info.get('outcome', {})
    winner = outcome.get('winner', '')
    
    # Get margin
    if 'by' in outcome:
        by_info = outcome['by']
        if 'runs' in by_info:
            margin_type = 'runs'
            margin_value = by_info['runs']
        elif 'wickets' in by_info:
            margin_type = 'wickets'
            margin_value = by_info['wickets']
        else:
            margin_type = ''
            margin_value = 0
    else:
        margin_type = ''
        margin_value = 0
    
    # Get toss info
    toss = info.get('toss', {})
    
    # Get umpires
    umpires = info.get('umpires', [])
    
    # Get player of match
    pom = info.get('player_of_match', [])
    
    match_info = {
        'match_id': info.get('match_id', ''),
        'tournament': tournament,
        'season': season,
        'match_date': dates[0] if dates else '',
        'venue': info.get('venue', ''),
        'city': info.get('city', ''),
        'team1': teams[0] if len(teams) > 0 else '',
        'team2': teams[1] if len(teams) > 1 else '',
        'toss_winner': toss.get('winner', ''),
        'toss_decision': toss.get('decision', ''),
        'winner': winner,
        'margin_type': margin_type,
        'margin_value': margin_value,
        'player_of_match': pom[0] if pom else '',
        'umpire1': umpires[0] if len(umpires) > 0 else '',
        'umpire2': umpires[1] if len(umpires) > 1 else '',
        'match_type': info.get('match_type', ''),
        'gender': info.get('gender', '')
    }
    
    return match_info


def process_ipl_data():
    """Process all IPL files in raw directory"""
    
    logger.info(f"Looking for IPL files in: {IPL_RAW_DIR}")
    
    if not IPL_RAW_DIR.exists():
        logger.error(f"Directory not found: {IPL_RAW_DIR}")
        logger.info("Please ensure IPL data is extracted to data/raw/ipl_2024/")
        return
    
    # Find all JSON/YAML files
    json_files = list(IPL_RAW_DIR.glob("**/*.json"))
    yaml_files = list(IPL_RAW_DIR.glob("**/*.yaml")) + list(IPL_RAW_DIR.glob("**/*.yml"))
    all_files = json_files + yaml_files
    
    logger.info(f"Found {len(all_files)} total files")
    logger.info(f"  - JSON files: {len(json_files)}")
    logger.info(f"  - YAML files: {len(yaml_files)}")
    
    if len(all_files) == 0:
        logger.error("No match files found!")
        logger.info("\nExpected structure:")
        logger.info("  data/raw/ipl_2024/")
        logger.info("    ├── 1234567.json")
        logger.info("    ├── 1234568.json")
        logger.info("    └── ...")
        return
    
    # Process each file
    all_matches = []
    processed_count = 0
    skipped_count = 0
    
    for file_path in all_files:
        match_data = parse_match_file(file_path)
        if not match_data:
            skipped_count += 1
            continue
        
        match_info = extract_match_info(match_data)
        if match_info:
            all_matches.append(match_info)
            processed_count += 1
        else:
            skipped_count += 1
    
    logger.info(f"\nProcessing complete:")
    logger.info(f"  - Processed: {processed_count} IPL 2024 matches")
    logger.info(f"  - Skipped: {skipped_count} files (other tournaments/seasons)")
    
    if len(all_matches) == 0:
        logger.warning("No IPL 2024 matches found in files!")
        logger.info("This could mean:")
        logger.info("  1. Files are from different seasons")
        logger.info("  2. Files are not IPL matches")
        logger.info("  3. File format is different than expected")
        return
    
    # Create DataFrame
    df = pd.DataFrame(all_matches)
    
    # Save to CSV
    output_file = PROCESSED_DIR / "ipl_2024_matches.csv"
    df.to_csv(output_file, index=False)
    
    logger.info(f"\n✅ Saved IPL data to: {output_file}")
    
    # Show summary
    logger.info(f"\n📊 IPL 2024 Summary:")
    logger.info(f"  - Total matches: {len(df)}")
    logger.info(f"  - Date range: {df['match_date'].min()} to {df['match_date'].max()}")
    logger.info(f"  - Venues: {df['venue'].nunique()}")
    logger.info(f"  - Teams: {len(set(df['team1'].tolist() + df['team2'].tolist()))}")
    
    # Show top teams
    if 'winner' in df.columns:
        top_teams = df['winner'].value_counts().head(5)
        logger.info(f"\n🏆 Top 5 Teams by Wins:")
        for team, wins in top_teams.items():
            logger.info(f"  - {team}: {wins} wins")
    
    return df


if __name__ == "__main__":
    logger.info("="*60)
    logger.info("🏏 PROCESSING IPL 2024 DATA")
    logger.info("="*60)
    
    df = process_ipl_data()
    
    if df is not None:
        logger.info("\n" + "="*60)
        logger.info("✅ IPL DATA PROCESSING COMPLETE!")
        logger.info("="*60)
        logger.info(f"\n📁 Output file: data/processed/ipl_2024_matches.csv")
        logger.info(f"📊 Total matches: {len(df)}")
        logger.info("\nNext steps:")
        logger.info("1. Check the CSV file")
        logger.info("2. Load data into database")
        logger.info("3. Start building analysis pages")
    else:
        logger.info("\n" + "="*60)
        logger.info("❌ NO IPL DATA PROCESSED")
        logger.info("="*60)
        logger.info("\nTroubleshooting:")
        logger.info("1. Verify files are in: data/raw/ipl_2024/")
        logger.info("2. Check file format (should be JSON or YAML)")
        logger.info("3. Ensure files are IPL 2024 matches")