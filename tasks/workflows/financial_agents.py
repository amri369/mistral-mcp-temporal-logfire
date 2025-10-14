import asyncio

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
    from models.structured_output import (
        FinancialSearchPlan,
        FinancialReportWorkflowOutput,
    )

@workflow.defn
class FinancialResearchWorkflow:
    @workflow.run
    async def run(self, query: str):
        agents = await asyncio.gather(
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["FUNDAMENTALS"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["PLANNER"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["RISK"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["SEARCH"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["VERIFIER"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["WRITER"], **ACTIVITY_OPTS),
        )

        fundamental_agent, planner_agent, risk_agent, search_agent, verifier_agent, writer_agent = agents

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

        search_plan = FinancialSearchPlan(**search_plan)

        search_activities = []
        for search_item in search_plan.searches:
            payload = AgentRunInputModel(
                id=search_agent.id,
                inputs=search_item.query,
                response_format=AGENTS_PARAMS["SEARCH"].response_format
            )
            search_activities.append(
                workflow.execute_activity(
                    start_conversation_activity,
                    payload,
                    **ACTIVITY_OPTS,
                )
            )

        search_results = await asyncio.gather(*search_activities)
        print(search_results)

        return search_results
