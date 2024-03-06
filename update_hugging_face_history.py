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

    model_cards = []# List to store found model cards
    response = requests.get(
        "https://huggingface.co/api/models",
        params={"search": name, "full": "True"},
        headers={}
    ).json()

    for model_card in response:
        # Remove model cards that has 0 download
        if model_card['downloads'] == 0:
            continue

        # Exclude model cards that does not contain the keyword in its name
        if name not in model_card['id'].split('/')[1]:
            continue

        model_cards.append(model_card)


    return model_cards  # Return the list of found model cards


# Function to format each model card into a structured data format
def formatting_model_cards(model_card, base_model_name):
    url = f"https://huggingface.co/{model_card['id']}"
    name = model_card['id'].split('/')[1]
    # Extract model owner and name from the model card
    model_card_df = {'base_model': base_model_name,
                     'owner': model_card['id'].split('/')[0],
                     'name': f'=HYPERLINK("{url}", "{name}")',
                     'downloads': model_card['downloads'],
                     'create_at': ISO_string_to_datetime(model_card['createdAt'])}

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
    all_model_card_df = lable_week_and_month(all_model_card_df, 'create_at', 'base_model')

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

