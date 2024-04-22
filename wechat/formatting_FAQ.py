import pandas as pd

file = open('wechat_FAQ.txt', 'r', encoding="utf8")
content = file.read().split('\n')
df = []

question, answer = None, None
for line in content:
    if line.startswith('Q'):
        question = line[3:]

    if line.startswith('A'):
        answer = line[3:]

    if question is not None and answer is not None:
        df.append({
            'question': question,
            'answer': answer
        })
        question, answer = None, None

df = pd.DataFrame(df)
df.to_csv('wechat_FAQ.csv', encoding='utf-8-sig')


