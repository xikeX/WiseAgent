from pydantic import BaseModel


class Message(BaseModel):
    send_from:str
    send_to: str
    cause_by: str
    content: str
    time_stamp: str
    type: str
    appendix: dict = {}
    
    def add_image(self, image):
        # TODO: if image is a path, read it
        self.appendix['image'] = image
        
    def add_audio(self, audio):
        # TODO: if audio is a path, read it
        self.appendix['audio'] = audio
        
class AIMessage(Message):
    type = 'AI'
    # TODO: add more fields
    
    
class UserMessage(Message):
    type = 'USER'
    # TODO: add more fields