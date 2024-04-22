import time
import pandas as pd
from util.APIClient import APIClient
from util.github_util import *
import yaml

# Load configuration settings from a YAML file.
with open('./config.yaml', 'r') as file:
    config = yaml.safe_load(file)


def wechat_to_faq(filename='./wechat/message.csv', chunk_size=100, overlap=20):
    assert(chunk_size > overlap)
    # create api client
    api_client = APIClient(config['API_KEY'], config['API_BASE'], temperature=0.3, max_tokens=1024)

    # load WeChat messages and
    df = pd.read_csv(filename)
    nickname = df['NickName'].tolist()
    str_content = df['StrContent'].tolist()

    # slice them into chunks with desirable size
    message_chunks = []
    for start in range(len(nickname) // (chunk_size - overlap) + 1):
        end = min(start * (chunk_size - overlap) + chunk_size, len(nickname))
        message_chunks.append([[nickname[i], str_content[i][:200]] for i in range(start * (chunk_size - overlap), end)])

    # generate FAQ by calling yi-34b-chat api
    FAQ = []
    name_dict = {}
    for chunk in message_chunks:
        messages = []
        for message in chunk:
            name = message[0]
            if name not in name_dict.keys():
                name_dict[name] = len(name_dict.keys())
            messages.append(f"{name_dict[name]}说：{message[1]}\n")

        messages = ''.join(messages)
        res = api_client.get_FAQ_from_wechat_message(messages)
        FAQ.append(res)
        # make sure it does not exceed request limit
        time.sleep(10)

    # save FAQ into text file
    with open('wechat/wechat_FAQ.txt', 'w', encoding="utf-8") as f:
        for faq in FAQ:
            f.write(faq)
            f.write('\n\n')




def github_to_faq(owner='01-ai', repo='Yi'):
    # create api client
    api_client = APIClient(config['API_KEY'], config['API_BASE'], model='yi-34b-chat-200k', temperature=0.3)

    # load GitHub issues
    issues = fetch_all_issues(owner, repo, config['github']['token'])

    # generate FAQ by calling yi-34b-chat api
    FAQ = []
    for issue in issues:
        # ignore PRs
        if 'pull_request' in issue.keys():
            continue

        # extract issue title, content, and replies
        title = issue['title']
        content = issue['body']
        comment = ''
        try:
            for c in make_github_request(issue['comments_url'], config['github']['token']):
                comment += f"{c['body']}\n"
        except:
            comment = '无'

        content = f'标题：{title}\n 内容:{content}\n 回复：{comment}'
        FAQ.append(api_client.get_FAQ_from_github_issue(content))

    # save FAQ into text file
    with open('GitHub_FAQ.txt', 'w', encoding="utf-8") as f:
        for faq in FAQ:
            f.write(faq)


def wechat_to_faq_200k(filename='./wechat/message.csv'):
    # create api client
    api_client = APIClient(config['API_KEY'], config['API_BASE'], model="yi-34b-chat-200k", temperature=0.2)

    # load WeChat messages and
    df = pd.read_csv(filename)

    messages = ''
    for row in df.iterrows():
        name = row[1]['NickName']
        content = row[1]['StrContent']
        time = row[1]['StrTime']

        messages += f"{name}在{time}的时候说：{content}\n"

    query = '运行34B需要多少显存'
    messages = messages[:int(len(messages) / 5)]
    prompt = f'{messages}\n\n以上是聊天记录，其中表明了谁在什么时间说了什么.\n'

    prompt += f'现在请根据提供的聊天记录作为参考文献，来回答该问题：{query}\n'
    system_prompt = '你是一个FAQ助手，你可以根据历史聊天记录来回答用户的提问'
    res = api_client.get_respond(system_prompt, prompt)
    print(res)


def wechat_to_chat_summary(filename='./wechat/message.csv'):
    # create api client
    api_client = APIClient(config['API_KEY'], config['API_BASE'], model='yi-34b-chat-200k', max_tokens=4096,temperature=0.2)

    # load WeChat messages and
    df = pd.read_csv(filename)
    nickname = df['NickName'].tolist()
    str_content = df['StrContent'].tolist()

    message_raw = [f"{x[0]}说：{x[1]}\n" for x in zip(nickname, str_content)]

    # generate FAQ by calling yi-34b-chat api
    messages = ''.join(message_raw[-300:])
    res = api_client.get_chat_summary(messages)
    print(res)



# wechat_to_chat_summary()
