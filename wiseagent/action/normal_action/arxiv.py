"""
Author: Huang Weitao
Date: 2024-09-28 22:48:34
LastEditors: Huang Weitao
LastEditTime: 2024-09-28 22:49:05
Description: This action is to get the arxiv information to help summary the current research eare and get the next research direction.
"""
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlencode

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from tqdm import tqdm

from wiseagent.action.action_annotation import action
from wiseagent.action.base import BaseAction, BaseActionData
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.common.file_io import repair_path, write_excel, write_file
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.message import BaseActionMessage, FileUploadMessage

BASE_CLASS = "\n".join(
    [
        "交互环境",
        "数据集",
        "架构",
        "社交仿真",
        "持续学习",
        "网页操作",
        "角色扮演",
        "操作系统操作",
        "模型微调",
        "交互学习",
        "智能体安全",
        "多模态",
        "数据生成",
        "代码生成",
        "自动数据分析",
        "意图识别",
        "信息抽取",
        "知识图谱",
        "具身智能",
        "使用工具",
        "模型水印",
    ]
)

TRANSLATION_PROMPT = """
## 现有的类别
{base_class}
...（其他,根据需要生成）

## 论文摘要
{abstract}

## 指令
你需要做两件事情：
1. 根据摘要将论文文章分类，文章可以由多个类别，以分号分隔，其中最特殊的类别放在最前面
2. 将摘要翻译成中文

## 输出格式
<label>最特殊的类别1;类别2;...</label>
<abstract>
中文摘要
</abstract>

你的回答:
"""

# Use to write paper item to
PAPER_ITEM_MARKDOWN_FORMAT = """
### {index}. {title}

- 时间 : {time}
- 作者 : {author}
- 标签 : {labels}
- 链接 : {link}
摘要: {abstract}

"""


class arxivActionData(BaseActionData):
    # playwright tools
    playwright: Any = None  #
    arxiv_browser: Any = None
    arxiv_page: Any = None

    # arxiv paper data
    from_date: Any = None
    to_date: Any = None
    current_arxiv_data: List[Dict] = []


