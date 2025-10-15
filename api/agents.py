import asyncio
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status

from models.agents import QueryModel, WorkflowIDModel
from models.structured_output import FinancialReportWorkflowOutput
from tasks.workflows.financial_agents import FinancialResearchWorkflow
from config import settings

router = APIRouter()

@router.post(
    "/start-agent-workflow",
    response_model=WorkflowIDModel,
)
async def start_agent_workflow(
        params: QueryModel,
        request: Request
):
    try:
        client = request.app.state.temporal_client
        workflow_id = f"financial-research-workflow-{uuid4()}"
        await client.start_workflow(
            FinancialResearchWorkflow.run,
            params,
            id=workflow_id,
            task_queue=settings.task_queue_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return WorkflowIDModel(workflow_id=workflow_id)

@router.get(
    "/get-agent-workflow-result",
    response_model=FinancialReportWorkflowOutput | None,
)
async def get_agent_workflow_result(
        workflow_id: str,
        request: Request
):
    try:
        client = request.app.state.temporal_client
        handle = client.get_workflow_handle(workflow_id)
        response = await asyncio.wait_for(handle.query("get_final_report"), timeout=10)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
