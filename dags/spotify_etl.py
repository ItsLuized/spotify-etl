import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import sqlite3

def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False

    # Primary Key Check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key Check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null value found")

    #  Check that all timestamps are of yesterday's date
    # yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    # yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    # timestamps = df["timestamp"].to_list()
    # for timestamp in timestamps:
    #     if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
    #         raise Exception(
    #             "At least one of the returned songs doesnot come from within the last 24 hours")

    return True

def run_spotify_etl():
    # Now in lower case because they are local variables 
    database_location = "sqlite:///my_played_tracks.sqlite"
    user_id = "itsluized"
    token = "BQAwx96V_p_DXGI3toa1iTeh4PayvZGR6DFNm3qFe0dDmMUkVLTJLQXWk5ZdeDyK2gIJt4qqoTuc6tnwSbRKGRWETqrSsXj0Vl5cjxw2_T_2XuKiI1ULOYMvy8bhkl5vFqCv-26eoVg-rdi7dG4jh-jHQNUvaKe_Z-SoziQEH6TVye-BDDg"


    # EXTRACT PART OF ETL
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=token)
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=60)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    r = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?after={time}".format(
            time=yesterday_unix_timestamp),
        headers=headers)

    data = r.json()

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    song_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps
    }

    song_df = pd.DataFrame(
        song_dict,
        columns=["song_name", "artist_name", "played_at", "timestamp"])

    # Validate
    if check_if_valid_data(song_df):
        print("Data valid, proceed to Load stage")

    # Load
    engine = sqlalchemy.create_engine(database_location)
    conn = sqlite3.connect('my_played_tracks.sqlite')
    cursor = conn.cursor()

    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor.execute(sql_query)

    try:
        song_df.to_sql("my_played_tracks", engine, index=False, if_exists="append")
    except:
        print("Data already exists in the database")

    conn.close()
    print("Close database successfully")