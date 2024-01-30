import datetime as dt
from datetime import datetime
import requests
import pandas as pd
import yaml
import os

# 读取YAML配置文件
with open('./config.yaml', 'r') as file:
    config = yaml.safe_load(file)

data_dir = config['github']['data_dir']

headers = {
    'Authorization': 'token {}'.format(config['github']['token']),
    'Accept': 'application/vnd.github.v3.star+json'
}


def function_call(keyword, owner, repo):
    print(f'Calling get_{keyword}_history function with args: {owner}, {repo}')
    method = eval(f'get_{keyword}_history')
    args = [owner, repo]
    kwargs = {}
    method(*args, **kwargs)


def datedelta_to_minutes(datedelta):
    days, seconds = datedelta.days, datedelta.seconds
    minutes = days * 24 * 60 + (seconds // 60)
    return minutes


def ISO_string_to_datetime(s):
    return datetime.fromisoformat(s).replace(tzinfo=None)


def load_issue_history_df(owner, repo):
    df = load_history_df('issues', owner, repo)
    df['created_at'] = pd.to_datetime(df['created_at'])

    return df


def load_metric_history_df(metric, owner, repo, days=None):
    df = load_history_df(metric, owner, repo)
    df['dates'] = pd.to_datetime(df['dates'])
    df['cumulative_counts'] = [sum(df['counts'][:i]) for i in range(len(df['counts']))]

    if isinstance(days, int):
        base_dt = pd.to_datetime(datetime.today().date() - dt.timedelta(days=days))
        df = df[df['dates'] > base_dt]

    return df


def load_history_df(metric, owner, repo):
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    filename = f'github_{owner}_{repo}_{metric}.csv'
    try:
        df = pd.read_csv(os.path.join(data_dir, filename), index_col=False, encoding='utf-8-sig')
    except:
        print(f'--- {filename} not found. Try to generate data file now...')
        function_call(metric, owner, repo)

        df = pd.read_csv(os.path.join(data_dir, filename), index_col=False, encoding='utf-8-sig')

    return df


def save_history_df(df, owner, repo, metric):
    filename = f'github_{owner}_{repo}_{metric}.csv'
    df.to_csv(os.path.join(data_dir, filename), index=False, encoding='utf-8-sig')
    print(f'--- File successfully saved to {filename}! ')


def get_dates(metric, keywords, owner, repo):
    dates_raw = []
    page = 1
    url = 'https://api.github.com/repos/{}/{}'.format(owner, repo)

    while True:
        response = requests.get(url + f'/{metric}?page={page}&per_page=100', headers=headers)
        if response.status_code != 200:
            break

        print(f"--- Loading page {page} for GitHub {owner} {repo} {metric} history...")

        records = response.json()
        if not records:
            break

        for record in records:
            dates_raw.append(datetime.fromisoformat(record[keywords].split('T')[0]))

        page += 1

    dates_raw.sort()
    return dates_raw


def get_counts_from_dates(dates_raw):
    dates, counts = [], []

    prev = dates_raw[0]
    count = 0
    for date in dates_raw:
        if date != prev:
            dates.append(date)
            counts.append(count)
            prev = date
            count = 1
        else:
            count += 1

    return dates, counts


def get_clone_history(owner, repo):
    dates, counts = [], []
    url = 'https://api.github.com/repos/{}/{}'.format(owner, repo)

    response = requests.get(url + f'/traffic/clones', headers=headers)
    if response.status_code != 200:
        print(str(response.status_code) + ' error')
        return

    clones = response.json()['clones']
    if not clones:
        print('Clones not found')
        return

    for clone in clones:
        dates.append(datetime.fromisoformat(clone['timestamp'].split('Z')[0]))
        counts.append(clone['uniques'])

    df = pd.DataFrame({'dates': dates,
                       'counts': counts})
    save_history_df(df, owner, repo, 'clone')


def get_fork_history(owner, repo):
    dates_raw = get_dates('forks', 'created_at', owner=owner, repo=repo)
    dates, counts = get_counts_from_dates(dates_raw)
    df = pd.DataFrame({'dates': dates,
                       'counts': counts})
    save_history_df(df, owner, repo, 'fork')


def get_star_history(owner, repo):
    dates_raw = get_dates('stargazers', 'starred_at', owner=owner, repo=repo)
    dates, counts = get_counts_from_dates(dates_raw)
    df = pd.DataFrame({'dates': dates,
                       'counts': counts})
    save_history_df(df, owner, repo, 'star')


def get_issues_history(owner, repo):
    issues = []
    pr = []
    page = 1

    ''' Get open issues'''
    print(' --- Load open issues...')
    while True:
        response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/issues?page={page}&per_page=100",
                                headers=headers)
        if response.text == '[]':
            break

        issues.extend(response.json())
        page += 1

    page = 1

    ''' Get closed issues'''
    print(' --- Load closed issues...')
    while True:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues?state=closed&page={page}&per_page=100",
            headers=headers)
        if response.text == '[]':
            break

        issues.extend(response.json())
        page += 1

    ''' Filter out pull requests'''
    print(' --- Filter out pull requests...')
    i = 0
    while i < len(issues):
        issue = issues[i]
        if 'pull_request' in issue.keys():
            pr.append(issues.pop(i))
        else:
            i += 1

    ''' Format issues '''
    print(' --- Format issues and save...')
    issues_df = []
    for issue in issues:
        issue_df = {}

        # Remove official posts
        if issue['author_association'] != 'NONE':
            continue

        issue_df['number'] = issue['number']
        issue_df['title'] = issue['title']
        issue_df['created_at'] = ISO_string_to_datetime(issue['created_at'])
        issue_df['state'] = issue['state']
        if issue['closed_at']:
            issue_df['closed_time'] = datedelta_to_minutes(
                ISO_string_to_datetime(issue['closed_at']) - issue_df['created_at'])

        comments = requests.get(issue['comments_url'], headers=headers).json()
        for comment in comments:
            if comment['author_association'] in ['CONTRIBUTOR', 'MEMBER']:
                issue_df['reply_time'] = datedelta_to_minutes(
                    ISO_string_to_datetime(comment['created_at']) - issue_df['created_at'])
                break

        issues_df.append(issue_df)

    df = pd.DataFrame(issues_df)
    save_history_df(df, owner, repo, 'issues')
    print('--- Success!')

