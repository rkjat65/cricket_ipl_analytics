"""
Merge 2020 Data and Add Team Names
Combines Kaggle data + 2020 Cricsheet data + team mapping
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")


def load_existing_data():
    """Load existing processed data"""
    logger.info("\n" + "="*70)
    logger.info("🔄 MERGING 2020 DATA & ADDING TEAM NAMES")
    logger.info("="*70)
    
    existing_file = PROCESSED_DIR / "ipl_all_years_combined.csv"
    
    if not existing_file.exists():
        logger.error("❌ Existing data not found!")
        return None
    
    df = pd.read_csv(existing_file)
    logger.info(f"✅ Loaded existing data: {len(df)} matches")
    
    return df


def load_2020_data():
    """Load 2020 Cricsheet data"""
    file_2020 = PROCESSED_DIR / "ipl_2020_matches_cricsheet.csv"
    
    if not file_2020.exists():
        logger.error("❌ 2020 data not found!")
        logger.info("Run: python scripts/extract_2020_and_teams.py first")
        return None
    
    df = pd.read_csv(file_2020)
    logger.info(f"✅ Loaded 2020 data: {len(df)} matches")
    
    return df


def load_team_mapping():
    """Load team mapping"""
    mapping_file = PROCESSED_DIR / "team_mapping.csv"
    
    if not mapping_file.exists():
        logger.warning("⚠️ Team mapping not found")
        return None
    
    df = pd.read_csv(mapping_file)
    logger.info(f"✅ Loaded team mapping: {len(df)} teams")
    
    return df


def add_team_names(df: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """Add team names using mapping"""
    if mapping is None:
        logger.warning("⚠️ Skipping team name addition (no mapping)")
        return df
    
    logger.info(f"\n🔧 Adding team names...")
    
    # Create mapping dictionary
    id_to_name = dict(zip(mapping['team_id'], mapping['team_name']))
    
    # Add team names
    df['team1_name'] = df['team1'].map(id_to_name)
    df['team2_name'] = df['team2'].map(id_to_name)
    df['toss_winner_name'] = df['toss_winner'].map(id_to_name)
    df['match_winner_name'] = df['match_winner'].map(id_to_name)
    
    logger.info(f"✅ Added team name columns")
    
    return df


def align_2020_with_existing(df_2020: pd.DataFrame, df_existing: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """Align 2020 data structure with existing data"""
    logger.info(f"\n🔧 Aligning 2020 data structure...")
    
    # 2020 has team names, need to convert to IDs
    if mapping is not None and 'team1' in df_2020.columns:
        # Check if team1 is string (name) or int (ID)
        if df_2020['team1'].dtype == 'object':
            logger.info("  Converting team names to IDs...")
            
            name_to_id = dict(zip(mapping['team_name'], mapping['team_id']))
            
            df_2020['team1_name'] = df_2020['team1']
            df_2020['team2_name'] = df_2020['team2']
            df_2020['toss_winner_name'] = df_2020['toss_winner']
            df_2020['match_winner_name'] = df_2020['match_winner']
            
            df_2020['team1'] = df_2020['team1_name'].map(name_to_id)
            df_2020['team2'] = df_2020['team2_name'].map(name_to_id)
            df_2020['toss_winner'] = df_2020['toss_winner_name'].map(name_to_id)
            df_2020['match_winner'] = df_2020['match_winner_name'].map(name_to_id)
    
    # Align columns
    for col in df_existing.columns:
        if col not in df_2020.columns:
            df_2020[col] = None
    
    # Ensure same column order
    df_2020 = df_2020[df_existing.columns]
    
    logger.info(f"✅ Aligned structure")
    
    return df_2020


def merge_datasets(df_existing: pd.DataFrame, df_2020: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """Merge existing and 2020 data"""
    logger.info(f"\n🔄 Merging datasets...")
    
    # Align 2020 structure
    df_2020_aligned = align_2020_with_existing(df_2020, df_existing, mapping)
    
    # Combine
    df_combined = pd.concat([df_existing, df_2020_aligned], ignore_index=True)
    
    # Sort by season and date
    df_combined = df_combined.sort_values(['season', 'match_date'], ignore_index=True)
    
    logger.info(f"✅ Merged: {len(df_combined)} total matches")
    logger.info(f"  - Original: {len(df_existing)}")
    logger.info(f"  - Added 2020: {len(df_2020_aligned)}")
    
    return df_combined


def save_final_dataset(df: pd.DataFrame):
    """Save final complete dataset"""
    logger.info(f"\n💾 Saving final dataset...")
    
    # Save combined
    combined_file = PROCESSED_DIR / "ipl_all_years_combined_FINAL.csv"
    df.to_csv(combined_file, index=False)
    logger.info(f"✅ Saved: {combined_file.name}")
    
    # Save 2020 separately
    df_2020 = df[df['season'] == '2020']
    if len(df_2020) > 0:
        file_2020 = PROCESSED_DIR / "ipl_2020_matches.csv"
        df_2020.to_csv(file_2020, index=False)
        logger.info(f"✅ Saved: {file_2020.name}")


def generate_final_report(df: pd.DataFrame):
    """Generate final completeness report"""
    logger.info(f"\n" + "="*70)
    logger.info("📊 FINAL DATA REPORT")
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
    complete = 0
    
    for season in sorted(EXPECTED_COUNTS.keys()):
        expected = EXPECTED_COUNTS[season]
        actual = len(df[df['season'] == season])
        
        total_actual += actual
        total_expected += expected
        
        if actual == expected:
            status = '✅'
            complete += 1
        elif actual == 0:
            status = '❌ MISSING'
        elif abs(actual - expected) <= 3:
            status = '⚠️'
        else:
            status = '❌'
        
        if actual > 0:
            logger.info(f"{season:<10} {actual:<10} {expected:<10} {status}")
    
    logger.info("-" * 50)
    logger.info(f"{'TOTAL':<10} {total_actual:<10} {total_expected:<10}")
    
    completeness = (total_actual / total_expected * 100)
    
    logger.info(f"\n📈 Final Completeness: {completeness:.1f}%")
    logger.info(f"✅ Complete seasons: {complete}/18")
    
    # Grade
    if completeness >= 98:
        grade = "A+ (Excellent)"
    elif completeness >= 95:
        grade = "A (Very Good)"
    elif completeness >= 90:
        grade = "B (Good)"
    else:
        grade = "C (Fair)"
    
    logger.info(f"\n🎯 Final Grade: {grade}")
    
    logger.info(f"\n✅ Dataset ready for:")
    logger.info(f"  - Database loading")
    logger.info(f"  - Dashboard creation")
    logger.info(f"  - Statistical analysis")
    logger.info(f"  - Portfolio showcase!")


def main():
    """Main execution"""
    
    # Load data
    df_existing = load_existing_data()
    if df_existing is None:
        return
    
    df_2020 = load_2020_data()
    if df_2020 is None:
        return
    
    mapping = load_team_mapping()
    
    # Add team names to existing data
    if mapping is not None:
        df_existing = add_team_names(df_existing, mapping)
    
    # Merge datasets
    df_final = merge_datasets(df_existing, df_2020, mapping)
    
    # Add team names to final
    if mapping is not None:
        df_final = add_team_names(df_final, mapping)
    
    # Save
    save_final_dataset(df_final)
    
    # Report
    generate_final_report(df_final)
    
    logger.info(f"\n" + "="*70)
    logger.info("🎉 MERGE COMPLETE!")
    logger.info("="*70)
    logger.info(f"\n📁 Final file: data/processed/ipl_all_years_combined_FINAL.csv")


if __name__ == "__main__":
    main()