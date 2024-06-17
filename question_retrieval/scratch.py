from interpreter import interpreter

interpreter.llm.api_key = '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'
interpreter.llm.model = "gpt-4o"
interpreter.llm.context_window = 128000
interpreter.llm.max_tokens = 3000

interpreter.chat("Hello")  # Starts an interactive chat


# print(interpreter.messages)
# interpreter.messages = []

print(interpreter.messages[-1]["content"])