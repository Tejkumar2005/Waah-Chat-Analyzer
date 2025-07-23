# helper.py

from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import re
from collections import Counter
import emoji
import calendar

extractor = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    df = df.dropna(subset=['message'])

    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    num_media_messages = df['message'].str.contains('media omitted', case=False, na=False).sum()

    return num_messages, len(words), num_media_messages

def most_busy_users(df):
    user_counts = df['user'].value_counts().head(10)
    user_percent = round((user_counts / df.shape[0]) * 100, 2)
    busy_df = user_percent.reset_index()
    busy_df.columns = ['name', 'percent']
    return user_counts, busy_df

def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('omitted', case=False, na=False)]

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    temp = temp.copy()
    temp['message'] = temp['message'].apply(remove_stop_words)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = f.read().splitlines()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('omitted', case=False, na=False)]

    words = []
    for message in temp['message']:
        message = re.sub(r'[^\w\s]', '', message)
        message = re.sub(r'\n', ' ', message)
        message = message.lower()

        for word in message.split():
            if word not in stop_words and word != "":
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['Year', 'month_num']).count()['message'].reset_index()
    timeline['month'] = timeline['month_num'].apply(lambda x: calendar.month_abbr[x])
    timeline['time'] = timeline['month'] + " " + timeline['Year'].astype(str)
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['only_Date']).count()['message'].reset_index()
    return timeline

def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    month_counts = df['month'].value_counts()
    ordered_months = [calendar.month_name[i] for i in range(1, 13)]
    month_counts = month_counts.reindex(ordered_months).dropna()
    return month_counts

def activity_heat_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Define all 24 hourly periods
    all_periods = [f"{str(i).zfill(2)}-{str(i+1).zfill(2)}" for i in range(0, 23)]
    all_periods.append("23-00")

    # Ensure 'period' column exists
    if 'period' not in df.columns:
        period = []
        for hour in df['hour']:
            if hour == 23:
                period.append('23-00')
            else:
                period.append(f"{str(hour).zfill(2)}-{str(hour+1).zfill(2)}")
        df['period'] = period

    # Pivot table: day_name vs period
    heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    # Add missing columns
    for period in all_periods:
        if period not in heatmap.columns:
            heatmap[period] = 0

    # Reorder columns by hour
    heatmap = heatmap[all_periods]

    return heatmap

