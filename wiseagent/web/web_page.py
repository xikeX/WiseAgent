import base64
import json
import os
import time
from dataclasses import dataclass

import extra_streamlit_components as stx
import replicate
import requests
import streamlit as st
from streamlit_float import float_init, float_parent
from streamlit_js_eval import streamlit_js_eval

from wiseagent.protocol.message import EnvironmentHandleType, Message

# Set the page configuration
st.set_page_config(page_title="WiseAgent", layout="wide")
float_init()
CODE_TYPE = {
    "py": "python",
    "js": "javascript",
    "java": "java",
    "c": "c",
    "cpp": "c++",
    "cs": "c#",
    "go": "go",
    "rb": "ruby",
    "php": "php",
    "pl": "perl",
    "swift": "swift",
    "m": "objective-c/objective-c++",
    "scala": "scala",
    "kt": "kotlin",
    "rs": "rust",
    "ts": "typescript",
    "lua": "lua",
    "sh": "bash/shell",
    "hs": "haskell",
    "erl": "erlang",
    "exs": "elixir",
    "fs": "f#",
    "r": "r",
    "ml": "ocaml",
    "vb": "visual basic .net",
    "groovy": "groovy",
    "dart": "dart",
    "sol": "solidity (ethereum)",
    "elm": "elm",
    "clj": "clojure",
    "cljs": "clojurescript",
    "fsx": "f# script",
    "md": "markdown",
    "html": "html",
    "css": "css",
    "json": "json",
    "yml": "yaml",
    "xml": "xml",
    "txt": "text",
    "log": "log",
    "ini": "ini",
    "conf": "ini",
    "cfg": "ini",
    "properties": "ini",
    "toml": "toml",
    "csv": "csv",
    "tsv": "tsv",
    "md": "markdown",
    "rst": "reStructuredText",
    "tex": "latex",
    "bib": "bibtex",
    "rmd": "R markdown",
    "ipynb": "jupyter notebook",
}


@dataclass
class WebData:
    """
    Data class to hold the current state of the chat environment and agents.
    The chat environment and chat agent are exclusive; if one is changed, the other will be reset.
    """

    # Current active chat environment
    current_chat_enviornment = None
    environment_list = ["MultiAgentEnvironment"]
    # Current active chat agent. cur
    current_chat_agent = None
    agent_list = []  # [{"name":agent_name,"active":0/1}]
    # The agents file that has been loaded
    agent_yaml_file = []


# Initialize session state variables
if "current_message_id" not in st.session_state:
    st.session_state["current_message_id"] = 0
    st.session_state["agent_workspace_map"] = {}
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

if "polling" not in st.session_state:
    st.session_state.polling = False


def get_web_data() -> WebData:
    """Retrieve or initialize the web data from session state."""
    if "web_data" not in st.session_state:
        st.session_state["web_data"] = WebData()
    return st.session_state["web_data"]


def main():
    """Main function where the app execution starts."""
    display_sidebar_ui()
    main_windows()


def display_sidebar_ui():
    """
    Displays the sidebar UI components, including environment and agent selection,
    as well as the option to start/stop polling and upload new agent YAML files.
    """
    with st.sidebar:
        st.title("WiseAgent System")

        # Get or initialize web data
        web_data = get_web_data()

        # Environment selection
        st.subheader("Environment List")
        # TODO: init web environment_list
        web_data.current_chat_enviornment = web_data.environment_list[0]
        for enviornment_name in web_data.environment_list:
            # Create columns for the arrow and the environment name
            if web_data.current_chat_enviornment == enviornment_name:
                col1, col2 = st.columns([1, 10])
                with col1:
                    # Display an arrow if this is the currently selected environment
                    st.subheader("→")
                with col2:
                    st.button(
                        enviornment_name,
                        on_click=change_chat_window,
                        args=(
                            "environment",
                            enviornment_name,
                        ),
                        use_container_width=True,
                    )
            else:
                st.button(
                    enviornment_name,
                    on_click=change_chat_window,
                    args=(
                        "environment",
                        enviornment_name,
                    ),
                    use_container_width=True,
                )

        # Agent selection and upload
        st.subheader("Agent List")
        uploaded_file = st.file_uploader("select a agent data YAML  file", type=["yaml"])
        if uploaded_file and uploaded_file not in web_data.agent_yaml_file:
            # Read and decode the content of the uploaded file
            file_content = uploaded_file.read()
            if uploaded_file.type == "application/octet-stream":
                yaml_string = file_content.decode("utf-8")

                # Send the YAML string to the server to add the new agent
                try:
                    response = requests.post("http://localhost:5000/add_agent", params={"yaml_string": yaml_string})
                    if response.status_code == 200:
                        web_data.agent_yaml_file.append(uploaded_file)
                    else:
                        st.toast("Failed to add agent")
                except Exception as e:
                    st.toast(f"Failed to add agent: {str(e)}")
        # Fetch the list of available agents from the server
        try:
            response = requests.post("http://localhost:5000/get_agent_list")
            if response.status_code == 200:
                web_data.agent_list = response.json()["agent_list"]
                for agent in web_data.agent_list:
                    if agent["active"] != 0:
                        st.session_state.polling = True
                        break
            else:
                st.toast("Failed to get agent list")
        except Exception as e:
            st.toast(f"Failed to get agent list: {str(e)}")
            web_data.agent_list = []
        print(web_data.agent_list)
        # Display buttons for each available agent
        for agent in web_data.agent_list:
            if agent["active"] > 0:
                col1, col2 = st.columns([1, 10])

                with col1:
                    # Display an arrow if this is the currently selected agent
                    st.write(":rocket:")

                with col2:
                    #  Button to select the agent
                    st.button(
                        agent["name"],
                        on_click=change_chat_window,
                        args=(
                            "agent",
                            agent["name"],
                        ),
                        use_container_width=True,
                    )
            else:
                st.button(
                    agent["name"],
                    on_click=change_chat_window,
                    args=(
                        "agent",
                        agent["name"],
                    ),
                    use_container_width=True,
                )


