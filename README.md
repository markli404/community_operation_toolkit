# Quick Start
## 0. Setup Environment
### 0.a Clone GitHub Repository
```commandline
git clone https://github.com/markli404/CommunityHealthiness.git
```
### 0.b Install Required Packages
```commandline
cd CommunityHealthiness
pip install -r requirements.txt
```
## 1. Edit Configurations
### 1.a Add GitHub Personal Access Token
In `config.yaml`, replace your PAT with `your_token_goes here`, it should look something like
```commandline
github:
  token: abc_UYJ666dvAAAo5AA3sjABCqwAAAxoD3XIKuN
  data_dir: ./data
```
### 1.b Add Owner and Repo for Projects that You Interested in
First, add the name of the project you interesed in to `all` in `config.yaml`. For example,
```yaml
all: [Yi, My_Project]
```
Next, add owner and repo of that project as following:
```yaml
My_Project:
  owner: my_name
  repo: my_project
```
Notice that `My_Project` is just a name you give to the project, it does not has to be the real name of the project.
However `owner` and `repo` has to be exactly the same as the project claimed.
## 2. Run Dashboard
```commandline
python ./CommunityHealthiness/main.py
```