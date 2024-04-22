from datetime import datetime
import time
from util.github_util import *

timestamp = int(datetime.now().timestamp())


# Load configuration from a YAML file
with open('../config.yaml', 'r') as file:
    config = yaml.safe_load(file)


def send_message(id, title, content, url):
    params = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh-CN": {
                    "title": title,
                    "content": [
                        [
                            {
                                "tag": "a",
                                "text": "#{}".format(id),
                                "href": url,
                            },
                            {
                                "tag": "text",
                                "text": content,
                            },
                        ]
                    ]
                }
            }
        }
    }

    resp = requests.post(config['webhook_url_hf'], json=params)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") and result.get("code") != 0:
        print(f"发送失败：{result['msg']}")
        return
    print("消息发送成功")


def fetch_hf_issue_by_id(model_name, id):
    response = requests.get(
        f"https://huggingface.co/api/models/01-ai/{model_name}/discussions/{id}",
        headers={}
    ).json()

    return response

def fetch_hf_all_issues(model_name):
    response = requests.get(
        f"https://huggingface.co/api/models/01-ai/{model_name}/discussions",
        headers={}
    ).json()['discussions']

    return response


if __name__ == '__main__':
    model_names = ['Yi-VL-34B', 'Yi-6B-Chat-4bits', 'Yi-34B', 'Yi-34B-200K', 'Yi-6B-Chat-8bits', 'Yi-34B-Chat-4bits',
                   'Yi-34B-Chat-8bits', 'Yi-6B-200K', 'Yi-9B', 'Yi-6B-Chat', 'Yi-VL-6B', 'Yi-34B-Chat', 'Yi-6B']

    last_posted_issue_id = {}
    while True:
        for model_name in model_names:
            if model_name not in last_posted_issue_id.keys():
                last_posted_issue_id[model_name] = len(fetch_hf_all_issues(model_name))
                continue

            current_issues = fetch_hf_all_issues(model_name)

            for id in range(last_posted_issue_id[model_name] + 1, len(current_issues)+1):
                issue = fetch_hf_issue_by_id(model_name, id)

                url = f'https://huggingface.co/01-ai/{model_name}/discussions/{id}'
                send_message(issue['num'], model_name + ': ' + issue['title'],
                             issue['events'][0]['data']['latest']['raw'], url)

            last_posted_issue_id[model_name] = len(current_issues)

        time.sleep(1800)

