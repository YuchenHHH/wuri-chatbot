# chatbot.py
import json
import os
import time
from pathlib import Path
from openai import OpenAI

class SimpleChatbot:
    def __init__(self):
        self.config = self._load_config()
        self.client = OpenAI(**self.config)
        self.history = []
        self.session_id = f"chat_{int(time.time())}"
        self.history_dir = Path("chat_history")
        self.history_dir.mkdir(exist_ok=True)

    def _load_config(self):
        try:
            with open("config.json") as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ 找不到 config.json 文件")
            exit(1)

    def _save_conversation(self, content: str):
        file_path = self.history_dir / f"{self.session_id}.md"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)

    def _print_stream(self, stream, prefix: str):
        print(f"\n{prefix}: ", end="", flush=True)
        full_content = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            full_content += content
        return full_content
    def chat_loop(self):
        print("\n🌟 简单聊天机器人已启动（输入 'exit' 退出）\n")
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    print("再见！")
                    break
                if not user_input:
                    continue

                # 保存用户输入
                self._save_conversation(f"**You:** {user_input}\n\n")
                self.history.append({"role": "user", "content": user_input})

                # 获取流式响应
                response = self.client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=self.history,
                    stream=True
                )

                thinking = ""
                answer = ""
                has_thinking = False
                has_answer = False

                for chunk in response:
                    # 处理思考内容
                    if getattr(chunk.choices[0].delta, 'reasoning_content', None):
                        thinking_chunk = chunk.choices[0].delta.reasoning_content
                        thinking += thinking_chunk
                        if not has_thinking:
                            print("\n🤔 思考: ", end="", flush=True)
                            has_thinking = True
                        print(thinking_chunk, end="", flush=True)

                    # 处理回答内容
                    if getattr(chunk.choices[0].delta, 'content', None):
                        answer_chunk = chunk.choices[0].delta.content
                        answer += answer_chunk
                        if not has_answer:
                            if has_thinking:
                                print("\n💡 回答: ", end="", flush=True)
                            else:
                                print("\n💡 回答: ", end="", flush=True)
                            has_answer = True
                        print(answer_chunk, end="", flush=True)

                # 处理纯文字回答没有思考的情况
                if not has_thinking and has_answer:
                    print()  # 确保最后换行

                # 保存到文件和历史记录
                if thinking or answer:
                    self._save_conversation(
                        f"**思考:** {thinking}\n\n"
                        f"**回答:** {answer}\n\n"
                    )
                    self.history.append({
                        "role": "assistant",
                        "content": answer
                    })

            except KeyboardInterrupt:
                print("\n🛑 对话已中断")
                break
            except Exception as e:
                print(f"\n⚠️ 发生错误: {str(e)}")
                # 回滚未完成的对话
                if self.history and self.history[-1]["role"] == "user":
                    self.history.pop()

if __name__ == "__main__":
    bot = SimpleChatbot()
    bot.chat_loop()