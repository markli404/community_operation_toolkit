import requests
from bs4 import BeautifulSoup
import yaml
from util.datetime_util import *

# Load configuration from a YAML file
with open('./config.yaml', 'r') as file:
    config = yaml.safe_load(file)


# Function to fetch all Hugging Face model cards that contain specific keywords
def fetch_model_cards_by_name(name):
    print(f"Fetching model cards that contains keyword: {name}")
    page = 0  # Initialize pagination
    model_cards = []  # List to store found model cards

    # Loop through paginated results until no more model cards are found
    while True:
        # Construct URL with pagination and search query
        url = f'https://huggingface.co/models?p={page}&sort=trending&search={name}'
        response = requests.get(url)  # Send HTTP GET request

        # Check if response is successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all model card elements on the page
            model_card = soup.find_all('a', class_='block p-2')
            # Break loop if no model cards are found on the current page
            if len(model_card) == 0:
                break
            else:
                model_cards.extend(model_card)  # Add found model cards to the list
                page += 1  # Increment page number to fetch next set of results

    return model_cards  # Return the list of found model cards


# Function to format each model card into a structured data format
def formatting_model_cards(model_card, base_model_name):
    # Extract model owner and name from the model card
    model_card_df = {
        'base_model': base_model_name,
        'owner': (model_card.find('header').text.strip().split('/'))[0],
        'name': (model_card.find('header').text.strip().split('/'))[1]
    }

    # Exclude model cards that do not include the base model name in their name
    if base_model_name not in model_card_df['name']:
        return None
    # Convert updated time to ISO datetime format
    model_card_df['updated_time'] = ISO_string_to_datetime(model_card.find('time')['datetime'])

    # Extract download count, converting 'k' to thousands where applicable
    try:
        downloads = model_card.find('svg', class_='flex-none w-3 text-gray-400 mr-0.5').next_sibling.strip()
        if 'k' in downloads:
            downloads = float(downloads[:-1]) * 1000
        downloads = int(downloads)
    except:
        downloads = 0  # Default to 0 if not found or on error

    model_card_df['downloads'] = downloads  # Add downloads to the data

    # Extract likes, converting 'k' to thousands where applicable
    try:
        likes = model_card.find('svg', class_='flex-none w-3 text-gray-400 mr-1').next_sibling.strip()
        if 'k' in likes:
            likes = float(likes[:-1]) * 1000
    except:
        likes = 0  # Default to 0 if not found or on error

    model_card_df['likes'] = likes  # Add likes to the data

    return model_card_df  # Return the formatted model card data


# Function to fetch and format model cards for all models specified in the config
def get_all_hugging_face_history():
    all_model_card_df = []  # List to store all formatted model cards

    # Loop through each model name specified in the config
    for llm_name in config['hugging_face']:
        model_cards = fetch_model_cards_by_name(llm_name)  # Fetch model cards for the model

        # Format each model card
        for model_card in model_cards:
            model_card_df = formatting_model_cards(model_card, llm_name)
            if model_card_df is not None:
                all_model_card_df.append(model_card_df)

    # Label each model card with its week and month of update
    all_model_card_df = pd.DataFrame(all_model_card_df)
    all_model_card_df = lable_week_and_month(all_model_card_df, 'updated_time')

    return all_model_card_df


# Function to update the Excel file with the latest model card data
def update_hugging_face_model_card_history():
    print('--- Collecting hugging face relevant model cards  ---')

    all_model_card_df = get_all_hugging_face_history()  # Fetch and format all model cards

    # Create an Excel writer with specific date formats
    writer = pd.ExcelWriter(
        "hugging_face_model_cards.xlsx",
        engine="xlsxwriter",
        datetime_format="mmm d yyyy hh:mm:ss",
        date_format="yyyy-mm-dd",
    )
    # Write the DataFrame to an Excel file
    all_model_card_df.to_excel(writer, index=False)

    writer._save()  # Save the Excel file


# Main execution block
if __name__ == "__main__":
    update_hugging_face_model_card_history()  # Update the Hugging Face model
