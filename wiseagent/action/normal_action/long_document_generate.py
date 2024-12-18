"""
Author: Huang Weitao
Date: 2024-11-03 15:40:54
LastEditors: Huang Weitao
LastEditTime: 2024-11-08 16:29:24
Description: 
"""
import json
import queue
import re
from functools import partial
from typing import Any, List

from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction, BaseActionData
from wiseagent.common.protocol_message import (
    STREAM_END_FLAG,
    CommunicationMessage,
    FileUploadMessage,
    Message,
)
from wiseagent.common.singleton import singleton
from wiseagent.common.utils import repair_path, write_file

GENERATE_LONG_DOCUMENT_PROMPT = """
You are a book writing expert, you need to complete a book.

## Topic
{topic}

## Topic Description
{topic_description}

## Written Content
{content}

## Article Outline
{outline}

## Instruction
You are a book writing expert, you need to complete a book. Now you need to complete
{chapter_title}
this section
The specific content can refer to several small points, as follows:
{chapter_description}.
You are a book writing expert, you need to complete a book. Now you need to complete
# Writing requirements:
1. You need to write in the style of writing books, that is, the requirement is to conform to natural language description, write each section in the form of total points, as far as possible not to appear additional section numbering.
2. You need to give a vivid and vivid introduction as much as possible, and give specific examples as much as possible, as far as possible not to appear too abstract concepts.
3. You use paragraphs to describe as much as possible, do not use too many inline formulas.
4. Do not use special formats, such as bold, points, columns, etc.
5. Do not use descriptions such as first, second, last, in conclusion, etc. that do not conform to the writing style of textbooks.
6. Do not appear words such as in addition, in conclusion, in general, etc.
7. Do not write capter, section, subsection, etc. that do not conform to the writing style of textbooks.
8. The Specific content must only contain the content of the section, and must not contain the title of the section.
9. Do not repeate the capter title.
10. The capter must be concise and clear, and the content must be related to the chapter title.
Please generate the content of this section.
First, you need to think about what content this section needs to write, and then write this section
The specific content to be written is output in follwing format.
<content>
Specific content
</content>
Output in the format.
The book must in the language of {language}

"""

GENERATE_OUTLINE_PROMPT = """
You are a book writing expert, you need to complete a book, now you need to complete an outline for the book. Base on the topic and description, you need to generate the outline of the book.

## Example
<outline>
<chapter level="1">Overview of intelligent agents</chapter>
<chapter level="2">Definition of intelligent agents</chapter>
<chapter level="3">
    <chapter_name>Broad definition of intelligent agents (philosophical system)</chapter_name>
    <chapter_description>Intelligent agents are entities that can perceive their environment and take actions to achieve goals.</chapter_description>
</chapter>
<chapter level="3">
    <chapter_name>Narrow definition of intelligent agents (computer system)</chapter_name>
    <chapter_description>Intelligent agents are computer programs that can perceive their environment and take actions to achieve goals.</chapter_description>
</chapter>
<chapter level="1">Classification of intelligent agents</chapter>
<chapter level="2">Classification based on the level of intelligence</chapter>
<chapter level="3">
    <chapter_name>Intelligent agents</chapter_name>
    <chapter_description>Intelligent agents are entities that can perceive their environment and take actions to achieve goals.</chapter_description>
</chapter>
<chapter level="3">
    <chapter_name>Limited intelligence agents</chapter_name>
    <chapter_description>Intelligent agents are entities that can perceive their environment and take actions to achieve goals.</chapter_description>
</chapter>
<chapter level="3">
    <chapter_name>Model-based reflex agents</chapter_name>
    <chapter_description>Intelligent agents are entities that can perceive their environment and take actions to achieve goals.</chapter_description>
</chapter>
<chapter level="2">Classification based on the level of autonomy</chapter>
<chapter level="3">
    <chapter_name>Autonomous agents</chapter_name>
    <chapter_description>Intelligent agents are entities that can perceive their environment and take actions to achieve goals.</chapter_description>
</chapter>
<chapter level="3">
    <chapter_name>Semi-autonomous agents</chapter_name>
    <chapter_description>Intelligent agents are entities that can perceive their environment and take actions to achieve goals.</chapter_description>
</chapter>
</outline>

## Topic
{topic}

## Description
{description}


## instruction
you need to generate the outline of the book, pay attention to the following points:
1. The outline should be in the form of a tree structure, with each level representing a different level of section.
2. The outline should be comprehensive and detailed, covering all the main points of the book.
3. You must take close attention to the logical relationship between the sections, and ensure that the outline is easy to understand and follow.
4. You must confirm there is one or more chapter belong to the chapter level 1 and 2. and level 3 is the smallest level.
5. For each chapter at level 3, there should be a concise description
6. The outline should be in the language of {language}
output in the xml like:

<outline>
<chapter level="1">level 1</chapter>
<chapter level="2">level 2</chapter>
<chapter level="3">
    <chapter_name>level 3</chapter_name>
    <chapter_description>level 3 description</chapter_description>
</chapter>
...
</outline>


"""


