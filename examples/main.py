import asyncio

from temporalio.client import Client

from config import settings
from tasks.workflows.financial_agents import (
    FinancialResearchWorkflow,
)
from logger import get_logger
logger = get_logger(__name__)

async def main():
    # Get the query from user input
    query = input("Enter a financial research query: ")
    if not query.strip():
        query = "Write up an analysis of Apple Inc.'s most recent quarter."
        logger.info(f"Using default query: {query}")

    client = await Client.connect(
        settings.temporal_server_url,
    )

    logger.info(f"Starting financial research for: {query}")
    logger.info("This may take several minutes to complete...\n")

    result = await client.execute_workflow(
        FinancialResearchWorkflow.run,
        args=[query],
        id=f"financial-research-{hash(query)}",
        task_queue="financial-research-task-queue",
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())