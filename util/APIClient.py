from openai import OpenAI
import json


class APIClient:
    def __init__(self, API_KEY, API_BASE, model="yi-34b-chat", temperature=0.5, max_tokens=600):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def response_to_json(self, response):
        response = response.split('{')[1]
        response = response.split('}')[0]

        if response.endswith('。'):
            response += '"'

        if not response.endswith('\n'):
            response += '\n'

        response = '{' + response + '}'

        response = response.replace('\\', '\\\\')

        return json.loads(response)

    def get_respond(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        message = response.choices[0].message.content

        return message

    def get_FAQ_from_wechat_message(self, content):
        system_prompt = """你是一个中文的群聊总结的助手，你可以为一个微信的群聊记录，提取出有价值的提问回答，生成一篇用户常见问题汇总。"""

        prompt = '''
基于以上的群聊内容，总结成一个用户常见问题清单，注意，这个清单会被放到网站首页。
第一步，请你根据群聊内容提取出开发者的主要问题。
第二步，请你思考第一步提取的内容，你先自己读一读那些你提取的问题，去除掉像弱智一样的问题，把那些连问句都不是的问题删除。
第三步，以群聊内容作为参考，来回答第一步中提出的问题，多多思考。如果没要找到答案，请写无，不需要写其他内容。

每个问题以'Q:'开头，回答以'A:'开头。
提示：你可以通过谁发送的消息来更好的理解每句话的上下文。
'''
        user_prompt = f'{content}\n' + prompt

        res = self.get_respond(system_prompt, user_prompt)
        print(res)
        return res


    def get_FAQ_from_github_issue(self, content):
        system_prompt = "你是一个代码库运维助手，这里有一个关于大语言模型的项目，你可以为项目的开发者问题进行总结，提取主要问题，并收集回答，生成一个小的问答报告。"
        prompt = ''' 
        请帮我总结这个开发者的提问，以及官方人员的回答。你需要总结一个列表，每个问题以'Q:'开头，回答以'A:'开头：

        以下是开发者提问的帖子，以及所有的回复内容：
        '''
        user_prompt = prompt + f'\n{content}\n'

        return self.get_respond(system_prompt, user_prompt)

    def get_SA_from_reddit_posts(self, content):
        system_prompt = "你是reddit上的机器人，你需要通过给你的标题以及回帖来总结这篇帖子的主要讨论内容，记住你需要输出中文"
        prompt = ''' 
        请根据我给出的帖子的内容生成一个关于该帖子的总结，你需要总结这个帖子主要讨论了什么主题，以及总体的情感如何，如果有需要你可以标出多个主题。
        请输出json格式的结果，包含'主题'，'情感'，'总结'这三个key，情感，只需要选择‘积极’或‘消极’

        另外有以下要求：
        1. 话题必须与Yi大语言模型相关，如果不相关，请回复无
        2. 你必须把内容翻译成中文
        3. 100%遵循输出格式。

        以下是帖子内容：
        '''

        user_prompt = prompt + f'\n{content}\n'

        return self.get_respond(system_prompt, user_prompt)

    def get_chat_summary(self, content):
        system_prompt = "你是一个中文的群聊总结的助手，你可以为一个微信群一天的聊天内容总结出多个讨论话题摘要。"
        prompt = ''' 
请帮我将给出的群聊内容总结多个讨论话题摘要，每个讨论点需要包含以下内容：
    1. 讨论话题：
    2. 参与者：
    3. 过程：
    4. 你自己对这个讨论话题的评价：

你的输出需要符合这样的格式：
    讨论话题：
    参与者：
    过程：
    评价：
        
以下是聊天记录：
'''

        user_prompt = prompt + f'\n{content}\n'

        return self.get_respond(system_prompt, user_prompt)
