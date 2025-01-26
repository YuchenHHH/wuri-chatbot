import json
import os
import time
from pathlib import Path
from openai import OpenAI

class CatChatbot:
    def __init__(self):
        self.config = self._load_config()
        # 建立 OpenAI 客户端
        self.client = OpenAI(**self.config)
        # 存放历史聊天记录的文件夹
        self.history_dir = Path("chat_history")
        self.history_dir.mkdir(exist_ok=True)

        # 初始化会话
        self.session_id = self._init_session()
        self.history = self._load_history_if_exists(self.session_id)

    def _load_config(self):
        try:
            with open("config.json", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("\n❌ 喵呜...找不到 config.json 文件，无法开始主人～\n")
            exit(1)

    def _init_session(self) -> str:
        """
        询问用户是否要新建猫猫会话或继续旧会话，并返回选定的 session_id（文件名）。
        """
        print("\n============================")
        print("  😺 喵～欢迎来到猫猫聊天空间～")
        print("============================\n")

        while True:
            choice = input("要新建喵喵会话 [n] 还是继续之前的喵喵会话 [c]？(n/c): ").strip().lower()
            if choice == "n":
                # 新聊天
                print()
                custom_name = input("给新喵喵会话取个名字吧（直接回车则使用默认）: ").strip()
                if custom_name == "":
                    # 如果未输入，则使用默认名
                    custom_name = f"chat_{int(time.time())}"
                print(f"\n喵呜～已为你创建新的猫猫会话：{custom_name}\n")
                return custom_name
            elif choice == "c":
                # 继续旧聊天
                return self._choose_existing_session()
            else:
                print("\n🐱 喵？请输入 'n' 或 'c' 好吗～\n")

    def _choose_existing_session(self) -> str:
        """
        列出 `chat_history` 下所有 .md 文件，供铲屎官选择继续。
        如果没找到记录，则自动创建新会话。
        """
        md_files = sorted(self.history_dir.glob("*.md"), key=os.path.getmtime)
        if not md_files:
            print("\n🐱 喵～没有找到旧会话记录，咱们来新建一个吧～\n")
            default_name = f"chat_{int(time.time())}"
            return default_name

        print("\n铲屎官，可以选择以下旧喵喵会话：\n")
        for i, file_path in enumerate(md_files, start=1):
            print(f" {i}. {file_path.stem}")

        while True:
            choice = input("\n请输入要继续的会话序号 (或按回车重新创建): ").strip()
            if choice == "":
                default_name = f"chat_{int(time.time())}"
                print(f"\n喵呜～已为你创建新的猫猫会话：{default_name}\n")
                return default_name

            try:
                idx = int(choice)
                if 1 <= idx <= len(md_files):
                    chosen_file = md_files[idx - 1]
                    print(f"\n已选择继续猫猫会话：{chosen_file.stem}\n")
                    return chosen_file.stem
            except ValueError:
                pass

            print("\n喵～无效输入，请输入正确的序号或按回车新建会话。\n")

    def _load_history_if_exists(self, session_id: str):
        """
        如果存在同名的 .md 文件，就尝试读取对话内容。
        只提取用户(**You:**)和机器人(**回答:**)，忽略猫猫思考(**思考:**)，
        将它们导入 `self.history`，以便继续对话上下文。
        """
        md_file = self.history_dir / f"{session_id}.md"
        if not md_file.exists():
            return []

        history = []
        with open(md_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        user_prefix = "**You:**"
        assistant_prefix = "**回答:**"
        current_role = None
        content_accum = []

        for line in lines:
            line_stripped = line.strip()

            # 检测用户行
            if line_stripped.startswith(user_prefix):
                # 先保存上一个角色段落
                if current_role and content_accum:
                    history.append({
                        "role": current_role,
                        "content": "".join(content_accum).strip()
                    })
                    content_accum = []

                current_role = "user"
                content_accum.append(line_stripped[len(user_prefix):].strip() + "\n")

            # 检测机器人回答行
            elif line_stripped.startswith(assistant_prefix):
                if current_role and content_accum:
                    history.append({
                        "role": current_role,
                        "content": "".join(content_accum).strip()
                    })
                    content_accum = []

                current_role = "assistant"
                content_accum.append(line_stripped[len(assistant_prefix):].strip() + "\n")

            else:
                if current_role is not None:
                    content_accum.append(line)

        # 循环结束后，如果还有残留内容，再存一次
        if current_role and content_accum:
            history.append({
                "role": current_role,
                "content": "".join(content_accum).strip()
            })

        print(f"\n喵呜～从 {md_file.name} 载入了以前的猫猫对话，共 {len(history)} 条消息～\n")
        return history

    def _save_conversation(self, content: str):
        file_path = self.history_dir / f"{self.session_id}.md"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)

    def chat_loop(self):
        print("\n😺 喵呜～猫猫已待命（输入 'exit' 或 'quit' 离开）\n")
        while True:
            try:
                user_input = input("你（铲屎官）: ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    print("\n喵～下次再找我玩哦，拜拜～\n")
                    break
                if not user_input:
                    continue

                # 保存用户输入
                self._save_conversation(f"**You:** {user_input}\n\n")
                self.history.append({"role": "user", "content": user_input})

                # 获取流式响应
                response = self.client.chat.completions.create(
                    model="deepseek-reasoner",  # 如需更换模型名称，请在此处修改
                    messages=self.history,
                    stream=True
                )

                thinking = ""
                answer = ""
                has_thinking = False
                has_answer = False

                for chunk in response:
                    # 处理猫猫思考
                    if getattr(chunk.choices[0].delta, 'reasoning_content', None):
                        thinking_chunk = chunk.choices[0].delta.reasoning_content
                        thinking += thinking_chunk
                        if not has_thinking:
                            print("\n🐱 猫猫思考中: ", end="", flush=True)
                            has_thinking = True
                        print(thinking_chunk, end="", flush=True)

                    # 处理猫猫回答
                    if getattr(chunk.choices[0].delta, 'content', None):
                        answer_chunk = chunk.choices[0].delta.content
                        answer += answer_chunk
                        if not has_answer:
                            # 首次出现回答时，换行+提示
                            if has_thinking:
                                print("\n\n🐱💡 猫猫回答: ", end="", flush=True)
                            else:
                                print("\n🐱💡 猫猫回答: ", end="", flush=True)
                            has_answer = True
                        print(answer_chunk, end="", flush=True)

                # 如果只有文本回答没有思考，就确保输出换行
                if not has_thinking and has_answer:
                    print()

                # 记录到文件和内存
                if thinking or answer:
                    self._save_conversation(
                        f"**思考:** {thinking}\n\n"
                        f"**回答:** {answer}\n\n"
                    )
                    self.history.append({
                        "role": "assistant",
                        "content": answer
                    })

                print()  # 回答结束后，再额外空一行，增加可读性

            except KeyboardInterrupt:
                print("\n😿 喵～对话被打断了...\n")
                break
            except Exception as e:
                print(f"\n⚠️ 喵喵出错了: {str(e)}\n")
                # 出错时回滚最后一条用户消息
                if self.history and self.history[-1]["role"] == "user":
                    self.history.pop()

def main():
    bot = CatChatbot()
    bot.chat_loop()

if __name__ == "__main__":
    main()