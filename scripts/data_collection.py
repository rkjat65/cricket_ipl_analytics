"""
Data Collection Script for Cricket Analytics
Downloads and processes data from Cricsheet and other sources
"""

import pandas as pd
import requests
from pathlib import Path
import zipfile
import json
import logging
from typing import List, Dict, Any
import yaml
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Create directories
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


class CricsheetDownloader:
    """
    Download cricket data from Cricsheet
    Website: https://cricsheet.org/
    """
    
    BASE_URL = "https://cricsheet.org/downloads"
    
    def __init__(self):
        self.session = requests.Session()
        
    def download_ipl_data(self, year: int = 2024) -> Path:
        """
        Download IPL data for specified year
        
        Args:
            year: IPL season year
            
        Returns:
            Path to downloaded file
        """
        
        # Cricsheet IPL data URLs (format may vary)
        url = f"{self.BASE_URL}/ipl_{year}_json.zip"
        
        logger.info(f"Downloading IPL {year} data from {url}")
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            output_file = RAW_DATA_DIR / f"ipl_{year}.zip"
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded: {output_file}")
            
            # Extract zip
            extract_dir = RAW_DATA_DIR / f"ipl_{year}"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(output_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info(f"Extracted to: {extract_dir}")
            
            return extract_dir
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise
    
    def download_t20wc_data(self, year: int = 2024) -> Path:
        """
        Download T20 World Cup data
        
        Args:
            year: World Cup year
            
        Returns:
            Path to downloaded file
        """
        
        url = f"{self.BASE_URL}/t20s_json.zip"  # May contain multiple years
        
        logger.info(f"Downloading T20 World Cup data from {url}")
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            output_file = RAW_DATA_DIR / "t20wc_all.zip"
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded: {output_file}")
            
            # Extract
            extract_dir = RAW_DATA_DIR / "t20wc"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(output_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info(f"Extracted to: {extract_dir}")
            
            return extract_dir
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise


class CricsheetParser:
    """
    Parse Cricsheet JSON/YAML files into structured data
    """
    
    @staticmethod
    def parse_match_file(file_path: Path) -> Dict[str, Any]:
        """
        Parse single match file (JSON or YAML)
        
        Args:
            file_path: Path to match file
            
        Returns:
            Parsed match data dictionary
        """
        
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix == '.json':
                    data = json.load(f)
                elif file_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return {}
    
    @staticmethod
    def extract_match_info(match_data: Dict) -> Dict:
        """Extract basic match information"""
        
        info = match_data.get('info', {})
        
        return {
            'match_id': info.get('match_id', ''),
            'tournament': info.get('event', {}).get('name', ''),
            'season': info.get('season', ''),
            'match_date': info.get('dates', [''])[0] if info.get('dates') else '',
            'venue': info.get('venue', ''),
            'team1': info.get('teams', ['', ''])[0],
            'team2': info.get('teams', ['', ''])[1] if len(info.get('teams', [])) > 1 else '',
            'toss_winner': info.get('toss', {}).get('winner', ''),
            'toss_decision': info.get('toss', {}).get('decision', ''),
            'winner': info.get('outcome', {}).get('winner', ''),
            'player_of_match': info.get('player_of_match', [''])[0] if info.get('player_of_match') else '',
            'umpires': info.get('umpires', [])
        }
    
    @staticmethod
    def extract_innings_data(match_data: Dict) -> List[Dict]:
        """Extract ball-by-ball innings data"""
        
        innings_list = []
        
        for inning in match_data.get('innings', []):
            team = inning.get('team', '')
            
            for over in inning.get('overs', []):
                over_num = over.get('over', 0)
                
                for delivery in over.get('deliveries', []):
                    innings_list.append({
                        'team': team,
                        'over': over_num,
                        'batter': delivery.get('batter', ''),
                        'bowler': delivery.get('bowler', ''),
                        'non_striker': delivery.get('non_striker', ''),
                        'runs_batter': delivery.get('runs', {}).get('batter', 0),
                        'runs_extras': delivery.get('runs', {}).get('extras', 0),
                        'runs_total': delivery.get('runs', {}).get('total', 0),
                        'wickets': delivery.get('wickets', [])
                    })
        
        return innings_list
    
    def process_directory(self, directory: Path, tournament_filter: str = None) -> pd.DataFrame:
        """
        Process all match files in directory
        
        Args:
            directory: Directory containing match files
            tournament_filter: Filter by tournament name (optional)
            
        Returns:
            DataFrame with all matches
        """
        
        all_matches = []
        
        match_files = list(directory.glob('**/*.json')) + list(directory.glob('**/*.yaml'))
        
        logger.info(f"Found {len(match_files)} match files")
        
        for file_path in match_files:
            try:
                match_data = self.parse_match_file(file_path)
                
                if not match_data:
                    continue
                
                match_info = self.extract_match_info(match_data)
                
                # Filter by tournament if specified
                if tournament_filter and tournament_filter.lower() not in match_info['tournament'].lower():
                    continue
                
                all_matches.append(match_info)
                
            except Exception as e:
                logger.warning(f"Skipping {file_path}: {e}")
                continue
        
        df = pd.DataFrame(all_matches)
        logger.info(f"Processed {len(df)} matches")
        
        return df


def main():
    """Main data collection workflow"""
    
    logger.info("Starting data collection...")
    
    # Initialize downloaders
    downloader = CricsheetDownloader()
    parser = CricsheetParser()
    
    # Download IPL 2024 data
    logger.info("\n=== Downloading IPL 2024 Data ===")
    try:
        ipl_dir = downloader.download_ipl_data(2024)
        
        # Process IPL data
        ipl_df = parser.process_directory(ipl_dir, tournament_filter="Indian Premier League")
        
        # Save processed data
        ipl_output = PROCESSED_DATA_DIR / "ipl_2024_matches.csv"
        ipl_df.to_csv(ipl_output, index=False)
        logger.info(f"Saved IPL data to {ipl_output}")
        
    except Exception as e:
        logger.error(f"IPL data collection failed: {e}")
    
    # Download T20 World Cup 2024 data
    logger.info("\n=== Downloading T20 World Cup 2024 Data ===")
    try:
        t20wc_dir = downloader.download_t20wc_data(2024)
        
        # Process T20 WC data
        t20wc_df = parser.process_directory(t20wc_dir, tournament_filter="ICC Men's T20 World Cup")
        
        # Save processed data
        t20wc_output = PROCESSED_DATA_DIR / "t20wc_2024_matches.csv"
        t20wc_df.to_csv(t20wc_output, index=False)
        logger.info(f"Saved T20 WC data to {t20wc_output}")
        
    except Exception as e:
        logger.error(f"T20 WC data collection failed: {e}")
    
    logger.info("\n=== Data Collection Complete ===")


if __name__ == "__main__":
    # Run data collection
    main()
    
    print("\n" + "="*60)
    print("✅ DATA COLLECTION COMPLETED")
    print("="*60)
    print(f"\n📁 Raw data saved in: {RAW_DATA_DIR}")
    print(f"📊 Processed data saved in: {PROCESSED_DATA_DIR}")
    print("\nNext steps:")
    print("1. Check the processed CSV files")
    print("2. Run data cleaning scripts")
    print("3. Load data into database using utils/database.py")
