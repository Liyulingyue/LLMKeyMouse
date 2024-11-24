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
        构建简化版 Prompt
        """
        prompt = f"""
    你是一个指令生成助手，请根据以下用户输入的自然语言，解析生成符合 JSON 格式的单步执行指令。
    每条指令需要包含以下字段：
    - "order"：指令的执行顺序，从 1 开始递增
    - "device"：设备名称，仅支持 "mouse" 和 "keyboard"
    - "operation"：设备的操作类型：
      - 如果设备为 "mouse"，支持 "move" 和 "click"
      - 如果设备为 "keyboard"，支持 "write"
    - 其他字段：
      - 如果操作为 "move"，需要提供：
        - "direction"：移动方向，仅支持 "x" 或 "y"
        - "steps"：移动的像素数量（正数为正向移动，负数为负向移动）
      - 如果操作为 "write"，需要提供：
        - "text"：要输入的文本内容

    每条指令仅对应一个动作。如果需要多个动作，请分为多条独立的指令。

    用户输入：{user_input}

    ### 示例输入：
    用户输入：鼠标向右移动 100 像素，然后鼠标向下移动 50 像素，最后键盘输入 "Hello"

    ### 示例输出：
    [
        {{
            "order": 1,
            "device": "mouse",
            "operation": "move",
            "direction": "x",
            "steps": 100
        }},
        {{
            "order": 2,
            "device": "mouse",
            "operation": "move",
            "direction": "y",
            "steps": 50
        }},
        {{
            "order": 3,
            "device": "keyboard",
            "operation": "write",
            "text": "Hello"
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

    def commands_format(self, valid_commands: list) -> list:
        """
        提取合规指令中的键值，生成指定格式的字符串列表（每个最多 64 字符）。

        格式：
        - 第一个位置：设备数值（mouse=0, keyboard=1）
        - 第二个位置：64（表示长度）
        - 第三个位置：操作类型数值
            - mouse: move=1, click=2
            - keyboard: write=1
        - 后续字段：
            - 如果是 mouse 且操作为 move，拼接 "direction" 和 "steps"
            - 如果是 mouse 且操作为 click，无需后续字段
            - 如果是 keyboard 且操作为 write，拼接 "text"

        :param valid_commands: 合规的 JSON 对象列表
        :return: 包含多个最多 64 字符的字符串的列表
        """
        result = []

        for item in valid_commands:
            # 获取设备并映射为数值
            device = item.get("device", "")
            device_value = "0" if device == "mouse" else "1" if device == "keyboard" else "-1"  # -1 表示未知设备

            # 固定长度标志
            length_flag = "64"

            # 获取操作类型
            operation = item.get("operation", "")
            if device == "mouse":
                operation_value = "1" if operation == "move" else "2" if operation == "click" else "-1"
            elif device == "keyboard":
                operation_value = "1" if operation == "write" else "-1"
            else:
                operation_value = "-1"  # 未知操作

            # 按设备和操作类型拼接指令
            if device == "mouse" and operation == "move":
                # mouse 的 move 需要 direction 和 steps
                direction = item.get("direction", "unknown")  # 默认值为 unknown
                steps = str(item.get("steps", 0))  # 默认步数为 0
                formatted_str = f"{device_value}{length_flag}{operation_value}{direction}{steps}"

            elif device == "mouse" and operation == "click":
                # mouse 的 click 不需要额外字段
                formatted_str = f"{device_value}{length_flag}{operation_value}"

            elif device == "keyboard" and operation == "write":
                # keyboard 的 write 需要 text
                text = item.get("text", "")  # 默认文本为空
                formatted_str = f"{device_value}{length_flag}{operation_value}{text}"

            else:
                # 未知设备或操作，返回错误字符串
                formatted_str = f"{device_value}{length_flag}-1"

            # 截断64 字符
            result.append(formatted_str[:64])

        return result

    def json_run(self, user_input: str):
        """
        主执行逻辑：构建 Prompt，调用 LLM，提取 JSON，校验指令。
        """
        try:
            # 构建 Prompt
            prompt = self.construct_prompt(user_input)
            LOG.debug(f"构建的 Prompt 为：{prompt}")

            # 获取 JSON 数据
            commands = self.get_llm_json_answer(prompt)

            # 把json转换成
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

    def run(self, user_input: str):
        """
        主执行逻辑：构建 Prompt，调用 LLM，提取 JSON，校验指令，并返回格式化的字符串列表。
        """
        try:
            # 构建 Prompt
            prompt = self.construct_prompt(user_input)
            LOG.debug(f"构建的 Prompt 为：{prompt}")

            # 获取 JSON 数据
            commands = self.get_llm_json_answer(prompt)

            # 校验指令合规
            validated_commands = self.validate_command(commands)

            # 检查是否有至少一个成功指令
            valid_commands = [cmd for cmd in validated_commands if cmd.get("err") == 0]
            if not valid_commands:
                # 如果没有合规指令，直接返回错误
                error_message = "错误：没有合规的指令，无法执行后续操作"
                LOG.error(error_message)
                return error_message, False

            # 提取键值并生成字符串列表
            formatted_strings = self.commands_format(valid_commands)

            # 返回字符串列表和成功状态
            return formatted_strings, True

        except Exception as e:
            # 捕获所有其他异常，记录日志并返回
            error_message = f"执行过程中发生错误: {str(e)}"
            LOG.error(error_message)
            return [{"err": -1, "message": error_message}], False

