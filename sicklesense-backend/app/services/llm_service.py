from groq import Groq
from app.config import settings

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def generate_answer(self, query: str, context: str) -> str:
        system_prompt = (
            "You are SickleSense AI, an expert clinical decision-support assistant specializing in "
            "Sickle Cell Disease (SCD) based on official clinical guidelines (NHLBI 2014, WHO 2026, and peer-reviewed studies).\n\n"
            "Instructions:\n"
            "1. Answer strictly using the provided context. If insufficient evidence exists, state the limitation clearly.\n"
            "2. Provide direct, actionable medical summaries with bold headers, dosage specifics, and safety considerations where applicable.\n"
            "3. Reference the specific guideline and page number in parentheses where relevant."
        )

        user_prompt = f"Clinical Context:\n{context}\n\nClinical Query: {query}\n\nStructured Answer:"

        response = self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=2048,
        )

        return response.choices[0].message.content
