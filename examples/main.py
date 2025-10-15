import asyncio

from tasks.utils.common import get_temporal_client
from tasks.workflows.financial_agents import FinancialResearchWorkflow
from models.agents import QueryModel
from config import settings

from logger import get_logger
logger = get_logger(__name__)

async def main():
    # Get the query from user input
    query = input("Enter a financial research query: ")
    if not query.strip():
        query = "Write up an analysis of Apple Inc.'s most recent quarter."
        logger.info(f"Using default query: {query}")

    client = await get_temporal_client()

    logger.info(f"Starting financial research for: {query}")
    logger.info("This may take several minutes to complete...\n")

    result = await client.execute_workflow(
        FinancialResearchWorkflow.run,
        args=[QueryModel(query=query)],
        id=f"financial-research-{hash(query)}",
        task_queue=settings.task_queue_url,
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())