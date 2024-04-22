import yaml
from util.datetime_util import *
from util.APIClient import *
import requests

# Load configuration settings from a YAML file.
with open('./config.yaml', 'r') as file:
    config = yaml.safe_load(file)


def fetch_by_id(id):
    url = f'https://hacker-news.firebaseio.com/v0/item/{id}.json?print=pretty'
    response = requests.get(url).json()

    return response


def formatting_single_comment(title, response):
    comment = {
        'id': response['id'],
        'title': title,
        'content': response['text'],
        'author': response['by'],
        'create_time': datetime.fromtimestamp(response['time']),
    }

    return comment

def get_all_descendants_comments(title, response):
    story_df = []
    try:
        comment_ids = response['kids']
    except:
        comment_ids = []

    for comment_id in comment_ids:
        comment_response = fetch_by_id(comment_id)
        if 'text' in comment_response.keys():
            story_df.append(formatting_single_comment(title, comment_response))
        story_df.extend(get_all_descendants_comments(title, comment_response))

    return story_df


def formatting_summary(response):
    summary = {
        'id': response['id'],
        'title': response['title'],
        'url': 'https://news.ycombinator.com/item?id=' + str(response['id']),
        'author': response['by'],
        'create_time': datetime.fromtimestamp(response['time']),
        '# of comments': response['descendants'],

    }
    return summary


def update_reddit_hisotry(id=39746468):
    df = []
    response = fetch_by_id(id)
    summary = formatting_summary(response)
    posts = get_all_descendants_comments(response['title'], response)

    return response

# Main execution block to update GitHub star and issue history.
if __name__ == "__main__":
    # update_reddit_hisotry()
    # sentiment_analysis()

    url = f'http://hn.algolia.com/api/v1/search?query=Yi&tags=story&numericFilters=num_comments>=20'
    response = requests.get(url).json()

    print(0)




