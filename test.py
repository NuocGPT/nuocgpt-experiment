from llama_index.llms.gemini import Gemini

resp = Gemini().complete("Write a poem about a magic backpack")
print(resp)
