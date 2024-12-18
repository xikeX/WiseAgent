"""
Author: Huang Weitao
Date: 2024-12-17 13:06:25
LastEditors: Huang Weitao
LastEditTime: 2024-12-17 13:06:54
Description: 
"""
from wiseagent.core.agent import Agent

bob = Agent.from_default(name="Bob")  # create an agent called Bob
bob.life()
while True:
    message = input("User Massage:")
    bob.input(message)
