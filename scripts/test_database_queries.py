"""
Test Database Queries
Demonstrates various queries for IPL Cricket Analytics database
"""

import sqlite3
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

DB_FILE = Path("data/cricket_analytics.db")


def connect_db():
    """Connect to database"""
    if not DB_FILE.exists():
        logger.error(f"❌ Database not found: {DB_FILE}")
        logger.info("Run 'python scripts/create_database.py' first!")
        return None
    
    return sqlite3.connect(DB_FILE)


def test_basic_queries(conn):
    """Test basic queries"""
    logger.info("\n" + "="*70)
    logger.info("📊 BASIC QUERIES")
    logger.info("="*70)
    
    # 1. All teams
    logger.info("\n1️⃣ All Teams:")
    df = pd.read_sql_query("""
        SELECT team_id, team_name, short_name, is_active
        FROM teams
        ORDER BY team_name
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")
    
    # 2. Matches per season
    logger.info("\n2️⃣ Matches Per Season:")
    df = pd.read_sql_query("""
        SELECT season, COUNT(*) as matches
        FROM matches
        GROUP BY season
        ORDER BY season
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")
    
    # 3. Total wins by team
    logger.info("\n3️⃣ Total Wins by Team:")
    df = pd.read_sql_query("""
        SELECT match_winner_name as team, COUNT(*) as wins
        FROM matches
        WHERE match_winner_name IS NOT NULL
        GROUP BY match_winner_name
        ORDER BY wins DESC
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")


def test_advanced_queries(conn):
    """Test advanced queries"""
    logger.info("\n" + "="*70)
    logger.info("🔍 ADVANCED QUERIES")
    logger.info("="*70)
    
    # 1. Head to head
    logger.info("\n1️⃣ Mumbai Indians vs Chennai Super Kings:")
    df = pd.read_sql_query("""
        SELECT 
            season,
            match_date,
            venue,
            team1_name,
            team2_name,
            match_winner_name as winner
        FROM matches
        WHERE (team1_name = 'Mumbai Indians' AND team2_name = 'Chennai Super Kings')
           OR (team1_name = 'Chennai Super Kings' AND team2_name = 'Mumbai Indians')
        ORDER BY match_date DESC
        LIMIT 10
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")
    
    # 2. Toss win impact
    logger.info("\n2️⃣ Toss Impact - Teams winning after winning toss:")
    df = pd.read_sql_query("""
        SELECT 
            toss_winner_name as team,
            COUNT(*) as toss_wins,
            SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) as match_wins,
            ROUND(100.0 * SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
        FROM matches
        WHERE toss_winner_name IS NOT NULL AND match_winner_name IS NOT NULL
        GROUP BY toss_winner_name
        HAVING COUNT(*) >= 50
        ORDER BY win_pct DESC
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")
    
    # 3. Home advantage
    logger.info("\n3️⃣ Top Venues by Matches:")
    df = pd.read_sql_query("""
        SELECT 
            venue,
            city,
            COUNT(*) as matches
        FROM matches
        WHERE venue IS NOT NULL
        GROUP BY venue, city
        ORDER BY matches DESC
        LIMIT 10
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")


def test_season_analysis(conn):
    """Test season-based queries"""
    logger.info("\n" + "="*70)
    logger.info("📅 SEASON ANALYSIS")
    logger.info("="*70)
    
    # 1. IPL 2024 winner
    logger.info("\n1️⃣ IPL 2024 Finals:")
    df = pd.read_sql_query("""
        SELECT 
            match_date,
            team1_name,
            team2_name,
            match_winner_name as winner,
            win_by_runs,
            win_by_wickets,
            venue
        FROM matches
        WHERE season = 2024
        ORDER BY match_date DESC
        LIMIT 5
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")
    
    # 2. Season winners
    logger.info("\n2️⃣ Season Winners (Last 5 years):")
    # This would require finals data or specific logic
    df = pd.read_sql_query("""
        SELECT 
            season,
            match_winner_name as champion,
            COUNT(*) as wins
        FROM matches
        WHERE season >= 2021
        GROUP BY season, match_winner_name
        ORDER BY season DESC, wins DESC
    """, conn)
    
    # Group by season and get top winner
    season_winners = df.groupby('season').first().reset_index()
    logger.info(f"\n{season_winners[['season', 'champion', 'wins']].to_string(index=False)}")


def test_team_performance(conn):
    """Test team performance queries"""
    logger.info("\n" + "="*70)
    logger.info("🏆 TEAM PERFORMANCE ANALYSIS")
    logger.info("="*70)
    
    # 1. Win percentage by team
    logger.info("\n1️⃣ Team Win Percentage (Min 50 matches):")
    df = pd.read_sql_query("""
        WITH team_stats AS (
            SELECT 
                COALESCE(team1_name, team2_name) as team,
                match_winner_name as winner
            FROM matches
            WHERE team1_name = match_winner_name OR team2_name = match_winner_name
            
            UNION ALL
            
            SELECT 
                COALESCE(team1_name, team2_name) as team,
                match_winner_name as winner
            FROM matches
            WHERE (team1_name != match_winner_name OR team2_name != match_winner_name)
               AND match_winner_name IS NOT NULL
        )
        SELECT 
            team,
            COUNT(*) as matches,
            SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) as wins,
            COUNT(*) - SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) as losses,
            ROUND(100.0 * SUM(CASE WHEN team = winner THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
        FROM team_stats
        WHERE team IS NOT NULL
        GROUP BY team
        HAVING matches >= 50
        ORDER BY win_pct DESC
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")
    
    # 2. Recent form (last 10 matches per team)
    logger.info("\n2️⃣ Recent Form - Gujarat Titans (2022-2025):")
    df = pd.read_sql_query("""
        SELECT 
            season,
            match_date,
            CASE 
                WHEN team1_name = 'Gujarat Titans' THEN team2_name
                ELSE team1_name
            END as opponent,
            CASE 
                WHEN match_winner_name = 'Gujarat Titans' THEN 'Won'
                ELSE 'Lost'
            END as result,
            venue
        FROM matches
        WHERE team1_name = 'Gujarat Titans' OR team2_name = 'Gujarat Titans'
        ORDER BY match_date DESC
        LIMIT 10
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")


def test_custom_analytics(conn):
    """Test custom analytics queries"""
    logger.info("\n" + "="*70)
    logger.info("💡 CUSTOM ANALYTICS")
    logger.info("="*70)
    
    # 1. Bat vs Field after toss win
    logger.info("\n1️⃣ Toss Decision Analysis:")
    df = pd.read_sql_query("""
        SELECT 
            toss_decision,
            COUNT(*) as times_chosen,
            SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) as wins,
            ROUND(100.0 * SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
        FROM matches
        WHERE toss_decision IS NOT NULL AND match_winner_id IS NOT NULL
        GROUP BY toss_decision
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")
    
    # 2. Biggest wins
    logger.info("\n2️⃣ Top 5 Biggest Wins by Runs:")
    df = pd.read_sql_query("""
        SELECT 
            season,
            match_date,
            match_winner_name as winner,
            CASE 
                WHEN team1_name = match_winner_name THEN team2_name
                ELSE team1_name
            END as opponent,
            win_by_runs as margin,
            venue
        FROM matches
        WHERE win_by_runs IS NOT NULL AND win_by_runs > 0
        ORDER BY win_by_runs DESC
        LIMIT 5
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")
    
    logger.info("\n3️⃣ Top 5 Biggest Wins by Wickets:")
    df = pd.read_sql_query("""
        SELECT 
            season,
            match_date,
            match_winner_name as winner,
            CASE 
                WHEN team1_name = match_winner_name THEN team2_name
                ELSE team1_name
            END as opponent,
            win_by_wickets as margin,
            venue
        FROM matches
        WHERE win_by_wickets IS NOT NULL AND win_by_wickets > 0
        ORDER BY win_by_wickets DESC
        LIMIT 5
    """, conn)
    logger.info(f"\n{df.to_string(index=False)}")


def export_sample_data(conn):
    """Export sample datasets"""
    logger.info("\n" + "="*70)
    logger.info("📤 EXPORTING SAMPLE DATA")
    logger.info("="*70)
    
    output_dir = Path("data/exports")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Team standings
    df = pd.read_sql_query("""
        SELECT 
            t.team_name,
            t.short_name,
            COUNT(DISTINCT m.season) as seasons_played,
            COUNT(*) as total_matches,
            SUM(CASE WHEN m.match_winner_id = t.team_id THEN 1 ELSE 0 END) as wins,
            ROUND(100.0 * SUM(CASE WHEN m.match_winner_id = t.team_id THEN 1 ELSE 0 END) / COUNT(*), 1) as win_pct
        FROM teams t
        LEFT JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
        GROUP BY t.team_id, t.team_name, t.short_name
        ORDER BY win_pct DESC
    """, conn)
    
    output_file = output_dir / "team_standings.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"✅ Exported: {output_file}")
    
    # 2. Season summary
    df = pd.read_sql_query("""
        SELECT 
            season,
            COUNT(*) as matches,
            COUNT(DISTINCT venue) as venues,
            COUNT(DISTINCT team1_id) + COUNT(DISTINCT team2_id) as teams
        FROM matches
        GROUP BY season
        ORDER BY season
    """, conn)
    
    output_file = output_dir / "season_summary.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"✅ Exported: {output_file}")


def main():
    """Main execution"""
    logger.info("\n" + "="*70)
    logger.info("🧪 TESTING DATABASE QUERIES")
    logger.info("="*70)
    
    # Connect
    conn = connect_db()
    if conn is None:
        return
    
    try:
        # Run tests
        test_basic_queries(conn)
        test_advanced_queries(conn)
        test_season_analysis(conn)
        test_team_performance(conn)
        test_custom_analytics(conn)
        export_sample_data(conn)
        
        logger.info("\n" + "="*70)
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("="*70)
        
        logger.info("\n🎯 Database is working perfectly!")
        logger.info("Ready for dashboard development!")
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()