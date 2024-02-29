from openai import OpenAI

class APIClient:
    def __init__(self, API_KEY, API_BASE, model="yi-34b-chat", temperature=0.2):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE
        )
        self.model = model
        self.temperature = temperature

    def get_respond(self, system_prompt, user_prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=512
            )
            message = response.choices[0].message.content
        except:
            message = ''
            print('Some error occurred... Please try again.')

        return message

    def get_FAQ_from_wechat_message(self, content):
        system_prompt = "你是一个中文的群聊总结的助手，你可以为一个微信的群聊记录，提取在重点讨论的问题，并收集回答"
        prompt = ''' 
        请帮我将给出的群聊内容总结成一个今日的群聊报告，提取群聊中开发者的主要问题，以及大家对于该问题的回答。
        你需要总结一个列表，每个问题以'Q:'开头，回答以'A:'开头：

        另外有以下要求：
        1. 话题必须与技术开发相关
        2. 回答需要准确，涵盖所有细节

        以下是群聊内容：
        '''

        user_prompt = prompt + f'\n{content}\n'

        return self.get_respond(system_prompt, user_prompt)

    def get_FAQ_from_github_issue(self, content):
        system_prompt = "你是一个代码库运维助手，这里有一个关于大语言模型的项目，你可以为项目的开发者问题进行总结，提取主要问题，并收集回答，生成一个小的问答报告。"
        prompt = ''' 
        请帮我总结这个开发者的提问，以及官方人员的回答。你需要总结一个列表，每个问题以'Q:'开头，回答以'A:'开头：

        以下是开发者提问的帖子，以及所有的回复内容：
        '''
        user_prompt = prompt + f'\n{content}\n'

        return self.get_respond(system_prompt, user_prompt)


