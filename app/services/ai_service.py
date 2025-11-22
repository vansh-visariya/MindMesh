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
        Your task is to answer the user's question based primarily on the information provided in the article text.
        
        Guidelines:
        1. **Summarization**: If asked to summarize, provide a concise summary of the article content.
        2. **Entity Context**: If the user asks about specific entities (people, organizations, places) mentioned in the article, you MAY use your general knowledge to briefly explain *who* or *what* they are (e.g., "X is the President of Y"), but strictly limit any *events*, *actions*, or *quotes* attributed to them to what is explicitly stated in the article.
        3. **Strictness**: Do not hallucinate facts or bring in outside news events not mentioned in the text.
        4. **Uncertainty**: If the answer is not in the article and cannot be inferred from general context definitions, state that you cannot answer based on the available information."""

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