class chapterTreeNode:
    is_title: bool = False
    content: str = ""
    description: str = ""
    children: List[Any] = []


class LongDocumentGenerateActionData(BaseActionData):
    chapter_list: List[str] = []


@singleton
class LongDocumentGenerateAction(BaseAction):
    """Generate long document from a list of chapters"""

    action_description: str = "Generate long document from a list of chapters"

    def init_agent(self, agent_data):
        agent_data.set_action_data(self.action_name, LongDocumentGenerateActionData())

    @action()
    def create_long_document(self, topic, topic_description, outline, language="chinese", save_path="result.md"):
        """Generate long document from a list of chapters
        Args:
            topic (str): The topic of the document
            topic_description (str): The description of the document
            outline (list): The outline of the document
            language (str): The language of the document
            save_path (str): The path to save the document, default is "result.md"
        Example:
            # The id and father_id is not necessary, just for the convenience of the outline.
            >>> outline = [
                {"level":1, "chapter_title":"the first chapter", description:"the first chapter description"},
                {"level":2, "chapter_title":"the first section", description:"the first section description"},
                {"level":3, "chapter_title":"the first subsection", description:"the first subsection description"},
                {"level":2, "chapter_title":"the second section", description:"the second section description"},
                {"level":3, "chapter_title":"the second subsection", description:"the second subsection description"},
            ]
            >>> create_long_document("topic", "description", outline, language="chinese", save_path="{book_name}.md")
        """
        if isinstance(outline, str):
            outline = json.loads(outline)
        level_list, pre_level = [0, 0, 0], ["", "", ""]
        format_outline = topic + "\n"
        # Prepare and format the outline
        for item in outline:
            level = item.get("level", None)
            title = item.get("chapter_title", None)
            level_list[level - 1] += 1
            pre_level[level - 1] = ".".join([str(i) for i in pre_level]) + " " + title
            item["location"] = "\n".join(pre_level[:level]) + " " + title
            item["full_chapter_title"] = ".".join([str(i) for i in pre_level]) + " " + title
            format_outline += "#" * level + " " + item["chapter_title"] + "\n"
        # Generate the document
        content = topic + "\n"
        stream_message = FileUploadMessage(
            file_name=str(repair_path(save_path)), is_stream=True, stream_queue=queue.Queue()
        ).send_message()
        for item in outline:
            level = item.get("level", None)
            content += "#" * level + " " + item["chapter_title"] + "\n"
            stream_message.stream_queue.put("\n" + "#" * level + " " + item["chapter_title"] + "\n")
            if level != 3:
                continue
            prompt = GENERATE_LONG_DOCUMENT_PROMPT.format(
                topic=topic,
                topic_description=topic_description,
                content=content,
                outline=format_outline,
                chapter_title=item["location"],
                chapter_description=item.get("description", None),
                language=language,
            )

            # Call the LLM to generate the chapter content
            response = self.llm_ask(
                prompt, handle_stream_function=partial(self.parse_document_stream, upload_mesage=stream_message)
            )
            content += f"{self.parse_document(response).strip()}\n"
        stream_message.stream_queue.put(STREAM_END_FLAG)
        if not content:
            return "No content generated"
        write_file(save_path, content)
        # FileUploadMessage(file_name=save_path).send_message()
        return f"document generated successfully. The path is {save_path}"

    def parse_document_stream(self, rsp_message, upload_mesage: Message):
        if rsp_message == STREAM_END_FLAG:
            return ""
        special_tag = ["<content>", "</content>"]
        if any(tag.startswith(rsp_message) for tag in special_tag):
            if "<content>" in rsp_message:
                upload_mesage.appendix["start_receive_content"] = True
                return ""
            elif "</content>" in rsp_message:
                upload_mesage.appendix["start_receive_content"] = False
                return ""
            return rsp_message
        else:
            if upload_mesage.appendix.get("start_receive_content", None):
                upload_mesage.stream_queue.put(rsp_message)
            return ""

    def parse_document(self, respond):
        pattern = "<content>\s*(.*?)\s*</content>"
        matches = re.findall(pattern, respond, re.DOTALL)
        if len(matches) == 0:
            return respond
        return matches[0]

    @action()
    def generate_outline(self, topic, description=None, language="chinese"):
        """Generate outline from topic and description
        Args:
            topic (str): topic of the document
            description (str): description of the document
            language (str): language of the document
        """
        generate_outline_prompt = GENERATE_OUTLINE_PROMPT.format(
            topic=topic, description=description, language=language
        )
        steam_mesage = CommunicationMessage(is_stream=True, stream_queue=queue.Queue()).send_message()

        respond = self.llm_ask(
            generate_outline_prompt,
            handle_stream_function=partial(self.parse_outline_stream, upload_mesage=steam_mesage),
        )
        outline = self.parse_outline(respond)
        return f"generate_outline executed successfully.\nThe outline is:\n{outline}"

    def parse_outline_stream(self, rsp_message, upload_mesage: Message):
        """Parse outline stream"""
        if "start_flag" not in upload_mesage.appendix:
            upload_mesage.appendix["start_flag"] = True
            upload_mesage.appendix["level_list"] = [0, 0, 0]
        if rsp_message == STREAM_END_FLAG:
            upload_mesage.stream_queue.put(STREAM_END_FLAG)
            return ""
        pattern = r'<chapter level="(\d+)">(.*?)</chapter>'
        chapter_pattern = re.compile(pattern, re.DOTALL)
        matches = chapter_pattern.findall(rsp_message)
        if not matches:
            return rsp_message
        outline_text = ""
        for level, content in matches:
            level = int(level) - 1
            upload_mesage.appendix["level_list"][level] += 1
            pre_level = ".".join([str(i) for i in upload_mesage.appendix["level_list"][: level + 1]]) + "."
            if level == 0 or level == 1:
                upload_mesage.appendix["level_list"][level + 1] = 0
                outline_text += f"{pre_level} {content}\n"
            elif level == 2:
                chapter_name = re.search(r"<chapter_name>(.*?)</chapter_name>", content, re.DOTALL).group(1)
                chapter_description = re.search(
                    r"<chapter_description>(.*?)</chapter_description>", content, re.DOTALL
                ).group(1)
                outline_text += f"{pre_level} {chapter_name}\n"
                outline_text += f"    {chapter_description}\n"
        outline_text += "\n"
        upload_mesage.stream_queue.put(outline_text)
        return ""

    def parse_outline(self, xml_outline):
        """Parse outline from xml
        Args:
            xml (str): xml string
        """
        pattern = r'<chapter level="(\d+)">(.*?)</chapter>'
        chapter_pattern = re.compile(pattern, re.DOTALL)
        matches = chapter_pattern.findall(xml_outline)
        outline_text = ""
        level_list = [0, 0, 0]
        for level, content in matches:
            level = int(level) - 1
            level_list[level] += 1
            pre_level = ".".join([str(i) for i in level_list[: level + 1]]) + "."
            if level == 0 or level == 1:
                level_list[level + 1] = 0
                outline_text += f"{pre_level} {content}\n"
            elif level == 2:
                chapter_name = re.search(r"<chapter_name>(.*?)</chapter_name>", content, re.DOTALL).group(1)
                chapter_description = re.search(
                    r"<chapter_description>(.*?)</chapter_description>", content, re.DOTALL
                ).group(1)
                outline_text += f"{pre_level} {chapter_name}\n"
                outline_text += f"    {chapter_description}\n"
        print(outline_text)
        return outline_text


def get_action():
    return LongDocumentGenerateAction()
