'''
Author: Huang Weitao
Date: 2024-09-17 14:23:28
LastEditors: Huang Weitao
LastEditTime: 2024-09-18 22:02:11
Description: 
'''

from typing import List
from typing_extensions import Unpack

from wiseagent.agent_data.base_agent_data import AgentData
from pydantic import BaseModel, ConfigDict
from wiseagent.monitor.reporter.base_reporter import BaseReporter


class Monitor(BaseModel):
    reportor: List[BaseReporter] = []
    # TODO: add more fields as needed
    reportor_cache = []
    
    def __init__(self):
        # init the perceptron model use global config
        for perceptron_model_path in GLOBAL_CONFIG.perceptron_model_path:
            # register the perecptron model
            import_module = importlib.import_module(perceptron_model_path)
            if not hasattr(import_module, 'register'):
                raise Exception(f"Perceptron model {perceptron_model_path} does not have a register method")
            perceptron = import_module.register(self)
            self.perceptron_list.append(perceptron)

    def _receive(self,agent_core:"AgentCore"):
        """Receive messages from the message queue and process them.
        Args:
            agent_core (AgentCore): The agent core object.
        """
        async def main():
            while agent_core.is_running:
                futures = []
                while len(self.message_queue) > 0:
                    message = self.message_queue.popleft()
                    found = False
                    for agent in agent_core.agent_list:
                        if message.send_to == agent.name or message.send_to == "all":
                            # process the message
                            futures.append(self.handle_message(agent,message))
                            found = True
                            break
                    if not found:
                        logger.warning(f"Message {message} is not sent to any agent")
                await asyncio.gather(*futures)
        asyncio.run(main())
            
                        
    def handle_message(self,agentdata:AgentData,message:Message):
        for perceptron in self.perceptron_list:
            if perceptron.name in agentdata.receive_ability and any([key_word == message.type for key_word in perceptron.key_word_list]):
                perceptron.handle_message(agentdata,message)

    def receive_thread(self,agent_core:"AgentData")->bool:
        # create a thread to receive message
        try:
            self.thread = threading.Thread(target=self._receive, args=(agent_core,))
            thread.start()
            return True
        except:
            return False
        
        
def register(agent_core:"AgentCore"):
    """Register the receiver to the agent core."""
    agent_core.receiver = BaseReceiver()
    agent_core.start_function_list.append(agent_core.receiver.receive_thread)
        