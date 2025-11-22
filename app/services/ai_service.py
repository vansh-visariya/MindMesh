from groq import AsyncGroq
from app.core.config import settings

class AIService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "llama3-8b-8192" # Efficient model for this task

    async def generate_answer(self, article_content: str, question: str) -> str:
        if not article_content:
            return "I cannot answer questions about this article because I couldn't read its content."

        system_prompt = """You are a helpful news analyst assistant. 
        You will be provided with the text of a news article. 
        Your task is to answer the user's question based ONLY on the information provided in the article text. 
        If the answer is not in the article, state that you cannot answer based on the available information.
        Do not use outside knowledge."""

        user_prompt = f"""Article Content:
        {article_content}

        Question: {question}"""

        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating AI answer: {e}")
            return "Sorry, I encountered an error while processing your request."

ai_service = AIService()
