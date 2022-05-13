import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import sqlite3

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USER_ID = "itsluized"
TOKEN = "BQDrOt6C5ruH31E1CrAjEuYLJaJ267Gj2utquesxRPHtFOnr_W1iKYldpCZQp1eUJN2bYVbNygGF_otpqrZYbdu0lQDvImQ_b801HwnKp54R9oMYZeeQ7O_NCA0feLF90ToWHy9tFZIMyt5XbMU"

# To get tocken, go to: "https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbF96VWJrNHRNVXlyU3ZsZnVhYURJMl9ta1pVd3xBQ3Jtc0ttTEw0Sm8xTEFHSVJnVXFMWGktUTMtLWVod1VMbmJSSk9GNHdGRHRsOWc2cl91ZlhTODJ3ZE14NjJEOEVuTXJ5M2ZlbkFodzQ1MGljcFl0M2xrc3RRY2xBRmlRbFpiRUR6VjBucTZtUjFzX0toT0E2RQ&q=https%3A%2F%2Fdeveloper.spotify.com%2Fconsole%2Fget-recently-played%2F&v=dvviIUKwH7o"

if __name__ == "__main__":

  # EXTRACT PART OF ETL
  headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization" : "Bearer {token}".format(token=TOKEN)
  }

  today = datetime.datetime.now()
  yesterday = today - datetime.timedelta(days=1)
  yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

  r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp),headers=headers)

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

  song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])

  print(song_df)