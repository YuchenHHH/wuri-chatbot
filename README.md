# 猫猫聊天机器人 (wuri-Chatbot)

	一个可爱猫猫风格的命令行聊天机器人
可与 OpenAI 进行对话，并自动保存、载入聊天历史～

功能简介
	•	猫猫语气互动：以猫猫口吻进行对话提示与回复，营造可爱的聊天氛围
	•	新建或续写聊天：启动时可选择新建喵喵会话，或从已有 .md 文件中载入旧聊天历史
	•	自动记录：每次对话会自动保存到 chat_history/会话名.md 文件中，方便日后查看或继续
	•	思考 + 回答：同时支持流式输出「思考内容」和「最终回答」，带给你沉浸式体验

环境与依赖
	1.	Python 3.7+
	2.	OpenAI Python 库：

pip install openai


	3.	配置文件 config.json：

{
  "api_key": "YOUR_OPENAI_API_KEY",
  "base_url": "https://api.deepseek.com/v1"
}

	•	api_key ：你的 OpenAI API 密钥
	•	其余字段可根据需要修改或直接删除

使用方法
	1.	克隆或下载本项目

git clone https://github.com/yourname/cat-chatbot.git
cd cat-chatbot


	2.	安装依赖

pip install -r requirements.txt

	若未提供 requirements.txt，可手动安装必要依赖（如 openai）。

	3.	创建并填写 config.json
将你的 OpenAI API Key 等配置信息写入 config.json。示例参考上文「环境与依赖」。
	4.	运行

python chatbot.py

你将看到类似以下界面：

============================
  😺 喵～欢迎来到猫猫聊天空间～
============================

要新建喵喵会话 [n] 还是继续之前的喵喵会话 [c]？(n/c):

	•	输入 n：新建一个会话，可为其命名。若直接回车，则使用默认的时间戳名称
	•	输入 c：选择继续某个已存在的 .md 聊天文件

	5.	开始对话
	•	在提示后输入你的内容并按回车
	•	程序将实时流式输出猫猫的「思考」与「回答」
	•	输入 exit / quit 可结束聊天
	6.	查看或续写聊天记录
	•	所有对话会保存在 chat_history/ 文件夹，以 .md 格式
	•	再次运行程序时，选择【继续旧聊天】即可从对应文件载入上下文

文件结构

cat-chatbot/
├── chatbot.py            # 主脚本（含猫猫对话逻辑）
├── config.json           # OpenAI 接口配置（自行创建）
├── chat_history/
│   ├── chat_1679999999.md   # 某次对话的历史记录
│   └── ...
└── README.md             # 本文件


贡献与许可
	•	如无特殊说明，本项目基于 MIT License 开源。具体细节请查看项目根目录下的 LICENSE 文件。

喵～祝你聊天愉快！