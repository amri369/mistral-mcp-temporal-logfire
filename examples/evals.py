from dotenv import load_dotenv
from deepeval.models import LiteLLMModel
from deepeval.metrics import FaithfulnessMetric, BiasMetric
from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from config import settings

load_dotenv()


def load_report(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_web_search_results(file_path: str) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
    return chunks


def main():
    mistral_large = LiteLLMModel(
        model="mistral/mistral-large-latest",
        api_key=settings.mistral_api_key,
        temperature=0,
        generation_kwargs={
            "max_tokens": 2000,
            "response_format": {"type": "json_object"},
        }
    )

    report_content = load_report("examples/report.md")
    retrieval_context = load_web_search_results("examples/web_search_results.txt")

    faithfulness = FaithfulnessMetric(
        threshold=0.7,
        model=mistral_large,
        include_reason=True,
        async_mode=False
    )

    bias = BiasMetric(
        threshold=0.5,
        model=mistral_large,
        include_reason=True,
        async_mode=False
    )

    test_cases = [
        LLMTestCase(
            input="Analyze Palantir Technologies Inc. (PLTR) as an investment opportunity, including financial performance, stock analysis, risks, and strategic initiatives.",
            actual_output=report_content,
            retrieval_context=retrieval_context
        ),
    ]

    print("Running DeepEval: Faithfulness & Bias Metrics")
    print(f"📄 Report: report.md")
    print(f"🔍 Context: web_search_results.txt ({len(retrieval_context)} chunks)\n")

    results = evaluate(
        test_cases,
        [faithfulness, bias]
    )

    print(f"\n✅ Evaluation Complete!")
    print(f"Results: {results}")

if __name__ == "__main__":
    main()