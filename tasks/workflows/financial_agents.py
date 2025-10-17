import asyncio

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from tasks.utils.common import ACTIVITY_OPTS
    from tasks.activities.financial_agents import (
        create_agent_activity,
        start_conversation_activity,
        run_activity,
    )
    from agents.agents_params import AGENTS_PARAMS
    from models.agents import AgentRunInputModel, QueryModel
    from models.structured_output import (
        AnalysisSummary,
        FinancialSearchPlan,
        FinancialReportData,
        VerificationResult,
        FinancialReportWorkflowOutput,
        WriterAgentInputModel,
        format_search_results,
    )
    from logger import get_logger
    logger = get_logger(__name__)

@workflow.defn
class FinancialResearchWorkflow:
    def __init__(self):
        self.final_report = None

    @workflow.run
    async def run(self, query: QueryModel) -> FinancialReportWorkflowOutput:
        query = query.query
        logger.info("Create agents started")
        agents = await asyncio.gather(
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["ANALYST"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["FUNDAMENTALS"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["PLANNER"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["RISK"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["SEARCH"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["VERIFIER"], **ACTIVITY_OPTS),
            workflow.execute_activity(create_agent_activity, AGENTS_PARAMS["WRITER"], **ACTIVITY_OPTS),
        )

        analyst_agent, fundamental_agent, planner_agent, risk_agent, search_agent, verifier_agent, writer_agent = agents
        logger.info("Create agents completed")

        logger.info("Analyst agent started")
        price_result = await workflow.execute_activity(
            run_activity,
            AgentRunInputModel(
                id=analyst_agent.id,
                inputs=query,
                response_format=AGENTS_PARAMS["ANALYST"].response_format,
                mcp_server_url=AGENTS_PARAMS["ANALYST"].mcp_server_url,
            ),
            **ACTIVITY_OPTS,
        )
        price_result = AnalysisSummary(**price_result)

        logger.info("Planner agent started")
        search_plan = await workflow.execute_activity(
            start_conversation_activity,
            AgentRunInputModel(
                id=planner_agent.id,
                inputs=query,
                response_format=AGENTS_PARAMS["PLANNER"].response_format,
                mcp_server_url=AGENTS_PARAMS["PLANNER"].mcp_server_url,
            ),
            **ACTIVITY_OPTS,
        )

        search_plan = FinancialSearchPlan(**search_plan)
        logger.info("Planner agent completed")

        logger.info("Search agents started")
        search_activities = []
        for search_item in search_plan.searches:
            payload = AgentRunInputModel(
                id=search_agent.id,
                inputs=search_item.query,
                response_format=AGENTS_PARAMS["SEARCH"].response_format,
                mcp_server_url=AGENTS_PARAMS["SEARCH"].mcp_server_url,
            )
            search_activities.append(
                workflow.execute_activity(
                    start_conversation_activity,
                    payload,
                    **ACTIVITY_OPTS,
                )
            )

        search_results = await asyncio.gather(*search_activities)
        search_results = [AnalysisSummary(**result) for result in search_results]
        search_results = format_search_results(search_results)
        logger.info("Search agents completed")

        logger.info("Risk and fundamental agents started")
        risk_handle = workflow.start_activity(
            start_conversation_activity,
            AgentRunInputModel(
                id=risk_agent.id,
                inputs=search_results,
                response_format=AGENTS_PARAMS["RISK"].response_format,
                mcp_server_url=AGENTS_PARAMS["RISK"].mcp_server_url,
            ),
            **ACTIVITY_OPTS,
        )
        fundamentals_handle = workflow.start_activity(
            start_conversation_activity,
            AgentRunInputModel(
                id=fundamental_agent.id,
                inputs=search_results,
                response_format=AGENTS_PARAMS["FUNDAMENTALS"].response_format,
                mcp_server_url=AGENTS_PARAMS["FUNDAMENTALS"].mcp_server_url,
            ),
            **ACTIVITY_OPTS,
        )
        risk_result, fundamentals_result = await asyncio.gather(
            *[risk_handle,
            fundamentals_handle]
        )
        risk_result = AnalysisSummary(**risk_result)
        fundamentals_result = AnalysisSummary(**fundamentals_result)
        logger.info("Risk and fundamental agents completed")

        logger.info("Writer agents started")
        writer_input = WriterAgentInputModel(
            fundamentals_analysis=fundamentals_result,
            prices_analysis=price_result,
            risk_analysis=risk_result,
        )
        report = await workflow.execute_activity(
            start_conversation_activity,
            AgentRunInputModel(
                id=writer_agent.id,
                inputs=writer_input.model_dump_json(),
                response_format=AGENTS_PARAMS["WRITER"].response_format,
                mcp_server_url=AGENTS_PARAMS["WRITER"].mcp_server_url,
            ),
            **ACTIVITY_OPTS,
        )
        report = FinancialReportData(**report)
        logger.info("Writer agent completed")

        logger.info("Verifier agents started")
        verification = await workflow.execute_activity(
            start_conversation_activity,
            AgentRunInputModel(
                id=verifier_agent.id,
                inputs=str(report),
                response_format=AGENTS_PARAMS["VERIFIER"].response_format,
                mcp_server_url=AGENTS_PARAMS["VERIFIER"].mcp_server_url,
            ),
            **ACTIVITY_OPTS,
        )
        verification = VerificationResult(**verification)
        logger.info("Verifier agent completed")

        print("\n\n=====REPORT=====\n\n")
        print(f"Report:\n{report.markdown_report}")
        print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
        print("\n".join(report.follow_up_questions))
        print("\n\n=====PRICES ANALYSIS=====\n\n")
        print(prices_analysis.model_dump_json())
        print("\n\n=====VERIFICATION=====\n\n")
        print(verification.issues)

        self.final_report = FinancialReportWorkflowOutput(
            search_plan=search_plan,
            report=report,
            verification=verification,
            risk_analysis=risk_result,
            fundamentals_analysis=fundamentals_result,
            price_analysis=prices_analysis,
        )

        return self.final_report

    @workflow.query
    def get_final_report(self):
        return self.final_report
