"""
Database utility functions for cricket analytics
Handles SQLite database operations
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "database" / "cricket.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class CricketDatabase:
    """
    Database manager for cricket analytics data
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection"""
        self.db_path = db_path or DB_PATH
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def create_tables(self):
        """Create database schema"""
        
        # Matches table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY,
                tournament TEXT NOT NULL,
                season INTEGER,
                match_date DATE,
                venue TEXT,
                team1 TEXT NOT NULL,
                team2 TEXT NOT NULL,
                winner TEXT,
                margin_type TEXT,
                margin_value INTEGER,
                toss_winner TEXT,
                toss_decision TEXT,
                umpire1 TEXT,
                umpire2 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Ball-by-ball data
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                inning INTEGER,
                over INTEGER,
                ball INTEGER,
                batting_team TEXT,
                bowling_team TEXT,
                striker TEXT,
                non_striker TEXT,
                bowler TEXT,
                runs_off_bat INTEGER,
                extras INTEGER,
                wides INTEGER,
                noballs INTEGER,
                byes INTEGER,
                legbyes INTEGER,
                penalty INTEGER,
                wicket_type TEXT,
                player_dismissed TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        """)
        
        # Player statistics
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT UNIQUE NOT NULL,
                tournament TEXT,
                matches_played INTEGER DEFAULT 0,
                innings_batted INTEGER DEFAULT 0,
                runs_scored INTEGER DEFAULT 0,
                balls_faced INTEGER DEFAULT 0,
                fours INTEGER DEFAULT 0,
                sixes INTEGER DEFAULT 0,
                highest_score INTEGER DEFAULT 0,
                innings_bowled INTEGER DEFAULT 0,
                overs_bowled REAL DEFAULT 0,
                wickets_taken INTEGER DEFAULT 0,
                runs_conceded INTEGER DEFAULT 0,
                maidens INTEGER DEFAULT 0,
                best_bowling TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Team statistics
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_stats (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                tournament TEXT NOT NULL,
                matches_played INTEGER DEFAULT 0,
                matches_won INTEGER DEFAULT 0,
                matches_lost INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                nrr REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(team_name, tournament)
            )
        """)
        
        self.conn.commit()
        logger.info("Database tables created successfully")
    
    def insert_match(self, match_data: Dict[str, Any]) -> int:
        """Insert match data"""
        query = """
            INSERT INTO matches (
                match_id, tournament, season, match_date, venue,
                team1, team2, winner, margin_type, margin_value,
                toss_winner, toss_decision, umpire1, umpire2
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            match_data.get('match_id'),
            match_data.get('tournament'),
            match_data.get('season'),
            match_data.get('match_date'),
            match_data.get('venue'),
            match_data.get('team1'),
            match_data.get('team2'),
            match_data.get('winner'),
            match_data.get('margin_type'),
            match_data.get('margin_value'),
            match_data.get('toss_winner'),
            match_data.get('toss_decision'),
            match_data.get('umpire1'),
            match_data.get('umpire2')
        )
        
        self.cursor.execute(query, values)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def query_to_dataframe(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        try:
            if params:
                df = pd.read_sql_query(query, self.conn, params=params)
            else:
                df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def get_matches(self, tournament: Optional[str] = None) -> pd.DataFrame:
        """Retrieve matches data"""
        query = "SELECT * FROM matches"
        if tournament:
            query += " WHERE tournament = ?"
            return self.query_to_dataframe(query, (tournament,))
        return self.query_to_dataframe(query)
    
    def get_player_stats(self, tournament: Optional[str] = None) -> pd.DataFrame:
        """Retrieve player statistics"""
        query = "SELECT * FROM player_stats"
        if tournament:
            query += " WHERE tournament = ?"
            return self.query_to_dataframe(query, (tournament,))
        return self.query_to_dataframe(query)
    
    def get_team_stats(self, tournament: Optional[str] = None) -> pd.DataFrame:
        """Retrieve team statistics"""
        query = "SELECT * FROM team_stats"
        if tournament:
            query += " WHERE tournament = ?"
            return self.query_to_dataframe(query, (tournament,))
        return self.query_to_dataframe(query)
    
    def bulk_insert_dataframe(self, df: pd.DataFrame, table_name: str):
        """Insert DataFrame into table"""
        try:
            df.to_sql(table_name, self.conn, if_exists='append', index=False)
            logger.info(f"Inserted {len(df)} rows into {table_name}")
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise


# Convenience functions
def init_database():
    """Initialize database with schema"""
    with CricketDatabase() as db:
        db.create_tables()
    logger.info("Database initialized")


def get_db_connection():
    """Get database connection"""
    return CricketDatabase()


if __name__ == "__main__":
    # Test database creation
    init_database()
    print("Database initialized successfully!")
