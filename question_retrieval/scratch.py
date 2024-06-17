from interpreter import interpreter

interpreter.llm.api_key = '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'
interpreter.llm.model = "gpt-4o"
# interpreter.model = "gpt-3.5-turbo"
interpreter.llm.context_window = 128000
interpreter.llm.max_tokens = 3000
interpreter.auto_run = True
interpreter.chat()  # Starts an interactive chat
# interpreter.chat("Hello")  

# print(interpreter.messages)
# interpreter.messages = []

# print(interpreter.messages[-1]["content"])