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

                self._save_conversation(f"**You:** {user_input}\n\n")
                self.history.append({"role": "user", "content": user_input})

                response = self.client.chat.completions.create(
                    model="deepseek-reasoner",
                    messages=self.history,
                    stream=True
                )

                assistant_response = ""
                thinking_stream = (chunk for chunk in response if chunk.choices[0].delta.reasoning_content)
                answer_stream = (chunk for chunk in response if chunk.choices[0].delta.content)

                thinking = self._print_stream(thinking_stream, "🤔 思考")
                answer = self._print_stream(answer_stream, "💡 回答")
                
                self._save_conversation(f"**思考:** {thinking}\n\n**回答:** {answer}\n\n")
                self.history.append({"role": "assistant", "content": answer})

            except KeyboardInterrupt:
                print("\n🛑 对话已中断")
                break

if __name__ == "__main__":
    bot = SimpleChatbot()
    bot.chat_loop()