@singleton
class ArxivAction(BaseAction):
    action_name: str = "arxivAction"
    action_description: str = (
        "Get the arxiv information to help summary the current research eare and get the next research direction."
    )

    def init_agent(self, agent_data: AgentData):
        agent_data.set_action_data(self.action_name, arxivActionData())

    ## class action -----------------------------------

    @action()
    def search_arxiv_paper(self, search_terms: str, pass_days: int = 1):
        """Builds the URL for an advanced search on arXiv.org.

        Args:
            search_terms (str): A string containing the search terms separated by spaces. Each search term should be enclosed in double quotes.Terms can be linked using AND, OR, and NOT operators
            pass_days (int, optional): The number of days to search back. Defaults to 1.

        Example:
            >>> build_arxiv_search_url("\"Agent\" AND \"LLM\"", 7)
            This will return the URL for searching for articles containing the terms "Agent" and "LLM" in the title or abstract, published in the last 7 days.
            >>> build_arxiv_search_url("\"Agent\" AND \"LLM\" NOT \"ChatGPT\"", 30)
            This will return the URL for searching for articles containing the terms "Agent" and "LLM" in the title or abstract, published in the last 30 days, excluding articles containing the term "ChatGPT".
        """
        # Get the action necessary data
        agent_core = get_agent_core()
        agent_data = get_current_agent_data()
        arxiv_data = agent_data.get_action_data(self.action_name)
        page = self.get_arxiv_browser_page(agent_data)

        # Go to the search page and analyze the data
        search_url = self.build_arxiv_search_url(search_terms, pass_days)
        page.goto(search_url)
        html = page.content()
        article_information_list = self.anaylze_data(html)

        # Save the data to the acton data
        arxiv_data.current_arxiv_data = article_information_list
        arxiv_data.from_date = (datetime.now() - timedelta(days=pass_days)).strftime("%Y-%m-%d")
        arxiv_data.to_date = (datetime.now()).strftime("%Y-%m-%d")

        # Save the data to the file. NOTE: This will be remove in the near version.
        file_content = json.dumps(article_information_list, ensure_ascii=False, indent=4)
        write_file("arxiv.json", file_content)

        # Report the arxiv information to the agent core
        article_information_json_string = "```json\n" + file_content + "```"
        agent_core.monitor.add_message(BaseActionMessage(content=article_information_json_string))

        # Report the arxiv information to the agent.
        article_information_description = ""
        for index, (_, title, authors, abstract) in enumerate(article_information_list):
            article_information_description += f"article {index+1}:\n"
            article_information_description += f"Title: {title}\nAuthors: {authors}\nAbstract: {abstract}\n\n"
        return (
            article_information_description
            + f"The size of the data is {len(article_information_list)}. Search arxiv paper task finished."
        )

    @action()
    def save_arxiv_paper(self, save_excel_path: str = "output.xlsx"):
        """Save the arxiv paper to excel
        Args:
            save_excel_path (str): The path to save the excel file.
        """
        # Repair the path to base on the agent working space.
        save_excel_path = Path(save_excel_path)
        save_excel_path = repair_path(save_excel_path)

        # Get the base data of this action
        agent_core = get_agent_core()
        agent_data = get_current_agent_data()
        arxiv_data = agent_data.get_action_data(self.action_name)

        # Prepare paper data
        paper_data = [
            {
                "id": index + 1,
                "title": title,
                "time": self.parse_time(arxiv_id_list),
                "author": authors,
                "link": f"https://arxiv.org/abs/{arxiv_id_list}",
                "conference": "arxiv",
                "abstract": abstract,
            }
            for index, (arxiv_id_list, title, authors, abstract) in enumerate(arxiv_data.current_arxiv_data)
        ]
        paper_data = paper_data[:2]
        # Translate and classify papers
        for item in tqdm(paper_data, total=len(paper_data)):
            self.translate_and_classify(item)
            agent_core.monitor.add_message(
                BaseActionMessage(content="```json" + json.dumps(item, ensure_ascii=False) + "```")
            )

        # classify the paper
        classified_data = defaultdict(list)
        for item in paper_data:
            primary_label = item["label"][0].strip() if item["label"] else "其他"
            classified_data[primary_label].append(item)

        # Save to Excel
        write_excel(save_excel_path, paper_data)

        # Upload the Excel file to the reporter
        with open(save_excel_path, "rb") as f:
            agent_core.monitor.add_message(FileUploadMessage(file_name=save_excel_path.name, file_content=f.read()))

        # Generate and save Markdown
        markdown_path = save_excel_path.with_suffix(".md")
        f = open(markdown_path, "w", encoding="utf-8")
        f.write(f"# Arxiv Paper\n - {arxiv_data.from_date} - {arxiv_data.to_date}\n")
        f.write("[TOC]\n\n")
        for key in classified_data:
            f.write(f"## {key} : {len(classified_data[key])}篇\n")
            for index, item in enumerate(classified_data[key]):
                labels = "|".join(item["label"])
                f.write(
                    PAPER_ITEM_MARKDOWN_FORMAT.format(
                        index=index + 1,
                        labels=labels,
                        title=item["title"],
                        time=item["time"],
                        author=item["author"],
                        link=item["link"],
                        abstract=item["abstract_translated"],
                    )
                )
        f.close()

        # Upload the Markdown file to the reporter
        with open(markdown_path, "rb") as f:
            agent_core.monitor.add_message(FileUploadMessage(file_name=markdown_path.name, file_content=f.read()))

        return f"Save the arxiv paper task finished. The path is {save_excel_path}."

    # class tools for this action --------------------------------------------------

    def anaylze_data(self, html: str):
        # 解析 HTML
        soup = BeautifulSoup(html, "html.parser")

        # 提取标题
        title_list = soup.find_all("p", class_="title is-5 mathjax")
        title_list = [t.get_text(strip=True) for t in title_list]

        # 提取作者
        authors_list = []
        for authors_container in soup.find_all("p", class_="authors"):
            authors_list.append("|".join([a.get_text() for a in authors_container.find_all("a")]))

        # 提取全部摘要
        abstract_full_list = soup.find_all("span", class_="abstract-full has-text-grey-dark mathjax")
        abstract_full_list = [abstract.get_text(strip=True) for abstract in abstract_full_list]

        # arxiv id
        arxiv_id_list = soup.find_all("p", class_="list-title is-inline-block")
        arxiv_id_list = [arxiv_id.get_text(strip=True) for arxiv_id in arxiv_id_list]
        article_information_list = list(zip(arxiv_id_list, title_list, authors_list, abstract_full_list))
        return article_information_list

    # Tools
    def build_arxiv_search_url(self, search_terms: str, pass_days: int = 1):
        """Builds the URL for an advanced search on arXiv.org.
        Args:
            search_terms (str): A string containing the search terms separated by spaces. Each search term should be enclosed in double quotes.Terms can be linked using AND, OR, and NOT operators
            pass_days (int, optional): The number of days to search back. Defaults to 1.

        Example:
            >>> build_arxiv_search_url("\"Agent\" AND \"LLM\"", 7)
            This will return the URL for searching for articles containing the terms "Agent" and "LLM" in the title or abstract, published in the last 7 days.
            >>> build_arxiv_search_url("\"Agent\" AND \"LLM\" NOT \"ChatGPT\"", 30)
            This will return the URL for searching for articles containing the terms "Agent" and "LLM" in the title or abstract, published in the last 30 days, excluding articles containing the term "ChatGPT".
        """
        base_url = "https://arxiv.org/search/advanced?"
        params = {
            "advanced": "",
            "classification-include_cross_list": "include",
            "date-filter_by": "date_range",
            "date-date_type": "submitted_date",
            "abstracts": "show",
            "size": 200,
            "order": "announced_date_first",
            "classification-physics_archives": "all",
        }

        search_tuples = []
        search_terms = search_terms.split('"')
        search_terms = ["AND"] + [search_term.strip() for search_term in search_terms if search_term.strip()]
        i = 0
        while i < len(search_terms):
            operator, search_term, search_field = search_terms[i], search_terms[i + 1], "all"
            operator = operator.upper()
            if operator not in ["AND", "OR", "NOT"]:
                raise ValueError("Invalid operator. Only AND, OR, and NOT are allowed.")
            search_tuples.append((operator, search_term, search_field))
            i += 2

        # 2024-09-26
        params["date-from_date"] = (datetime.now() - timedelta(days=pass_days)).strftime("%Y-%m-%d")
        params["date-to_date"] = (datetime.now()).strftime("%Y-%m-%d")

        # 处理搜索条件
        for i, (operator, term, field) in enumerate(search_tuples):
            params[f"terms-{i}-operator"] = operator
            params[f"terms-{i}-term"] = term
            params[f"terms-{i}-field"] = field

        # 生成完整的 URL
        return base_url + urlencode(params, doseq=True)

    def get_arxiv_browser_page(self, agent_data: AgentData):
        """Get arxiv browser from the action data."""
        arxiv_action_data = agent_data.get_action_data(self.action_name)
        if arxiv_action_data.arxiv_browser is None:
            arxiv_action_data.playwright = sync_playwright().start()
            arxiv_action_data.arxiv_browser = arxiv_action_data.playwright.chromium.launch(headless=False)
        if arxiv_action_data.arxiv_page is None:
            arxiv_action_data.arxiv_page = arxiv_action_data.arxiv_browser.new_page()
        return arxiv_action_data.arxiv_page

    def parse_time(slef, arxiv_id):
        DATE_FORMAT = "20{}-{}"
        time_part = arxiv_id.split(".")[0].split(":")[1]
        year, month = time_part[:2], time_part[2:4]
        return DATE_FORMAT.format(year, month)

    def translate_and_classify(self, arxiv_paper_item):
        """Translates the abstract of an arXiv item and classifies it using the LLM."""
        content = TRANSLATION_PROMPT.format(base_class=BASE_CLASS, abstract=arxiv_paper_item["abstract"])
        try:
            output = self.llm_ask(prompt=content, memory=[], system_prompt="")
            label_start, label_end = "<label>", "</label>"
            abstract_start, abstract_end = "<abstract>", "</abstract>"

            label = output[output.find(label_start) + len(label_start) : output.find(label_end)].strip().split(";")
            abstract_translated = output[
                output.find(abstract_start) + len(abstract_start) : output.find(abstract_end)
            ].strip()

            arxiv_paper_item["label"] = label
            arxiv_paper_item["abstract_translated"] = abstract_translated
        except Exception as e:
            print(f"Error processing {arxiv_paper_item['title']}: {e}")
            arxiv_paper_item["label"] = []
            arxiv_paper_item["abstract_translated"] = ""


def get_action():
    return ArxivAction()
