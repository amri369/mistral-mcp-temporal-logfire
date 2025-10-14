from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from tasks.utils.common import ACTIVITY_OPTS
    from tasks.activities.financial_agents import create_agent_activity, update_agent_activity
    from agents.agents_params import AgentParams
    from models.agents import FinancialAgentsIDsModel, MistralAgentUpdateModel

@workflow.defn
class CreateAgentsWorkflow:
    @workflow.run
    async def run(self) -> FinancialAgentsIDsModel:
        fundamental_agent = await workflow.execute_activity(
            create_agent_activity,
            AgentParams.FUNDAMENTALS,
            **ACTIVITY_OPTS
        )

        planner_agent = await workflow.execute_activity(
            create_agent_activity,
            AgentParams.PLANNER,
            **ACTIVITY_OPTS
        )

        risk_agent = await workflow.execute_activity(
            create_agent_activity,
            AgentParams.RISK,
            **ACTIVITY_OPTS
        )

        search_agent = await workflow.execute_activity(
            create_agent_activity,
            AgentParams.SEARCH,
            **ACTIVITY_OPTS
        )

        verifier_agent = await workflow.execute_activity(
            create_agent_activity,
            AgentParams.VERIFIER,
            **ACTIVITY_OPTS
        )

        writer_agent = await workflow.execute_activity(
            create_agent_activity,
            AgentParams.WRITER,
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

        return FinancialAgentsIDsModel(
            planner_agent_id=planner_agent.id,
            search_agent_id=search_agent.id,
            writer_agent_id=writer_agent.id,
            verifier_agent_id=verifier_agent.id,
        )