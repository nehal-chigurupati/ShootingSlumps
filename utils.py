import numpy as np
import pandas as pd

def three_attempts_per_season(career_stats, excluded_season="2023-24"):
    total_3pa = career_stats[career_stats["SEASON_ID"] != "2023-24"]['FG3A'].sum()
    num_seasons = len(career_stats[career_stats["SEASON_ID"] != "2023-24"]['SEASON_ID'].unique())
    
    if num_seasons == 0:
        return None
    
    return int(total_3pa / num_seasons)

def get_career_3pt_pct(all_season_data):
    return float(np.sum(all_season_data["FG3M"])) / float(np.sum(all_season_data["FG3A"]))

def detect_shooting_slumps(game_data, all_season_data):
    """
    #Calculate slump threshold
    mean_3pct = np.mean(game_data["FG3_PCT"])
    std_dev_3pct = np.std(game_data["FG3_PCT"])
    # Define a threshold for a slump (2 standard deviations lower than average 3PT%)
    slump_threshold_3pt = mean_3pct - 2*std_dev_3pct
    """

    #Let's use a naive slump threshold - 10% below career pct
    slump_threshold_3pt = get_career_3pt_pct(all_season_data) - .05

    # Identify slumps
    slump_periods = []
    slump_start = None

    for start in range(len(game_data)):
        for end in range(start + 5, len(game_data)):  # Ensure at least 5 games
            span_avg_3pt = game_data.iloc[start:end+1]["FG3M"].sum() / game_data.iloc[start:end+1]["FG3A"].sum()
            if span_avg_3pt < slump_threshold_3pt:
                slump_start = start
                break
        if slump_start is not None:
            slump_periods.append((slump_start, end))
            slump_start = None

    # Removing overlapping and continuous slumps
    filtered_slump_periods = []
    for start, end in slump_periods:
        if not filtered_slump_periods or start > filtered_slump_periods[-1][1]:
            filtered_slump_periods.append((start, end))

    # Extract slump periods
    slump_dfs = [game_data.iloc[start:end+1] for start, end in filtered_slump_periods]

    return slump_dfs
