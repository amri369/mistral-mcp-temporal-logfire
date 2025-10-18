from dotenv import load_dotenv

load_dotenv()

from deepeval.models import LiteLLMModel
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval import evaluate
from config import settings


def main():
    # Use mistral-large-latest with JSON mode enabled
    mistral_large = LiteLLMModel(
        model="mistral/mistral-large-latest",
        api_key=settings.mistral_api_key,
        temperature=0,  # Zero temp for deterministic output
        generation_kwargs={
            "max_tokens": 2000,  # Increased for complex JSON
            "response_format": {"type": "json_object"},  # Force JSON mode
        }
    )

    # Use simpler metrics that require less complex JSON
    answer_relevancy = AnswerRelevancyMetric(
        threshold=0.7,
        model=mistral_large,
        include_reason=False,  # Less complex JSON without reasons
        async_mode=False  # Disable async for more stable responses
    )

    test_cases = [
        LLMTestCase(
            input="What is the capital of France?",
            actual_output="Paris is the capital of France",
            expected_output="Paris"
        ),
    ]

    print("\n🚀 Running DeepEval with Mistral Large (JSON mode)...\n")
    results = evaluate(test_cases, [answer_relevancy])
    print(f"results: {results}")


if __name__ == "__main__":
    main()