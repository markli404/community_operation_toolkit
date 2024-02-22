import pandas as pd
import numpy as np
import emoji
df = pd.read_csv('Yi_User_Group_中文社区_utf8.csv')
df = df[['NickName', 'StrContent', 'StrTime']]

# remove images
df = df[~df.StrContent.str.get(0).isin(['<', ''])]

# remove pad
df = df[df['StrContent'].str.contains('拍了拍 ') == False]

# remove emotes
df['StrContent'] = df['StrContent'].str.replace('(\[(抱拳|呲牙|666|Party|Lol|捂脸|强|OK|Happy|尴尬|流泪|偷笑|奸笑|爱心|皱眉|耶|汗|Worship|旺柴|衰|勾引|让我看看|胜利|得意|握手|吃瓜|发呆|可怜|抠鼻)\])', "", regex=True)
df.dropna(subset=['StrContent'], inplace=True)

# remove unknown characters
df['NickName'] = df['NickName'].str.replace('[\x00-\x1F\x7F]', "U", regex=True)
df['StrContent'] = df['StrContent'].str.replace('[\x00-\x1F\x7F]', "", regex=True)

# remove @
df['StrContent'] = df['StrContent'].str.replace('@\S+?( | )', "", regex=True)

# remove hyperlinks
df['StrContent'] = df['StrContent'].str.replace('https?:\/\/\S+', "", regex=True)

# remove 666
df['StrContent'] = df['StrContent'].str.replace('\b6+\b', "", regex=True)

# remove emoji
df['StrContent'] = df['StrContent'].apply(lambda s: emoji.replace_emoji(str(s), ''))
df.dropna(subset=['StrContent'], inplace=True)

# remove short messages
df = df[df.StrContent.str.len() >= 3]


# remove empty message
df['StrContent'].replace('', np.nan, inplace=True)
df['NickName'].replace('', np.nan, inplace=True)
df.dropna(subset=['StrContent'], inplace=True)
df.dropna(subset=['NickName'], inplace=True)

df['time'] = (pd.to_datetime(df['StrTime']).dt.hour + 14) % 24

df.to_csv('message.csv', encoding='utf-8_sig', index=False)
