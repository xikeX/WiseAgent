'''
Author: Huang Weitao
Date: 2024-09-17 15:30:12
LastEditors: Huang Weitao
LastEditTime: 2024-09-18 23:14:09
Description: 
'''
from pydantic import BaseModel


class Message(BaseModel):
    send_from:str
    send_to: str
    cause_by: str
    content: str
    time_stamp: str
    message_type : str
    appendix: dict = {}
    
    def add_image(self, image):
        # TODO: if image is a path, read it
        self.appendix['image'] = image
        
    def add_audio(self, audio):
        # TODO: if audio is a path, read it
        self.appendix['audio'] = audio
        
class AIMessage(Message):
    message_type:str =  'AI'
    # TODO: add more fields
    
    
class UserMessage(Message):
    message_type:str =  'USER'
    # TODO: add more fields
    
class ReportMessage(Message):
    message_type:str =  'REPORT'
    report_type: str
    
    
class ReceiveMessage(Message):
    message_type:str =  'RECEIVE'
    receiver_type:str = 'text'
    # TODO: add more fields