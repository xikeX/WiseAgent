from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.monitor.reporter.base_reporter import BaseReporter


class SingleAgentReport(BaseReporter):
    name = "single_agent_report"
    
    def report(self, agentdata: AgentData, report_type, report_data)-> bool:
        """ the single agent report will report the message to the website.
        Args:
            agentdata (AgentData): the agent data to report
            report_type (str): the type of report
            report_data (dict): the data to report
        """
        # TODO: implement the report function
        print("Reporting to website")
        print(f"{report_type}: {report_data}")
        return True