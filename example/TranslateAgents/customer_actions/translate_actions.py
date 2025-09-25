
import json
import re
from wiseagent.action.base_action import BaseAction, BaseActionData
from wiseagent.action.action_decorator import action
from wiseagent.common.protocol_message import CommunicationMessage
from wiseagent.common.logs import logger
from wiseagent.common.singleton import singleton
from wiseagent.common.utils import read_file
class TranslateActionData(BaseActionData):
    """
    translate_word_dictionary
    """
    translate_word_dictionary:dict = {}

ADDTIONAL_PROMPT = """
# Original Text
{original_text}

## Word Dictionary
{translate_word_dictionary}

## Instruction
Your task is to augment the word translation dictionary by adding new entries when necessary. The entries you add must follow the format and should be limited to names, locations, or domain-specific terminology. you output should be in the following format:
{{
"word_1": "translation_1",
"word_2": "translation_2",
}}

NOTE: 
1. If you don't need to add any new entries, just output "{{}}".
2. Do not repeat existing entries.
3. you original language is {original_language} and target language is {target_language}
"""
TRANSLATION_PROMPT = """
# Original Text
{original_text}

# Word Dictionary
{translate_word_dictionary}

## Instruction
Your task is to translate the original text to {target_language} language. 
NOET: you must use the word translation dictionary to translate the text.

You output should be in the following format:
<translation>
translated text
</translation>
"""
REFINEMENT_PROMPT = """
# Original Text
{original_text}

# Word Dictionary
{translate_word_dictionary}

# Translated Text
{translated_text}

## Instruction
Your task is to refine the translated text to make it more fluent and accurate, and more suitable for the locals to understand.
And you must use the word translation dictionary to translate the text.

you output should be in the following format:
<refine_translation>
refined text
</refine_translation>
"""
@singleton
class TranslateAction(BaseAction):

    def init_agent(self, agent):
        self.set_action_data(agent, TranslateActionData())

    @action()
    def easy_translate(self,translated_text:str):
        """
        This function is used report the translate result.
        Args:
            translated_text(str): The translated text.
        """
        CommunicationMessage(
            content=translated_text,
            role="user",
        ).send_message()
        return "The translated text has been reported."

    @action()
    def hard_translate(self,file:str,original_language:str,target_language:str):
        """
        This function is used to translate the original text for difficult cases.
        Args:
            file(str): The file path of the original text.
            original_language(str): The original language.
            target_language(str): The target language.
        """
        original_text = read_file(file)
        translate_word_dictionary = self.get_action_data().translate_word_dictionary
        # 1. generate the translation word dictionary
        self.generate_translation_word_dictionary(original_text,original_language,target_language,translate_word_dictionary)
        # 2. translate the text utill accessed by the judgement
        max_tries = 0
        translated_text = ""
        while max_tries < 3:
            prompt = TRANSLATION_PROMPT.format(
                original_text=original_text,
                translate_word_dictionary=json.dumps(translate_word_dictionary,ensure_ascii=False),
                target_language=target_language,
            )
            respond = self.llm_ask(prompt,memory=[],system_prompt="")

            pattern = re.compile(r"<translation>(.*?)</translation>", re.DOTALL)
            match = pattern.search(respond)
            if match:
                translated_text = match.group(1)
                break
            else:
                max_tries += 1
        # 3. refine the text by the localization Specialist
        refine_prompt = REFINEMENT_PROMPT.format(
            original_text=original_text,
            translated_text=translated_text,
            translate_word_dictionary = translate_word_dictionary,
            target_language=target_language,
        )
        respond = self.llm_ask(refine_prompt)

        pattern = re.compile(r"<refine_translation>(.*?)</refine_translation>", re.DOTALL)
        match = pattern.search(respond)
        if match:
            translated_text = match.group(1)
        return "translation successfully."


    def generate_translation_word_dictionary(self,original_text:str,original_language:str,target_language:str,translate_word_dictionary:dict):
        """Get the translation word dictionary."""
        addtional_prompt = ADDTIONAL_PROMPT.format(
            original_text=original_text,
            translate_word_dictionary = json.dumps(translate_word_dictionary,ensure_ascii=False),
            original_language=original_language,
            target_language=target_language,    
        )
        try:
            respond = self.llm_ask(addtional_prompt,system_prompt="")
            new_dict = json.loads(respond)
            translate_word_dictionary.update(new_dict)
        except Exception as e:
            logger.debug(f"Error in generate_translation_word_dictionary: {e}.\nIgnore the translation word dictionary step.")

        return ""
    @action()
    def add_translation_word_dictionary(self,original_word:str,target_word:str):
        """Add a translation word dictionary.
        Args:
            original_word (str): The original word.
            target_word (str): The target word.
        """
        translate_word_dictionary = self.get_action_data().translate_word_dictionary
        translate_word_dictionary[original_word] = target_word
        return "Adding successful."

    def remove_translation_word_dictionary(self,original_word:str):
        """Remove a translation word dictionary.
        Args:
            original_word (str): The original_word word.
        """
        translate_word_dictionary = self.get_action_data().translate_word_dictionary
        if original_word in translate_word_dictionary:
            del translate_word_dictionary[original_word]
        return "Removing successful."
    