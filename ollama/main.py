import ollama

client = ollama.Client("127.0.0.1:11434")

model = "Jarvis"

prompt = "Who is father of world"

response = client.generate(model,prompt,stream=True)

for chunk in response:
    if 'response' in chunk:
        print(chunk['response'], end='', flush=True)

print()  # Final newline