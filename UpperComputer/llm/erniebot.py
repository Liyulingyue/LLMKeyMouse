import erniebot
from utils import LOG


class Ernie_TransChain:
    def __init__(self, model_name: str, access_token: str):
        self.model_name = model_name
        self.access_token = access_token

        erniebot.api_type = 'aistudio'
        erniebot.access_token = self.access_token

    def construct_prompt(self, user_input: str, structure: str) -> str:
        prompt = f"""
        请按照要求将以下用户输入转换成指定的规范指令输出,
        输出示例如下：<{structure}>
        用户输入：<{user_input}>
        请输出转化后的结果：
        """
        return prompt

    def call_ernieChat(self, prompt: str):
        """调用 ERNIE"""
        try:
            response = erniebot.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.get_result()
        except Exception as e:
            LOG.error(f"调用 ERNIE Bot 出错: {e}")
            return None

    def run(self, user_input: str, structure: str):
        try:
            # 构建 Prompt
            prompt = self.construct_prompt(user_input, structure)
            LOG.debug(f"开始调用模型：{prompt}")

            # 调用 ERNIE Bot 获取响应
            result = self.call_ernieChat(prompt)
            LOG.debug(f"LLM返回结果为：{result}")
            return result, True
        except Exception as e:
            LOG.error(f"执行过程中发生错误: {e}")
            return f"执行过程中发生错误: {str(e)}", False

