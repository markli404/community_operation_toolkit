import time

import pandas as pd
import praw
import yaml
from util.util import *
from util.datetime_util import *
from util.APIClient import *
import json

# Load configuration settings from a YAML file.
with open('./config.yaml', 'r') as file:
    config = yaml.safe_load(file)


def formatting_comment(title, comment):
    comment_df = [{
        'id': comment.id,
        'title': title,
        'author': comment.author.name if comment.author is not None else 'deleted',
        'create_at': datetime.fromtimestamp(comment.created),
        'content': comment.body,
        'ups': comment.ups
    }]

    for reply in comment.replies:
        comment_df.extend(formatting_comment(title, reply))

    return comment_df


def formatting_comments(submission):
    original_post = {
        'id': submission.id,
        'title': submission.title,
        'author': submission.author.name,
        'create_at': datetime.fromtimestamp(submission.created),
        'content': submission.selftext
    }
    comment_by_post = [original_post]

    comments = submission.comments.list()
    for comment in comments:
        comment = formatting_comment(submission.title, comment)
        comment_by_post.extend(comment)

    df = pd.DataFrame(comment_by_post)
    df = df.drop_duplicates(subset=['id'])
    return df


def formatting_post(submission):
    summary_by_post = {
        'id': submission.id,
        'title': submission.title,
        'url': 'https://www.reddit.com' + submission.permalink,
        'author': submission.author.name,
        'create_at': datetime.fromtimestamp(submission.created),
        '# of comments': submission.num_comments,
        'ups': submission.ups
    }

    return summary_by_post


def update_reddit_hisotry():
    # Replace these values with your Reddit API credentials
    client_id = '9K4IKSACH9LjkNpzxeNKcQ'
    client_secret = 'OsHJeEMHG0rzjBj8LLsZILW-6wZ7wg'
    user_agent = 'AnyMail440'

    # Initialize the PRAW Reddit client
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent)

    # Define the subreddit and search query
    subreddit_name = 'LocalLLaMA'
    search_query = 'Yi'

    # Fetch and print related posts from the subreddit
    subreddit = reddit.subreddit(subreddit_name)

    summary_df, post_df = [], []
    for submission in subreddit.search(search_query, sort='relevance'):
        summary_df.append(formatting_post(submission))
        submission.comments.replace_more(limit=0)
        post_df.append(formatting_comments(submission))

    summary_df = lable_week_and_month(pd.DataFrame(summary_df), 'create_at', None)
    post_df = pd.concat(post_df)

    export_to_excel(summary_df, "reddit_summary.xlsx")
    export_to_excel(post_df, "reddit_post.xlsx")


def sentiment_analysis():
    df_post = pd.read_excel('reddit_post.xlsx')
    df_summary = pd.read_excel('reddit_summary.xlsx')

    api = APIClient(config['API_KEY'], config['API_BASE'], model='yi-34b-chat')

    additional_df = []
    for title in df_summary['title']:
        content = f'title: {title}\n'
        for comment in df_post[df_post['title'] == title]['content']:
            content += f'comment: {comment}\n'

        response = api.get_SA_from_reddit_posts(content)
        response = api.response_to_json(response)
        additional_df.append(response)

        time.sleep(20)

    additional_df = pd.DataFrame(additional_df)
    df_summary = pd.concat([df_summary, additional_df], axis=1)

    df_summary['create_at'] = pd.to_datetime(df_summary['create_at'])

    export_to_excel(df_summary, "reddit_summary.xlsx")


# Main execution block to update GitHub star and issue history.
if __name__ == "__main__":
    update_reddit_hisotry()
    # sentiment_analysis()





