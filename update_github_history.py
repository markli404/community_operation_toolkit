import requests
import yaml
from util.datetime_util import *
from util.util import *

# Load configuration settings from a YAML file.
with open('./config.yaml', 'r') as file:
    config = yaml.safe_load(file)


# Function to make a paginated request to GitHub API and gather all data from a specific endpoint.
def make_github_request(url, params=None):
    params = params or {}
    params.update({"per_page": 100})  # Default to 100 items per page for maximum efficiency.
    all_data = []
    headers = {
        'Authorization': f'token {config["github"]["token"]}',  # Authentication token from config.
        'Accept': 'application/vnd.github.v3.star+json'  # Ensure compatibility with the GitHub API version 3.
    }
    # Loop to handle pagination.
    while True:
        response = requests.get(url, headers=headers, params=params)
        # Break loop if request fails or no more data is available.
        if response.status_code != 200 or not response.json():
            break
        all_data.extend(response.json())
        # If there's a next page, update the URL and continue; otherwise, break.
        if 'next' not in response.links:
            break
        url = response.links['next']['url']
    return all_data


# Convert raw data into a list of datetime objects.
def make_datetime_list(raw_data, key):
    return [datetime.fromisoformat(record[key].split('T')[0]) for record in raw_data]


# Fetch a specific metric (e.g., stars, forks) for a GitHub repository.
def fetch_metric_by_repo(metric, keywords, owner, repo):
    print(f'Fetching github {metric} on {owner}:{repo}')
    full_url = f'https://api.github.com/repos/{owner}/{repo}/{metric}'
    raw_dates = make_github_request(full_url)
    return make_datetime_list(raw_dates, keywords)


# Retrieve and process star history for a specific repository.
def get_star_history_by_repo(owner, repo):
    dates_raw = fetch_metric_by_repo('stargazers', 'starred_at', owner=owner, repo=repo)
    df = pd.DataFrame({
        'name': [repo] * len(dates_raw),
        'dates': dates_raw
    })
    df['dates'] = pd.to_datetime(df['dates']).dt.date
    # Group by date and count occurrences for each date.
    df = df.groupby('dates').size().reset_index(name='counts')

    date_range = pd.date_range(min(df['dates']), datetime.today(), freq='D')
    df.set_index('dates', inplace=True)
    df = df.reindex(date_range, fill_value=0).rename_axis('dates').reset_index()

    df['cumulative'] = df['counts'].cumsum()
    df.insert(0, 'name', [repo] * len(df))
    return df


# Generate and export GitHub star history for all configured repositories.
def update_github_star():
    print('--- Generating github star history ---')
    star_df = []
    for owner, repo in [(config[llm]['owner'], config[llm]['repo']) for llm in config['all']]:
        star_df.append(get_star_history_by_repo(owner, repo))
    star_df = pd.concat(star_df)
    star_df = lable_week_and_month(star_df, 'dates')
    export_to_excel(star_df, "github_star.xlsx")


# Fetch all issues (both open and closed) for a GitHub repository.
def fetch_all_issues(owner, repo):
    print(f'Fetching github issues on {owner}:{repo}...')
    issues = []
    open_issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    issues.extend(make_github_request(open_issue_url))
    closed_issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=closed"
    issues.extend(make_github_request(closed_issue_url))
    return issues


# Format a single issue into a structured dictionary.
def formatting_issue(repo, issue):
    issue_df = {}
    create_time = ISO_string_to_datetime(issue['created_at'])
    # Populate issue data including PR distinction, duration, and comments.
    issue_df['name'] = repo
    issue_df['number'] = issue['number']
    issue_df['title'] = issue['title']
    issue_df['created_at'] = create_time.date()
    issue_df['state'] = issue['state']
    issue_df['author'] = issue['user']['login']
    issue_df['PR'] = str('pull_request' in issue.keys())
    if issue['closed_at']:
        open_duration = datedelta_to_minutes(
            ISO_string_to_datetime(issue['closed_at']) - create_time)
        issue_df['closed_time'] = open_duration / 60
    else:
        open_duration = datedelta_to_minutes(datetime.today() - create_time)
    # Determine issue duration category.
    if open_duration <= 24 * 60 * 2:
        issue_df['open_duration'] = '2天内'
    elif open_duration <= 24 * 60 * 4:
        issue_df['open_duration'] = '2-4天'
    else:
        issue_df['open_duration'] = '大于4天'
    # Count comments and calculate reply time for the first relevant comment.
    comments = make_github_request(issue['comments_url'])
    issue_df['# of comments'] = len(comments)
    for comment in comments:
        if comment['author_association'] in ['CONTRIBUTOR', 'MEMBER']:
            issue_df['reply_time'] = datedelta_to_minutes(
                ISO_string_to_datetime(comment['created_at']) - create_time) / 60
    return issue_df


# Generate and export GitHub issue history, update any new data since last run.
def update_issue_history():
    print('--- Generating github issue history ---')
    try:
        print('Loading previous history...')
        previous_issue_df = pd.read_excel("github_issue.xlsx")
    except FileNotFoundError:
        previous_issue_df = None
        print('Previous history not found... Trying to regenerate everything.')
    all_issues_df = []

    for owner, repo in [(config[llm]['owner'], config[llm]['repo']) for llm in config['all']]:
        # Loading recorded issues, avoiding unnecessary calculations
        if previous_issue_df is not None:
            recorded_issues = previous_issue_df[previous_issue_df['name'] == repo]
            recorded_issues_id = recorded_issues['number'].values.tolist()
        else:
            recorded_issues = pd.DataFrame([])
            recorded_issues_id = []

        # Processing all fetched issues from github
        new_issues = []
        issues = fetch_all_issues(owner, repo)
        for issue in issues:
            # Remove official posts
            if issue['author_association'] != 'NONE' and 'pull_request' not in issue.keys():
                print(f' --- Removing official posts: ' + issue['title'])
                continue

            # if this issue is recorded in the history...
            issue_id = issue['number']
            if issue_id in recorded_issues_id:
                current_record = recorded_issues[recorded_issues['number'] == issue_id]
                # if this recorded issue is closed, which means that this record is probably unchanged
                if current_record['state'].values == 'closed':
                    continue

                # otherwise this recorded issue is open previously, remove it from the history:
                else:
                    previous_issue_df = previous_issue_df.drop([current_record.index[0]])

            # otherwise this is a new issue
            new_issues.append(formatting_issue(repo, issue))

        # make new_records a DataFrame
        if new_issues:
            new_issues = pd.DataFrame(new_issues)
            new_issues = lable_week_and_month(new_issues, 'created_at')
            all_issues_df.append(new_issues)

    if previous_issue_df is not None:
        all_issues_df.append(previous_issue_df)

    all_issues_df = pd.concat(all_issues_df)
    export_to_excel(all_issues_df, "github_issue.xlsx")


# Main execution block to update GitHub star and issue history.
if __name__ == "__main__":
    update_github_star()
    # update_issue_history()