def change_chat_window(switch_button_type, enviornment_name):
    web_data = get_web_data()
    if switch_button_type == "environment":
        web_data.current_chat_enviornment = enviornment_name
        st.toast(f"Environment changed to {enviornment_name}")
        web_data.current_chat_agent = None
    elif switch_button_type == "agent":
        web_data.current_chat_agent = enviornment_name
        st.toast(f"Agent changed to {enviornment_name}")
        web_data.current_chat_enviornment = None


def chat_box(web_data, window_height):
    """Initialize the chat box"""
    st.subheader("ChatBox")
    with st.container(height=window_height - 330, border=True):
        # Display chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                response = message["content"]
                st.write(response)
    # Reset chat button if chat is aborted
    if prompt := st.chat_input():
        # Chat input for user to send messages
        try:
            target_agent_name = prompt.split(" ")[0].split("@")[1]
            content = " ".join(prompt.split(" ")[1:])
        except:
            target_agent_name = ""
            content = ""
        if target_agent_name in [agent["name"] for agent in web_data.agent_list]:
            try:
                response = requests.post(
                    "http://localhost:5000/post_message",
                    params={"target_agent_name": target_agent_name, "content": content},
                )
                if response.status_code == 200:
                    st.session_state.chat_messages.append({"role": "user", "content": content})
                    st.rerun()
                else:
                    st.toast(f"Agent {target_agent_name} not found")
            except Exception as e:
                st.toast(f"Error posting message: {e}")
        else:
            st.toast(f"Agent {target_agent_name} not found.Please input the format '@agent_name message'")
    float_parent()


def workspace_box(web_data, window_height):
    """Initialize the workspace box"""
    tab_bar_data = []
    for agent_name in [agent["name"] for agent in web_data.agent_list]:
        tab_bar_data.append(stx.TabBarItemData(id=agent_name, title=agent_name, description="Tasks to take care of"))

    # Add a default tab if no agents are available
    if not tab_bar_data:
        tab_bar_data.append(stx.TabBarItemData(id="No agent", title="No agent", description="Please add agent"))

    # Select the active agent tab
    chosen_agent_name = stx.tab_bar(
        data=tab_bar_data, default=web_data.agent_list[0]["name"] if web_data.agent_list else "No agent"
    )

    with st.container(height=window_height - 330):
        if chosen_agent_name in st.session_state.agent_workspace_map:
            workspace_tabs_name = list(st.session_state.agent_workspace_map[chosen_agent_name].keys())
            if "file_upload" in workspace_tabs_name:
                workspace_tabs_name.extend(["preview markdown file"])

            if len(workspace_tabs_name) != 0:
                workspace_name = st.selectbox(
                    "select observation",
                    workspace_tabs_name,
                )

                if workspace_name == "file_upload":
                    for index, message in enumerate(
                        st.session_state.agent_workspace_map[chosen_agent_name][workspace_name]
                    ):
                        base64_data = message["file_content"]
                        _bytes = base64.b64decode(base64_data.encode(encoding="utf-8"))
                        print(f"{index}.{message}")
                        st.download_button(
                            label=f"Download {message['file_name']} file",
                            file_name=message["file_name"],
                            data=_bytes,
                            use_container_width=True,
                            key=message["file_name"] + str(index),
                        )
                elif workspace_name == "preview markdown file":
                    file_list = [
                        file
                        for file in st.session_state.agent_workspace_map[chosen_agent_name]["file_upload"]
                        if file["file_name"].split(".")[-1]
                        in ["html", "md", "txt", "py", "json", "css", "js", "xml", "vue"]
                    ]
                    file_name_list = [file["file_name"] for file in file_list]
                    file_name = st.selectbox("Select a file to preview", file_name_list, key="file_name")
                    if file_name:
                        if base64_data := next(
                            (
                                file["file_content"]
                                for file in st.session_state.agent_workspace_map[chosen_agent_name]["file_upload"]
                                if file["file_name"] == file_name
                            ),
                            None,
                        ):
                            _bytes = base64.b64decode(base64_data.encode(encoding="utf-8"))
                            content = _bytes.decode(encoding="utf-8")
                            st.markdown(f"```{CODE_TYPE.get(file_name.split('.')[-1], '')}\n" + content + "\n```")
                else:
                    st.write(st.session_state.agent_workspace_map[chosen_agent_name][workspace_name])
    # float_parent()


