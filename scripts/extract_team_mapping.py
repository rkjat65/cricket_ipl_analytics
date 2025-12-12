"""
Extract Team ID to Name Mapping
Uses ball-by-ball data to create team ID mapping
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

BALL_DATA = Path("data/raw/ipl_2024/all_ball_by_ball_data.csv")
OUTPUT_FILE = Path("data/processed/team_mapping.csv")


def extract_team_mapping():
    """Extract team ID to name mapping from ball-by-ball data"""
    logger.info("\n" + "="*70)
    logger.info("🏏 TEAM ID MAPPING EXTRACTOR")
    logger.info("="*70)
    
    logger.info(f"\n📂 Loading ball-by-ball data...")
    
    if not BALL_DATA.exists():
        logger.error(f"❌ File not found: {BALL_DATA}")
        logger.info("This script needs: data/raw/ipl_2024/all_ball_by_ball_data.csv")
        return None
    
    # Read only necessary columns
    try:
        df = pd.read_csv(BALL_DATA, usecols=lambda x: 'team' in x.lower() or 'batting' in x.lower() or 'bowling' in x.lower())
    except:
        # If that fails, load all and find team columns
        df = pd.read_csv(BALL_DATA)
    
    logger.info(f"✅ Loaded {len(df):,} deliveries")
    logger.info(f"📋 Columns: {list(df.columns)}")
    
    # Find team-related columns
    team_columns = [col for col in df.columns if 'team' in col.lower()]
    logger.info(f"\n🔍 Found team columns: {team_columns}")
    
    # Extract unique team ID-name pairs
    team_mappings = {}
    
    for col in team_columns:
        # Check if this column has both ID and name info
        # Common patterns: 'batting_team', 'bowling_team', 'BattingTeam', etc.
        if col in df.columns:
            unique_teams = df[col].dropna().unique()
            logger.info(f"\n  {col}: {len(unique_teams)} unique values")
            
            # If values are strings (team names), not integers (IDs)
            if df[col].dtype == 'object':
                logger.info(f"    Sample: {list(unique_teams[:5])}")
    
    # Try to find team ID and team name columns
    id_col = None
    name_col = None
    
    # Look for common patterns
    possible_id_cols = ['team_id', 'batting_team_id', 'bowling_team_id']
    possible_name_cols = ['batting_team', 'bowling_team', 'BattingTeam', 'BowlingTeam']
    
    for col in possible_name_cols:
        if col in df.columns and df[col].dtype == 'object':
            name_col = col
            break
    
    if name_col:
        # Get unique team names
        teams = sorted(df[name_col].dropna().unique())
        
        logger.info(f"\n✅ Found {len(teams)} unique teams:")
        for i, team in enumerate(teams, 1):
            logger.info(f"  {i:2d}. {team}")
        
        # Create mapping DataFrame
        team_df = pd.DataFrame({
            'team_id': range(1, len(teams) + 1),
            'team_name': teams
        })
        
        # Save mapping
        team_df.to_csv(OUTPUT_FILE, index=False)
        logger.info(f"\n💾 Saved team mapping to: {OUTPUT_FILE}")
        
        return team_df
    else:
        logger.warning("\n⚠️ Could not find team name column in ball-by-ball data")
        logger.info("Available columns: " + ", ".join(df.columns))
        return None


def main():
    """Main execution"""
    mapping = extract_team_mapping()
    
    if mapping is not None:
        logger.info(f"\n" + "="*70)
        logger.info("🎉 TEAM MAPPING CREATED!")
        logger.info("="*70)
        logger.info(f"\n📊 Next: Use this mapping to add team names to match data")
    else:
        logger.info(f"\n" + "="*70)
        logger.info("⚠️ Could not create automatic mapping")
        logger.info("="*70)
        logger.info(f"\nYou may need to manually create team_mapping.csv with:")
        logger.info(f"  - team_id (1, 2, 3...)")
        logger.info(f"  - team_name (Mumbai Indians, Chennai Super Kings, etc.)")


if __name__ == "__main__":
    main()