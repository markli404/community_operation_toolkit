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
    api_client = APIClient(config['API_KEY'], config['API_BASE'])

    # load WeChat messages and
    df = pd.read_csv(filename)
    nickname = df['NickName'].tolist()
    str_content = df['StrContent'].tolist()

    # slice them into chunks with desirable size
    message_chunks = []
    for start in range(len(nickname) // (chunk_size - overlap) + 1):
        end = min(start * (chunk_size - overlap) + chunk_size, len(nickname))
        message_chunks.append([[nickname[i], str_content[i]] for i in range(start * (chunk_size - overlap), end)])

    # generate FAQ by calling yi-34b-chat api
    FAQ = []
    for chunk in message_chunks:
        messages = [f"{message[0]}说：{message[1]}\n" for message in chunk]
        messages = ''.join(messages)
        FAQ.append(api_client.get_FAQ_from_wechat_message(messages))
        # make sure it does not exceed request limit
        time.sleep(20)

    # save FAQ into text file
    with open('wechat/wechat_FAQ.txt', 'w', encoding="utf-8") as f:
        for faq in FAQ:
            f.write(faq)


def github_to_faq(owner='01-ai', repo='Yi'):
    # create api client
    api_client = APIClient(config['API_KEY'], config['API_BASE'], model='yi-34b-chat-200k')

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
