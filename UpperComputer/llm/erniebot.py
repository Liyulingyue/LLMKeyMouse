import json
import erniebot
from utils import LOG


class Ernie_TransChain:
    def __init__(self, model_name: str, access_token: str):
        """
        初始化LLMChain
        """
        self.model_name = model_name
        self.access_token = access_token

        # 配置文心 API
        erniebot.api_type = 'aistudio'
        erniebot.access_token = self.access_token

        # 定义支持的设备和操作类型
        self.supported_devices = {
            "mouse": ["move", "click"],
            "keyboard": ["write"]
        }

    def construct_prompt(self, user_input: str) -> str:
        """
        构建 Prompt
        """
        prompt = f"""
你是一个指令生成助手，请根据以下用户输入的自然语言，解析生成符合 JSON 格式的执行指令。
每条指令需要包含以下字段：
- "order"：指令的执行顺序，从 1 开始递增
- "device"：设备名称，仅支持 "mouse" 和 "keyboard"
- "operation"：设备的操作类型，"mouse" 支持 "move" 和 "click"，"keyboard" 支持 "write"
- 其他字段：
  - 如果设备为 "mouse"，需要提供 "x" 和 "y"（坐标移动值）以及 "steps"（移动次数）
  - 如果设备为 "keyboard"，需要提供 "text"（输入的文本内容）
为每条指令添加字段：
- "err"：0 表示成功，-1 表示失败
- "message"：指令生成的状态消息
如果输入的指令不在支持范围内，请返回带有 "err": -1 和相应 "message" 的指令。

用户输入：{user_input}

### 示例输入：
用户输入：鼠标移动到右下方，每次移动 10 和 5，共计 50 次，然后键盘输入 "Hello, CircuitPython!"

### 示例输出：
[
    {{
        "order": 1,
        "device": "mouse",
        "operation": "move",
        "x": 10,
        "y": 5,
        "steps": 50,
        "err": 0,
        "message": "成功转换指令"
    }},
    {{
        "order": 2,
        "device": "keyboard",
        "operation": "write",
        "text": "Hello, CircuitPython!",
        "err": 0,
        "message": "成功转换指令"
    }}
]

请根据以下用户输入生成符合上述规则的 JSON 数据：
"""
        return prompt

    def validate_command(self, commands: list) -> list:
        """
        校验生成的指令
        """
        validated_commands = []
        for cmd in commands:
            device = cmd.get("device")
            operation = cmd.get("operation")

            # 检查合法性
            if device in self.supported_devices and operation in self.supported_devices[device]:
                cmd["err"] = 0
                cmd["message"] = "成功转换指令"
            else:
                cmd["err"] = -1
                cmd["message"] = f"当前设备或操作不支持：device={device}, operation={operation}"

            validated_commands.append(cmd)

        return validated_commands

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

    def extract_json_from_llm_answer(self, result, start_str="```json", end_str="```", replace_list=["\n"]):
        """
        从 LLM 返回结果中提取 JSON 数据并解析为字典。
        """
        try:
            # 找到起始和结束标记符
            s_id = result.index(start_str)
            e_id = result.index(end_str, s_id + len(start_str))

            # 提取 JSON 部分
            json_str = result[s_id + len(start_str):e_id]

            # 清理字符串
            for replace_str in replace_list:
                json_str = json_str.replace(replace_str, "")

            # 转换为字典
            json_dict = json.loads(json_str)
            return json_dict
        except ValueError as e:
            LOG.error(f"未找到有效的 JSON 部分或解析失败: {e}")
            raise ValueError(f"未找到有效的 JSON 部分或解析失败: {e}")
        except json.JSONDecodeError as e:
            LOG.error(f"提取到的字符串无法解析为 JSON: {e}")
            raise ValueError(f"提取到的字符串无法解析为 JSON: {e}")

    def get_llm_json_answer(self, prompt):
        """
        调用 LLM 并提取 JSON 数据。
        """
        result = self.call_ernieChat(prompt)
        LOG.debug(f"LLM 返回结果为：{result}")
        # 提取并解析 JSON
        try:
            json_dict = self.extract_json_from_llm_answer(result)
            LOG.debug(f"提取的 JSON 内容：{json_dict}")
            return json_dict
        except Exception as e:
            LOG.error(f"提取 JSON 时出错: {e}")
            return [{"err": -1, "message": "提取 JSON 数据失败"}]

    def run(self, user_input: str):
        """
        主执行逻辑：构建 Prompt，调用 LLM，提取 JSON，校验指令。
        """
        try:
            # 构建 Prompt
            prompt = self.construct_prompt(user_input)
            LOG.debug(f"构建的 Prompt 为：{prompt}")

            # 获取 JSON 数据
            commands = self.get_llm_json_answer(prompt)

            # 校验指令合规
            validated_commands = self.validate_command(commands)

            # 转换 commands 为commands_str
            try:
                validated_commands_str = json.dumps(validated_commands, ensure_ascii=False)
                return validated_commands_str, True  # 返回 JSON 字符串和成功状态
            except (TypeError, ValueError) as e:
                # JSON 转换失败，记录错误并返回
                error_message = f"错误：无法将 commands 转换为 JSON 字符串 - {e}"
                LOG.error(error_message)
                return error_message, False

        except Exception as e:
            # 捕获所有其他异常，记录日志并返回
            error_message = f"执行过程中发生错误: {str(e)}"
            LOG.error(error_message)
            return [{"err": -1, "message": error_message}], False
