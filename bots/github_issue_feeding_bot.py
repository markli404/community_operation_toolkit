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

    resp = requests.post(config['webbook_url'], json=params)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") and result.get("code") != 0:
        print(f"发送失败：{result['msg']}")
        return
    print("消息发送成功")


if __name__ == '__main__':
    last_posted_issue_id = None
    while True:
        open_issue_url = f"https://api.github.com/repos/01-ai/Yi/issues"
        issues = make_github_request(open_issue_url, config['github']['token'])
        if last_posted_issue_id is None:
            last_posted_issue_id = int(issues[0]['number'])
            continue

        for issue in issues:
            id = issue['number']
            if int(id) > last_posted_issue_id:
                title = issue['title']
                url = issue['html_url']
                content = issue['body']
                send_message(id, title, content, url)

        last_posted_issue_id = int(issues[0]['number'])
        time.sleep(1800)