def main_windows():
    """
    Displays the chat messages and workspace tabs. The chat messages are shown in the first column,
    and the workspace for the selected agent is shown in the second column.
    """
    # Create two columns: one for the chat box and one for the workspace
    col1, col2 = st.columns([3, 7])

    # Get the current web data
    web_data = get_web_data()

    # Get the height of the window
    window_height = streamlit_js_eval(
        js_expressions="window.parent.innerHeight",
        key="HEIGHT",
        want_output=True,
    )
    while window_height == None:
        time.sleep(0.1)

    # First column: ChatBox
    with col1:
        chat_box(web_data=web_data, window_height=window_height)

    # Second column: Workspace
    with col2:
        workspace_box(web_data=web_data, window_height=window_height)


def abort_chat(error_message: str):
    """Display an error message requiring the chat to be cleared.
    Forces a rerun of the app."""
    assert error_message, "Error message must be provided."
    error_message = f":red[{error_message}]"
    if st.session_state.chat_messages[-1]["role"] != "assistant":
        st.session_state.chat_messages.append({"role": "assistant", "content": error_message})
    else:
        st.session_state.chat_messages[-1]["content"] = error_message
    st.session_state.chat_aborted = True
    st.rerun()


main()


def handle_message(message: Message):
    agent_name = message["send_from"].lower()

    def add_to_workspace(_agent_name, env_handle_type, message):
        if message["content"].startswith("```json"):
            print(message["content"][7:-3])
            message["content"] = json.loads(message["content"][7:-3])
        if _agent_name not in st.session_state.agent_workspace_map:
            st.session_state.agent_workspace_map[_agent_name] = {}
        if env_handle_type not in st.session_state.agent_workspace_map[_agent_name]:
            st.session_state.agent_workspace_map[_agent_name][env_handle_type] = []
        st.session_state.agent_workspace_map[_agent_name][env_handle_type].insert(0, message)

    if message["env_handle_type"] in [
        EnvironmentHandleType.COMMAND,
        EnvironmentHandleType.CONTROL,
        EnvironmentHandleType.THOUGHT,
        EnvironmentHandleType.BASE_ACTION_MESSAGE,
        EnvironmentHandleType.FILE_UPLOAD,
    ]:
        add_to_workspace(agent_name, message["env_handle_type"], message)
    elif message["env_handle_type"] == EnvironmentHandleType.COMUNICATION:
        st.session_state.chat_messages.append(
            {"role": message["send_from"], "content": message["send_to"] + message["content"]}
        )
        print("handle communcate")
    elif message["env_handle_type"] == EnvironmentHandleType.SLEEP:
        agent_name = message["send_from"]
        active_agent_number = 0
        for agent in get_web_data().agent_list:
            if agent["name"] == agent_name:
                agent["active"] = 0
            if agent["active"] != 0:
                active_agent_number += 1
        if active_agent_number == 0:
            st.session_state.polling = False

    elif message["env_handle_type"] == EnvironmentHandleType.WAKEUP:
        agent_name = message["send_from"]
        for agent in get_web_data().agent_list:
            if agent["name"] == agent_name:
                agent["active"] = 1
        st.session_state.polling = True
    else:
        print("handel error")


def fetch_message_from_backend():
    try:
        response = requests.get(
            "http://localhost:5000/get_message", params={"position": st.session_state.current_message_id}
        )
        if response.status_code == 200:
            data = response.json()
            message_list = data["message_list"]
            next_position_tag = data["next_position_tag"]
            new_message = bool(data["new_message"])
            if new_message:
                message_list = json.loads(message_list)
                for message in message_list:
                    handle_message(message)
                st.session_state.current_message_id = next_position_tag
                st.rerun()
                return True
            else:
                return False
        else:
            st.error("Failed to get message from the backend.")
    except Exception as e:
        st.error(f"An error occurred while fetching message from the backend: {str(e)}")


def start_polling():
    """Start polling the backend for new messages"""
    while True:
        has_new_message = fetch_message_from_backend()
        if not has_new_message:
            time.sleep(3)


if st.session_state.polling:
    start_polling()
