import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.sidebar.title("📱 WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Upload WhatsApp Chat (.txt)")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    # Optional: Display raw chat data
    if st.sidebar.button("Show Raw Chat"):
        st.subheader("📝 Raw WhatsApp Chat Data")
        st.dataframe(df)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Analyze chat for:", user_list)

    if st.sidebar.button("Show Analysis"):
        # Top Stats
        num_messages, words, num_media_messages = helper.fetch_stats(selected_user, df)

        st.title("📊 Top Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Media Shared", num_media_messages)

        # Monthly Timeline
        st.title("🗓️ Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        ax.set_xticks(range(0, len(timeline['time']), max(1, len(timeline['time']) // 10)))
        ax.set_xticklabels(timeline['time'][::max(1, len(timeline['time']) // 10)], rotation=45)
        st.pyplot(fig)

        # Daily Timeline
        st.title("📅 Daily Timeline")
        daily = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(daily['only_Date'], daily['message'], color='black', linewidth=1.5)
        ax.set_xticks(daily['only_Date'][::max(1, len(daily) // 10)])
        ax.set_xticklabels(daily['only_Date'][::max(1, len(daily) // 10)], rotation=45)
        ax.set_xlabel("Date")
        ax.set_ylabel("Messages")
        ax.set_title("Messages per Day")
        ax.grid(True)
        st.pyplot(fig)

        # Activity Map
        st.title("📈 Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Busy Days")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            bars = ax.bar(busy_day.index, busy_day.values, color='skyblue', edgecolor='black')
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(int(bar.get_height())),
                        ha='center', va='bottom', fontsize=8)
            ax.set_ylabel("Messages")
            st.pyplot(fig)

        with col2:
            st.header("Busy Months")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            bars = ax.bar(busy_month.index, busy_month.values, color='salmon', edgecolor='black')
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), str(int(bar.get_height())),
                        ha='center', va='bottom', fontsize=8)
            ax.set_ylabel("Messages")
            st.pyplot(fig)

        # Weekly Activity Heatmap
        st.title("🌡️ Weekly Activity Heatmap")
        heatmap_data = helper.activity_heat_map(selected_user, df)
        fig, ax = plt.subplots(figsize=(20, 6))
        sns.heatmap(heatmap_data, cmap='YlGnBu', ax=ax)
        ax.set_xlabel("Hour Range")
        ax.set_ylabel("Day")
        st.pyplot(fig)

        # Most Busy Users
        if selected_user == "Overall":
            st.title("👥 Most Active Users")
            x, percent = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            ax.bar(x.index, x.values, color='green')
            plt.xticks(rotation=45)
            ax.set_ylabel("Messages")
            st.pyplot(fig)
            st.dataframe(percent)

        # Word Cloud
        st.title("☁️ Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

        # Most Common Words
        st.title("🔠 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df['word'], most_common_df['count'], color='purple')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Emoji Analysis
        st.title("😊 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct='%1.1f%%')
            st.pyplot(fig)
