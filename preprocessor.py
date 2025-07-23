import re
import pandas as pd

def preprocess(content):
    # Use raw string for regex
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\u202f|\s)?(?:am|pm|AM|PM)?\s-\s'

    # Extract messages and dates
    messages = re.split(pattern, content)[1:]
    dates = re.findall(pattern, content)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M\u202f%p - ', errors='coerce')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    message_text = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)  # use raw string here too
        if len(entry) >= 3:
            users.append(entry[1])
            message_text.append(entry[2])
        else:
            users.append('group_notification')
            message_text.append(entry[0])

    df['user'] = users
    df['message'] = message_text
    df.drop(columns=['user_message'], inplace=True)

    # Add datetime features
    df['only_Date'] = df['date'].dt.date
    df['Year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []

    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + '00')
        elif hour == 0:
            period.append('00' + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
