from google import genai
from google.genai import types


class GeminiProvider:
    """Generate text using the asynchronous Gemini Developer API client."""

    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key).aio
        self.model = model

    async def generate_text(self, prompt: str) -> str:
        response = await self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Eres un asistente meteorológico. Interpreta exclusivamente "
                    "los datos proporcionados: no inventes mediciones, condiciones "
                    "ni predicciones. Redacta en español de España, con lenguaje "
                    "claro y práctico. Resume la situación, explica la evolución "
                    "relevante y ofrece recomendaciones proporcionadas sobre "
                    "ropa, paraguas, temperatura o exposición UV cuando los datos "
                    "lo justifiquen. Si los datos no permiten valorar algo, "
                    "indícalo brevemente. No presentes el análisis como una "
                    "predicción adicional. Limita la respuesta a 180 palabras."
                ),
                temperature=0.3,
                max_output_tokens=512,
            ),
        )

        generated_text = response.text

        if not generated_text or not generated_text.strip():
            raise RuntimeError("Gemini returned an empty response")

        return generated_text.strip()

    async def close(self) -> None:
        await self.client.aclose()
