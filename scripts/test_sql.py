import sqlite3
import pandas as pd

conn = sqlite3.connect("data/cricket_analytics.db")

# Check count
print(pd.read_sql_query("SELECT COUNT(*) as total FROM deliveries", conn))

# Top scorers
print(pd.read_sql_query("""
    SELECT batter, SUM(batter_runs) as runs 
    FROM deliveries 
    GROUP BY batter 
    ORDER BY runs DESC 
    LIMIT 5
""", conn))

conn.close()
