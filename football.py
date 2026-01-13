# Create a ready-to-run Streamlit dashboard app (app.py) using the already loaded analysis_df
import textwrap


import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title='Football Players Dashboard', layout='wide')

# @st.cache_data
# def load_data():
#     df = pd.read_csv("C:\\Users\\shine\\STREAMLIT\\Latest Football  Players 2024 Data.csv", encoding='ascii')
#     # basic cleaning
#     for c in ['Matches', 'Goals', 'Assists', 'Seasons Ratings']:
#         df[c] = pd.to_numeric(df[c], errors='coerce')
#     df['Teams'] = df['Teams'].astype(str).str.strip()
#     df['Players'] = df['Players'].astype(str).str.strip()
#     df['Seasons'] = df['Seasons'].astype(str).str.strip()
#     return df


import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "Latest Football Players 2024 Data.csv")
    df = pd.read_csv(csv_path, encoding="ascii")
    return df

df = load_data()

st.title('Football Players Dashboard')
st.caption('Assumption used in this dashboard: Season winner = team with the most total goals in that season (within this dataset).')

with st.sidebar:
    st.header('Filters')
    seasons_sel = st.multiselect('Seasons', options=sorted(df['Seasons'].unique().tolist()))
    teams_sel = st.multiselect('Teams', options=sorted(df['Teams'].unique().tolist()))
    players_sel = st.multiselect('Players', options=sorted(df['Players'].unique().tolist()))

fdf = df.copy()
if seasons_sel:
    fdf = fdf[fdf['Seasons'].isin(seasons_sel)]
if teams_sel:
    fdf = fdf[fdf['Teams'].isin(teams_sel)]
if players_sel:
    fdf = fdf[fdf['Players'].isin(players_sel)]

# KPIs
kpi_total_goals = float(fdf['Goals'].sum(skipna=True))
kpi_total_players = int(fdf['Players'].nunique())
kpi_total_matches = float(fdf['Matches'].sum(skipna=True))
kpi_avg_rating = float(fdf['Seasons Ratings'].mean(skipna=True))

k1, k2, k3, k4 = st.columns(4)
k1.metric('Total goals', int(kpi_total_goals) if np.isfinite(kpi_total_goals) else 0)
k2.metric('Unique players', kpi_total_players)
k3.metric('Total matches (sum)', int(kpi_total_matches) if np.isfinite(kpi_total_matches) else 0)
k4.metric('Average season rating', round(kpi_avg_rating, 2) if np.isfinite(kpi_avg_rating) else None)

st.divider()

# Aggregations
by_player = fdf.groupby('Players', as_index=False).agg(
    Goals=('Goals', 'sum'),
    Matches=('Matches', 'sum'),
    Assists=('Assists', 'sum'),
    Avg_Rating=('Seasons Ratings', 'mean')
)
by_team = fdf.groupby('Teams', as_index=False).agg(
    Goals=('Goals', 'sum'),
    Matches=('Matches', 'sum'),
    Assists=('Assists', 'sum'),
    Avg_Rating=('Seasons Ratings', 'mean'),
    Players=('Players', 'nunique')
)
by_season = fdf.groupby('Seasons', as_index=False).agg(
    Goals=('Goals', 'sum'),
    Matches=('Matches', 'sum'),
    Assists=('Assists', 'sum'),
    Avg_Rating=('Seasons Ratings', 'mean'),
    Teams=('Teams', 'nunique'),
    Players=('Players', 'nunique')
)

# Winners per season (most goals)
season_team = fdf.groupby(['Seasons', 'Teams'], as_index=False).agg(
    Goals=('Goals', 'sum'),
    Avg_Rating=('Seasons Ratings', 'mean')
)
season_winners = season_team.sort_values(['Seasons', 'Goals'], ascending=[True, False]).groupby('Seasons', as_index=False).head(1)

# Best rated team per season
best_rated_team = season_team.sort_values(['Seasons', 'Avg_Rating'], ascending=[True, False]).groupby('Seasons', as_index=False).head(1)

# Best rated player overall (record-level)
best_rated_player_record = fdf.sort_values('Seasons Ratings', ascending=False).head(1)

# Top scorer overall
by_player_sorted = by_player.sort_values('Goals', ascending=False)
top_scorer = by_player_sorted.head(1)

c_left, c_right = st.columns(2)

with c_left:
    st.subheader('Goals distribution')
    st.plotly_chart(px.histogram(fdf, x='Goals', nbins=30, title='Distribution of Goals (row-level)'), use_container_width=True)

with c_right:
    st.subheader('Matches distribution')
    st.plotly_chart(px.histogram(fdf, x='Matches', nbins=30, title='Distribution of Matches (row-level)'), use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader('Goals by player')
    top_n = st.slider('Top N players by goals', 5, 50, 15)
    chart_df = by_player_sorted.head(top_n)
    st.plotly_chart(px.bar(chart_df, x='Goals', y='Players', orientation='h', title='Top Players by Total Goals'), use_container_width=True)

with c2:
    st.subheader('Goals by team')
    chart_team = by_team.sort_values('Goals', ascending=False)
    st.plotly_chart(px.bar(chart_team.head(20), x='Goals', y='Teams', orientation='h', title='Top Teams by Total Goals'), use_container_width=True)

st.subheader('Goals / Assists / Matches by season')
season_sorted = by_season.sort_values('Seasons')
st.plotly_chart(px.line(season_sorted, x='Seasons', y=['Goals', 'Assists', 'Matches'], markers=True, title='Season Totals'), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.subheader('Season winners (most goals)')
    st.dataframe(season_winners[['Seasons', 'Teams', 'Goals']].reset_index(drop=True), use_container_width=True)

with c4:
    st.subheader('Best rated team per season')
    st.dataframe(best_rated_team[['Seasons', 'Teams', 'Avg_Rating']].reset_index(drop=True), use_container_width=True)

c5, c6 = st.columns(2)
with c5:
    st.subheader('Top scorer overall')
    if len(top_scorer) > 0:
        st.dataframe(top_scorer[['Players', 'Goals', 'Matches', 'Assists', 'Avg_Rating']].reset_index(drop=True), use_container_width=True)

with c6:
    st.subheader('Best rating (player + season)')
    if len(best_rated_player_record) > 0:
        st.dataframe(best_rated_player_record[['Players', 'Teams', 'Seasons', 'Seasons Ratings', 'Goals', 'Assists', 'Matches']].reset_index(drop=True), use_container_width=True)

st.subheader('How many matches does a player feature in')
st.plotly_chart(px.scatter(by_player, x='Matches', y='Goals', hover_name='Players', title='Player Matches vs Goals'), use_container_width=True)

st.subheader('How many players are in a team (unique players)')
players_per_team = by_team.sort_values('Players', ascending=False)
st.plotly_chart(px.bar(players_per_team.head(25), x='Players', y='Teams', orientation='h', title='Unique Players per Team'), use_container_width=True)

st.subheader('How many matches were played in a season (sum of Matches)')
matches_per_season = by_season[['Seasons', 'Matches']].sort_values('Seasons')
st.plotly_chart(px.bar(matches_per_season, x='Seasons', y='Matches', title='Matches per Season'), use_container_width=True)

st.subheader('Assists: who assisted, in which season, and what team')
assists_tbl = fdf.loc[fdf['Assists'].fillna(0) > 0, ['Players', 'Assists', 'Seasons', 'Teams']].sort_values('Assists', ascending=False)
st.dataframe(assists_tbl.reset_index(drop=True), use_container_width=True)

st.subheader('Raw data')
st.dataframe(fdf.reset_index(drop=True), use_container_width=True)


# 


print('football.py')
