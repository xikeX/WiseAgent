from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.message import ReportMessage
from wiseagent.monitor.reporter.base_reporter import BaseReporter


class TextReporter(BaseReporter):
    name = "text_reporter"
    map_key_word = ["text"]
    def report(self, agentdata: AgentData, report_message:ReportMessage)-> bool:
        """ the single agent report will report the message to the website.
        Args:
            agentdata (AgentData): the agent data to report
            report_type (str): the type of report
            report_data (dict): the data to report
        """
        # TODO: implement the report function
        print("Reporting to website")
        print(f"{report_message.report_type}: {report_message.report_data}")
        return True