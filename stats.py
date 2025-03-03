import requests
import sqlite3
import pandas as pd
import json
import os
from dotenv import load_dotenv


load_dotenv()

JENKINS_URL         = os.getenv("JENKINS_URL")
JENKINS_USER        = os.getenv("JENKINS_USER")
JENKINS_API_TOKEN   = os.getenv("JENKINS_API_TOKEN")
DB_FILE             = os.getenv("DB_FILE")


# List of Jenkins jobs to track
JOBS = ["test"]

def query_stats():
    """ Fetches aggregated Jenkins stats from SQLite """
    conn = sqlite3.connect("jenkins_stats.db")
    
    query = """
        SELECT job_name, COUNT(*) AS total_builds, 
               AVG(duration) AS avg_duration, 
               SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) AS success_count, 
               SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END) AS failed_count
        FROM build_stats
        GROUP BY job_name;
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(df)

def get_jenkins_builds(job_name):
    """ Fetches the latest build stats for a job from Jenkins API """
    url = f"{JENKINS_URL}/job/{job_name}/api/json?tree=builds[number,result,duration,url]"
    response = requests.get(url, auth=(JENKINS_USER, JENKINS_API_TOKEN))

    if response.status_code == 200:
        return response.json().get("builds", [])
    else:
        print(f"⚠️ Failed to fetch data from {url}: {response.status_code}")
        return []

def save_to_sqlite(job_name, builds):
    """ Stores Jenkins build stats into SQLite """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for build in builds:
        build_number = build["number"]
        duration = build["duration"] // 1000  # Convert to seconds
        status = build["result"]

        cursor.execute("""
            INSERT INTO build_stats (job_name, build_number, status, duration)
            VALUES (?, ?, ?, ?);
        """, (job_name, build_number, status, duration))

    conn.commit()
    conn.close()

def main():
    """ Main function to extract and save Jenkins build stats """
    # for job in JOBS:
    #     builds = get_jenkins_builds(job)
    #     if builds:
    #         save_to_sqlite(job, builds)
    #         print(f"✅ Stats saved for {job}")
    #     else:
    #         print(f"⚠️ No builds found for {job}")
    print("Fetching Jenkins Stats...")
    query_stats()
if __name__ == "__main__":
    main()
