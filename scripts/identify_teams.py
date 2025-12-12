"""
Team ID Identifier
Analyzes match patterns to identify unknown team IDs
"""

import pandas as pd
from pathlib import Path
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
FINAL_FILE = PROCESSED_DIR / "ipl_all_years_FINAL.csv"


def analyze_team_patterns():
    """Analyze team ID patterns to identify teams"""
    logger.info("\n" + "="*70)
    logger.info("🔍 TEAM ID DETECTIVE")
    logger.info("="*70)
    
    df = pd.read_csv(FINAL_FILE)
    
    # Get all unique team IDs
    all_ids = sorted(set(df['team1'].tolist() + df['team2'].tolist()))
    
    logger.info(f"\n📊 Found {len(all_ids)} unique team IDs:")
    logger.info(f"IDs: {all_ids}")
    
    # Unknown IDs
    unknown_ids = [614, 615, 1414, 1419]
    
    logger.info(f"\n🔍 Analyzing unknown IDs: {unknown_ids}")
    logger.info("="*70)
    
    for team_id in unknown_ids:
        logger.info(f"\n{'='*70}")
        logger.info(f"TEAM ID: {team_id}")
        logger.info(f"{'='*70}")
        
        # Get matches for this team
        team_matches = df[(df['team1'] == team_id) | (df['team2'] == team_id)]
        
        logger.info(f"\n📊 Statistics:")
        logger.info(f"  - Total matches: {len(team_matches)}")
        logger.info(f"  - Seasons active: {sorted(team_matches['season'].unique())}")
        logger.info(f"  - Date range: {team_matches['match_date'].min()} to {team_matches['match_date'].max()}")
        
        # Venues (gives clue about home ground)
        logger.info(f"\n🏟️ Top 5 Venues:")
        venues = team_matches['venue'].value_counts().head(5)
        for venue, count in venues.items():
            logger.info(f"  - {venue}: {count} matches")
        
        # Cities
        logger.info(f"\n🏙️ Top 3 Cities:")
        cities = team_matches['city'].dropna().value_counts().head(3)
        for city, count in cities.items():
            logger.info(f"  - {city}: {count} matches")
        
        # Opponents (see which teams they play most)
        logger.info(f"\n⚔️ Most Common Opponents:")
        opponents = []
        for _, row in team_matches.iterrows():
            if row['team1'] == team_id:
                opponents.append(row['team2'])
            else:
                opponents.append(row['team1'])
        
        opponent_counts = Counter(opponents).most_common(5)
        for opp_id, count in opponent_counts:
            logger.info(f"  - Team ID {opp_id}: {count} matches")
        
        # Win rate
        wins = len(team_matches[team_matches['match_winner'] == team_id])
        total = len(team_matches)
        win_pct = (wins / total * 100) if total > 0 else 0
        logger.info(f"\n🏆 Performance:")
        logger.info(f"  - Wins: {wins}/{total} ({win_pct:.1f}%)")


def provide_identification_hints():
    """Provide hints for team identification"""
    logger.info(f"\n" + "="*70)
    logger.info("💡 IDENTIFICATION HINTS")
    logger.info("="*70)
    
    logger.info(f"\n🏏 Known IPL Teams by Era:")
    logger.info(f"\n2008-2010:")
    logger.info(f"  - Chennai Super Kings, Mumbai Indians, Kolkata Knight Riders")
    logger.info(f"  - Royal Challengers Bangalore, Rajasthan Royals")
    logger.info(f"  - Delhi Daredevils (now Delhi Capitals)")
    logger.info(f"  - Kings XI Punjab (now Punjab Kings)")
    logger.info(f"  - Deccan Chargers (defunct)")
    
    logger.info(f"\n2011-2012:")
    logger.info(f"  + Pune Warriors (defunct)")
    logger.info(f"  + Kochi Tuskers Kerala (defunct, only 2011)")
    
    logger.info(f"\n2013-2015:")
    logger.info(f"  - Deccan Chargers → Sunrisers Hyderabad (2013)")
    
    logger.info(f"\n2016-2017:")
    logger.info(f"  + Gujarat Lions (2016-2017 only)")
    logger.info(f"  + Rising Pune Supergiant (2016-2017 only)")
    logger.info(f"  - Chennai Super Kings (banned 2016-2017)")
    logger.info(f"  - Rajasthan Royals (banned 2016-2017)")
    
    logger.info(f"\n2018-2021:")
    logger.info(f"  - CSK, RR returned")
    logger.info(f"  - Delhi Daredevils → Delhi Capitals (2019)")
    
    logger.info(f"\n2022+:")
    logger.info(f"  + Gujarat Titans (2022+)")
    logger.info(f"  + Lucknow Super Giants (2022+)")
    logger.info(f"  - Kings XI Punjab → Punjab Kings (2021)")
    logger.info(f"  - RCB → Royal Challengers Bengaluru (2024)")
    
    logger.info(f"\n🎯 CLUES TO USE:")
    logger.info(f"  1. Check seasons active (helps identify temporary teams)")
    logger.info(f"  2. Check home venues/cities")
    logger.info(f"  3. If active 2016-2017 only → Gujarat Lions or Rising Pune Supergiant")
    logger.info(f"  4. If active 2022+ → Gujarat Titans or Lucknow Super Giants")
    logger.info(f"  5. If only 2011 → Kochi Tuskers Kerala")


def suggest_mapping():
    """Suggest team mapping based on analysis"""
    logger.info(f"\n" + "="*70)
    logger.info("🎯 SUGGESTED MAPPING")
    logger.info("="*70)
    
    df = pd.read_csv(FINAL_FILE)
    
    logger.info(f"\nBased on the analysis above, here are likely identifications:")
    logger.info(f"\n  614 → Check seasons & home city")
    logger.info(f"  615 → Check seasons & home city")
    logger.info(f"  1414 → Check seasons & venues")
    logger.info(f"  1419 → Check seasons & venues")
    
    logger.info(f"\n📝 TO IDENTIFY:")
    logger.info(f"  1. Look at the analysis output above")
    logger.info(f"  2. Match seasons + cities with team history")
    logger.info(f"  3. Update the mapping manually")
    
    logger.info(f"\n💡 COMMON PATTERNS:")
    logger.info(f"  - Active 2016-2017 only → GL or RPS")
    logger.info(f"  - Active 2022+ → GT or LSG")
    logger.info(f"  - Consistent through 2008-2025 → Major franchises")
    logger.info(f"  - Home in Bangalore → RCB")
    logger.info(f"  - Home in Hyderabad → SRH")


def main():
    """Main execution"""
    
    # Analyze patterns
    analyze_team_patterns()
    
    # Provide hints
    provide_identification_hints()
    
    # Suggest mapping
    suggest_mapping()
    
    logger.info(f"\n" + "="*70)
    logger.info("🔍 ANALYSIS COMPLETE")
    logger.info("="*70)
    logger.info(f"\nUse the information above to identify:")
    logger.info(f"  - Team ID 614")
    logger.info(f"  - Team ID 615")
    logger.info(f"  - Team ID 1414")
    logger.info(f"  - Team ID 1419")


if __name__ == "__main__":
    main()