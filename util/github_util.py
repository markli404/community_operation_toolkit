import yaml
import requests
import sys

# Function to make a paginated request to GitHub API and gather all data from a specific endpoint.
def make_github_request(url, token, params=None):
    params = params or {}
    params.update({"per_page": 100})  # Default to 100 items per page for maximum efficiency.
    all_data = []
    headers = {
        'Authorization': f'token {token}',  # Authentication token from config.
        'Accept': 'application/vnd.github.v3.star+json'  # Ensure compatibility with the GitHub API version 3.
    }
    # Loop to handle pagination.
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
        except:
            print("Some error occurred while fetching through GitHub API")
            sys.exit(1)

        # Break loop if request fails or no more data is available.
        if response.status_code != 200 or not response.json():
            break
        all_data.extend(response.json())
        # If there's a next page, update the URL and continue; otherwise, break.
        if 'next' not in response.links:
            break
        url = response.links['next']['url']
    return all_data