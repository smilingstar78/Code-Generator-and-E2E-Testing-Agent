from app.core.llm import get_llm

try:
    print("Testing Groq API Connection...")
    llm = get_llm()
    response = llm.invoke("Hello! Confirm you are working by replying with 'API OK'.")
    print("Response:", response.content)
    print("\nGroq Model connected successfully!")
except Exception as e:
    print("\nGroq API Error:", str(e))