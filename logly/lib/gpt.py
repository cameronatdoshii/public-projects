import openai

class gpt:

    def __init__(self, key='YOUR_API_KEY'):
        self.key = key

    def q_and_a(self, messages, tokens, temperature):
        openai.api_key = self.key

        response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=tokens,
        n=1,
        temperature=temperature,    
        )
        return response.choices[0].message['content'].strip()
