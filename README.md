# Quick Start
## 0. Setup Environment
### 0.a Clone GitHub Repository
```commandline
git clone https://github.com/markli404/community_operation_toolkit.git
```
### 0.b Install Required Packages
```commandline
cd community_healthiness
pip install -r requirements.txt
```
## 1. Edit Configurations
### 1.a Add GitHub Personal Access Token
In `config.yaml`, replace your PAT with `your_token_goes_here`, it should look something like
```commandline
github:
  token: abc_UYJ666dvAAAo5AA3sjABCqwAAAxoD3XIKuN
```
### 1.b Add webhook_url for Feishu bot
In `config.yaml`, replace your webhook url of your Feishu custom bot in with `your_webhook_url_goes_here`. It should look something like
```commandline
webhook_url_gh_bot: https://open.feishu.cn/open-apis/bot/v2/hook/8qwewe931-dsgsaf4ed-b0fb-wewqasdr
webhook_url_hf_bot: https://open.feishu.cn/open-apis/bot/v2/hook/8d6sadase1931-dsgfae44ed-b0fb-wewqasdr
```
Notice that, `webhook_url_gh_bot` is for GitHub issue feed bot, and `webhook_url_hf_bot` is for Hugging Face issue feed bot.

To create your webhook url, please check this [document](https://open.feishu.cn/community/articles/7271149634339422210)
### 1.c  Add Owner and Repo for Projects that You Interested in GitHub
First, add the name of the project you interesed in to `all` in `config.yaml`. For example,
```yaml
github_repo: [this_project]
```
Next, add owner and repo of that project as following:
```yaml
My_Project:
  owner: markli404
  repo: community_operation_toolkit
```
Notice that `this_project` is just a name you give to the project, it does not have to be the real name of the project.
However `owner` and `repo` has to be exactly the same as the project claimed.
### 1.d Add keywords You Interested in Hugging Face
For anything that you want to search in Hugging Face, you can simply add that keyword to `config.yaml`, and the script will do the work for you. For example,
```yaml
hugging_face: [llama]
```
It will record all model cards that derived from llama and their downloads.
### 1.f Add your API key and API base
To use features involving LLMs like Yi, please enter your API key in `config.yaml`, replacing `your_api_key_goes_here`. It should look something like
```commandline
API_BASE: "https://api.lingyiwanwu.com/v1"
API_KEY: "ef79mdnas9013j4rlkowq013rc7"
```

## 2. GitHub/Hugging Face Issue Bot
It is designed to provide instant help to developers by sending new posted issues in GitHub or Hugging Face to Feishu group chat.
### 2.a Requirements
`webhook_url` and `github_PAT` are required to run those bots. Please add those to `config.yaml`, which are demostrated in part 1.a and part 1.b.
### 2.b Run
The scripts are located at
```bash
|-- community_operation_toolkit
|   |-- bots
|   |   |-- github_issue_feeding_bot.py
|   |   |-- huggingface_issue_feeding_bot.py
|   |-- ...

```

It is supposed to work by simpling running the scripts by using either command line or IDEs like PyCharm.

## 3. Community Healthiness Dashboard
### 3.a Requirements
Please have your GitHub PAT added you `config.yaml`, otherwise please read part 1.a. If you want to add more communities to compare, please read part 1.c and part 1.d.
### 3.b Run
#### 3.b.i Github 
Simply run `update_github_history.py` using command line or IDEs, it will generate `github_issues.xlsx` which contains all issues in each community, and `github_star.xlsx` which contains information about star of each community.
```commandline
python update_github_history.py
```
#### 3.b.ii Hugging Face
Simply run `update_hugging_face_history.py` using command line or IDEs, it will generate `hugging_face_model_cards.xlsx` which contains information about model cards that are related to each keyword.
```commandline
python update_hugging_face_history.py
```
#### 3.b.iii Reddit - not fully developed
Simply run `update_reddit.py` using command line or IDEs, it will generate `reddit_post.xlsx` and `reddit_summary.xlsx` which records all posts that related to `Yi` in `LocalLLaMA` forum.
```commandline
python update_reddit.py
```
#### 3.b.iv Hacker News - not fully developed
Basic functions like searching posts by keywords and extracting key information.

## 4. WeChat message to FAQ
### 4.a Requirements
This part will use generated content from LLMs, please have your API key added to `config.yaml`, otherwise please read part 1.f.
### 4.b Extract WeChat Message
Chat history is extracted using [MemoTrace](https://github.com/LC044/WeChatMsg/releases).
### 4.c Clean/Format Chat History
Run `clean_wechat_messages.py` under `wechat` folder, and it will generate a clean version of chat history named `messages.csv` under `wechat` folder.
update_hugging_face_history
```commandline
python clean_wechat_messages.py path_to_raw_chat_history.csv
```
### 4.d Generate FAQ from WeChat History
Run `generate_FAQ.py`. It will split chat history into small chunks with size of 100, and have overlaps of 20.
```commandline
python generate_FAQ.py path_to_clean_chat_history.csv
```