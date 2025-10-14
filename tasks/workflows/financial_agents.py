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
        FinancialReportData,
        VerificationResult,
        FinancialReportWorkflowOutput,
    )
    from logger import get_logger
    logger = get_logger(__name__)

@workflow.defn
class FinancialResearchWorkflow:
    @workflow.run
    async def run(self, query: str):
        logger.info("Initialize agents started")
        agents = await asyncio.gather(
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["FUNDAMENTALS"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["PLANNER"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["RISK"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["SEARCH"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["VERIFIER"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["WRITER"], **ACTIVITY_OPTS),
        )

        fundamental_agent, planner_agent, risk_agent, search_agent, verifier_agent, writer_agent = agents
        logger.info("Initialize agents finished")

        await workflow.execute_activity(
            update_agent_activity,
            MistralAgentUpdateModel(
                id=writer_agent.id,
                handoffs=[fundamental_agent.id, risk_agent.id]
            ),
            **ACTIVITY_OPTS
        )

        logger.info("Planner agent started")
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
        logger.info("Planner agent finished")

        logger.info("Search agents started")
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
        logger.info("Search agents finished")

        logger.info("Writer agents started")
        report = await workflow.execute_activity(
            start_conversation_activity,
            AgentRunInputModel(
                id=writer_agent.id,
                inputs=str(search_results),
                response_format=AGENTS_PARAMS["WRITER"].response_format
            ),
            **ACTIVITY_OPTS,
        )
        report = FinancialReportData(**report)
        logger.info("Writer agent finished")

        logger.info("Verifier agents started")
        verification = await workflow.execute_activity(
            start_conversation_activity,
            AgentRunInputModel(
                id=verifier_agent.id,
                inputs=str(report),
                response_format=AGENTS_PARAMS["VERIFIER"].response_format
            ),
            **ACTIVITY_OPTS,
        )
        verification = VerificationResult(**verification)
        logger.info("Verifier agent finished")

        print("\n\n=====REPORT=====\n\n")
        print(f"Report:\n{report.markdown_report}")
        print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
        print("\n".join(report.follow_up_questions))
        print("\n\n=====VERIFICATION=====\n\n")
        print(verification.issues)

        return FinancialReportWorkflowOutput(
            search_plan=search_plan,
            report=report,
            verification=verification,
        )
