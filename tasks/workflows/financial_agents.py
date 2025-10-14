from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from tasks.utils.common import ACTIVITY_OPTS
    from tasks.activities.financial_agents import (
        create_agent_activity,
        update_agent_activity,
        start_conversation_activity
    )
    from agents.agents_params import AGENTS_PARAMS
    from models.agents import MistralAgentUpdateModel, AgentRunInputModel
    from models.structured_output import FinancialReportWorkflowOutput

@workflow.defn
class FinancialResearchWorkflow:
    @workflow.run
    async def run(self, query: str):
        fundamental_agent = await workflow.execute_activity(
            create_agent_activity,
            AGENTS_PARAMS["FUNDAMENTALS"],
            **ACTIVITY_OPTS
        )

        planner_agent = await workflow.execute_activity(
            create_agent_activity,
            AGENTS_PARAMS["PLANNER"],
            **ACTIVITY_OPTS
        )

        risk_agent = await workflow.execute_activity(
            create_agent_activity,
            AGENTS_PARAMS["RISK"],
            **ACTIVITY_OPTS
        )

        search_agent = await workflow.execute_activity(
            create_agent_activity,
            AGENTS_PARAMS["SEARCH"],
            **ACTIVITY_OPTS
        )

        verifier_agent = await workflow.execute_activity(
            create_agent_activity,
            AGENTS_PARAMS["VERIFIER"],
            **ACTIVITY_OPTS
        )

        writer_agent = await workflow.execute_activity(
            create_agent_activity,
            AGENTS_PARAMS["WRITER"],
            **ACTIVITY_OPTS
        )

        await workflow.execute_activity(
            update_agent_activity,
            MistralAgentUpdateModel(
                id=writer_agent.id,
                handoffs=[fundamental_agent.id, risk_agent.id]
            ),
            **ACTIVITY_OPTS
        )

        search_plan = await workflow.execute_activity(
            start_conversation_activity,
            AgentRunInputModel(
                id=planner_agent.id,
                inputs=query,
                response_format=AGENTS_PARAMS["PLANNER"].response_format
            ),
            **ACTIVITY_OPTS,
        )

        return search_plan
