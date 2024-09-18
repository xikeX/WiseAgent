'''
Author: Huang Weitao
Date: 2024-09-17 14:24:14
LastEditors: Huang Weitao
LastEditTime: 2024-09-18 23:53:08
Description: 
'''
import importlib

import queue
import threading
from typing import ClassVar, List
from pydantic import BaseModel
from wiseagent.common.message import ReceiveMessage
from wiseagent.core.agent_core import AgentCore,get_agent_core
from wiseagent.receiver.perceptron import BasePerceptron
from wiseagent.config import GLOBAL_CONFIG,logger
from wiseagent.agent_data import AgentData

class BaseReceiver(BaseModel):
    """Base class for receivers."""
    class Config:
        arbitrary_types_allowed = True
        ignored_types = (queue.Queue,)
    # All the perceptron model. For difference agent, will use different perceptron model according to the Agent Data
    perceptron_list:list[BasePerceptron]=[]
    # cache
    message_queue = queue.Queue()
    receive_thread:threading.Thread = None
    def __init__(self):
        super().__init__()
        # init the perceptron model use global config
        for perceptron_model_path in GLOBAL_CONFIG.perceptron_model_path:
            # register the perecptron model
            import_module = importlib.import_module(perceptron_model_path)
            if not hasattr(import_module, 'get_perceptron') and not callable(getattr(import_module, 'get_perceptron')):
                raise Exception(f"Perceptron model {perceptron_model_path} does not have a get_perceptron method")
            perceptron = import_module.get_perceptron()
            if perceptron not in self.perceptron_list:
                self.perceptron_list.append(perceptron)

    def add_message(self,message:list[ReceiveMessage]):
        if not isinstance(message,ReceiveMessage):
            message = [message]
        for m in message:
            if not isinstance(m,ReceiveMessage):
                logger.info(f"Message {m} is not a ReceiveMessage. andd will be ignored")
                continue
            self.message_queue.put(m)
    
    def _receive(self,agent_core:"AgentCore"):
        """Receive messages from the message queue and process them.
        Args:
            agent_core (AgentCore): The agent core object.
        """
        while agent_core.is_running:
            # get the message from the queue, if the queue is empty, the get() method will block until a message is available
            message = None
            try:
                message = self.message_queue.get(timeout=1)
            except queue.Empty:
                continue
            receive_agent = None
            for agent in agent_core.agent_list.index():
                if message.send_to == agent.name or message.send_to == "all":
                    receive_agent = agent
                    break
            if receive_agent:
                self.handle_message(agent,message)
            else:
                logger.warning(f"Message {message} is not sent to any agent")
                        
    def handle_message(self,agentdata:AgentData,message:ReceiveMessage):
        for perceptron in self.perceptron_list:
            if perceptron.name in agentdata.receive_ability and\
                any([key_word == message.receive_type for key_word in perceptron.key_word_list]):
                perceptron.handle_message(agentdata,message)

    def run_receive_thread(self)->bool:
        # check if the thread is running
        if self.receive_thread is not None and self.receive_thread.is_alive():
            return True
        # create or continue a thread to receive message
        try:
            self.receive_thread = self.receive_thread|threading.Thread(target=self._receive, args=(get_agent_core(),))
            self.receive_thread.start()
            return True
        except Exception as e:
            print(e)
            return False
        
        
def register(agent_core:"AgentCore"):
    """Register the receiver to the agent core."""
    agent_core.receiver = BaseReceiver()
    agent_core.start_function_list.append(agent_core.receiver.run_receive)
        