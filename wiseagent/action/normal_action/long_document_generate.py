import re
from typing import Any, List

from click import prompt
from humanfriendly import parse_size

from wiseagent.action.action_annotation import action
from wiseagent.action.base import BaseAction, BaseActionData
from wiseagent.common.annotation import singleton
from wiseagent.common.file_io import write_file

GENERATE_LONG_DOCUMENT_PROMPT = """
You are a book writing expert, you need to complete a book.

## Topic
{topic}

## Description
{description}

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

    action_name: str = "LongDocumentGenerateAction"
    action_description: str = "Generate long document from a list of chapters"

    def init_agent(self, agent_data):
        agent_data.set_action_data(self.action_name, LongDocumentGenerateActionData())

    @action()
    def create_long_document(self, topic, description, outline, language="chinese", save_path="result.md"):
        """Generate long document from a list of chapters
        Args:
            topic (str): The topic of the document
            description (str): The description of the document
            outline (str): The outline of the document
            language (str): The language of the document
            save_path (str): The path to save the document, default is "result.md"
        """
        # Initialize the content and title list
        content = ""
        title = [""] * 3  # List to store titles for different levels
        # Split the outline into lines and remove empty lines
        outline_lines = [line for line in outline.split("\n") if line.strip()]
        content += f"# {topic}\n"

        # Iterate through each line in the outline
        for i, line in enumerate(outline_lines):
            # Determine the chapter level by counting the number of dots in the line
            chapter_level = line.count(".")

            # Handle different levels of headings
            if chapter_level == 0:
                continue
            elif chapter_level <= 3:  # Ensure we don't process more than 3 levels deep
                title[chapter_level - 1] = line
                # Add the appropriate number of '#' for the heading level
                content += f"{'#' * (chapter_level + 1)} {line}\n"

                # If it's a third-level heading, generate detailed content
                if chapter_level == 3:
                    # Construct the chapter title with all relevant levels
                    chapter_title = "\n".join(f"{'#' * (i + 2)} {t}" for i, t in enumerate(title) if t)

                    # Get the next line as the chapter description, if available
                    chapter_description = outline_lines[i + 1] if i + 1 < len(outline_lines) else ""

                    # Generate the prompt for the LLM
                    prompt = GENERATE_LONG_DOCUMENT_PROMPT.format(
                        topic=topic,
                        description=description,
                        content=content,
                        outline=outline,
                        chapter_title=chapter_title,
                        chapter_description=chapter_description,
                        language=language,
                    )

                    # Call the LLM to generate the chapter content
                    response = self.llm_ask(prompt)

                    # Parse the response and add it to the content
                    chapter_content = "\n".join(
                        line for line in self.parse_content(response).splitlines() if not line.startswith("#")
                    )
                    content += f"{chapter_content}\n"
        write_file(save_path, content)
        return content

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
        respond = self.llm_ask(generate_outline_prompt)
        outline = self.parse_outline(respond)
        return outline

    def parse_outline(self, xml_outline):
        """Parse outline from xml
        Args:
            xml (str): xml string
        """
        pure_outline = re.sub(r"<outline>|</outline>", "", xml_outline).strip()
        outline_text = ""
        level_1_cnt = 0
        level_2_cnt = 0
        level_3_cnt = 0
        while pure_outline.strip():
            try:
                level = int(re.search(r'level="(\d+)"', pure_outline).group(1))
            except:
                break
            if level == 1:
                cur_lever_1_chapters = re.search(r'<chapter level="1">(.*?)</chapter>', pure_outline, re.DOTALL).group(
                    1
                )
                level_1_cnt += 1
                level_2_cnt = 0
                outline_text += str(level_1_cnt) + ". " + cur_lever_1_chapters + "\n"
            elif level == 2:
                cur_lever_2_chapters = re.search(r'<chapter level="2">(.*?)</chapter>', pure_outline, re.DOTALL).group(
                    1
                )
                level_2_cnt += 1
                level_3_cnt = 0
                outline_text += str(level_1_cnt) + "." + str(level_2_cnt) + ". " + cur_lever_2_chapters + "\n"
            elif level == 3:
                cur_lever_1_chapters_xml = re.search(
                    r'<chapter level="3">(.*?)</chapter>', pure_outline, re.DOTALL
                ).group(1)
                chapter_name = re.search(r"<chapter_name>(.*?)</chapter_name>", cur_lever_1_chapters_xml).group(1)
                chapter_description = re.search(
                    r"<chapter_description>(.*?)</chapter_description>", cur_lever_1_chapters_xml
                ).group(1)
                level_3_cnt += 1
                outline_text += (
                    str(level_1_cnt) + "." + str(level_2_cnt) + "." + str(level_3_cnt) + ". " + chapter_name + "\n"
                )
                outline_text += "    " + chapter_description + "\n"
            pure_outline = re.sub(
                r'<chapter level="\d+">(.*?)</chapter>', "", pure_outline, flags=re.DOTALL, count=1
            ).strip()
        return outline_text

    def parse_content(self, respond):
        start_tag = "<content>"
        end_tag = "</content>"
        return respond.split(start_tag)[1].split(end_tag)[0]


def get_action():
    return LongDocumentGenerateAction()
