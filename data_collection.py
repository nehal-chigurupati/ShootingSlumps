import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from nba_api.stats.endpoints import playercareerstats, playergamelog
from nba_api.stats.static import players
import time

"""
Algorithm for detecting shooting slumps:
First, filter to players who have average 250 or more threes
"""

def get_active_players():
    all_players = players.get_active_players()

    player_names = []
    player_ids = []
    for player in all_players:
        player_names.append(player["full_name"])
        player_ids.append(player["id"])
    
    return pd.DataFrame({"PLAYER_NAME": player_names, "PLAYER_ID": player_ids})

def get_career_stats(player_df):
    #Accepts a dataframe with player ids and names
    dfs = []
    counter = 1
    for index, row in player_df.iterrows():
        print("Getting career stats for player " + str(counter) + "/" + str(len(player_df)))
        counter += 1
        time.sleep(.25)
        stats = playercareerstats.PlayerCareerStats(player_id = row["PLAYER_ID"]).get_data_frames()[0]
        stats["PLAYER_NAME"] = [row["PLAYER_NAME"]]*len(stats)
        dfs.append(stats)
    
    return pd.concat(dfs)

def get_player_game_logs(player_id, seasons):
    season_data = []
    for season in seasons:
        data = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star="Regular Season")
        season_data.append(data.get_data_frames()[0])
    
    return pd.concat(season_data)


#Connect to SQL database
engine = create_engine("sqlite:///Data/shooting_slumps_data.db")

#Get all active players
all_active_players = get_active_players()
all_active_players.to_sql("ACTIVE_PLAYER_IDS", engine, if_exists="replace", index=False)

#Collect player career stats
all_career_stats = get_career_stats(all_active_players)
all_career_stats.to_sql("PLAYER_CAREER_STATS", engine, if_exists="replace", index=False)
#Get player game logs
player_game_logs = []
counter = 1
for player_id in np.unique(all_career_stats["PLAYER_ID"]):
    print("Collecting game logs for player " + str(counter) + "/" + str(len(np.unique(all_career_stats["PLAYER_ID"]))))
    counter += 1
    time.sleep(.25)
    seasons = np.unique(all_career_stats[all_career_stats["PLAYER_ID"] == player_id]["SEASON_ID"])
    player_game_logs.append(get_player_game_logs(player_id, seasons=seasons))

player_game_logs = pd.concat(player_game_logs)
player_game_logs.to_sql("PLAYER_GAME_LOGS", engine, if_exists="replace", index=False)

    





