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
    agent_list = []
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
        st.button(
            "Stop Polling" if st.session_state.polling else "Start Polling",
            on_click=lambda: st.session_state.update(polling=not st.session_state.polling),
            use_container_width=True,
        )

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
            else:
                st.toast("Failed to get agent list")
        except Exception as e:
            st.toast(f"Failed to get agent list: {str(e)}")
            web_data.agent_list = []

        # Display buttons for each available agent
        for agent_name in web_data.agent_list:
            if web_data.current_chat_agent == agent_name:
                col1, col2 = st.columns([1, 10])

                with col1:
                    # Display an arrow if this is the currently selected agent
                    st.subheader("→")

                with col2:
                    #  Button to select the agent
                    st.button(
                        agent_name,
                        on_click=change_chat_window,
                        args=(
                            "agent",
                            agent_name,
                        ),
                        use_container_width=True,
                    )
            else:
                st.button(
                    agent_name,
                    on_click=change_chat_window,
                    args=(
                        "agent",
                        agent_name,
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
        target_agent_name = prompt.split(" ")[0].split("@")[1]
        content = " ".join(prompt.split(" ")[1:])
        if target_agent_name in web_data.agent_list:
            try:
                response = requests.post(
                    "http://localhost:5000/post_message",
                    params={"target_agent_name": target_agent_name, "content": content},
                )
                if response.status_code == 200:
                    st.session_state.chat_messages.append({"role": "assistant", "content": content})
                    st.rerun()
                else:
                    st.toast(f"Agent {target_agent_name} not found")
            except Exception as e:
                st.toast(f"Error posting message: {e}")
        else:
            st.toast(f"Agent {target_agent_name} not found")
    float_parent()


def workspace_box(web_data, window_height):
    """Initialize the workspace box"""
    tab_bar_data = []
    for agent_name in web_data.agent_list:
        tab_bar_data.append(stx.TabBarItemData(id=agent_name, title=agent_name, description="Tasks to take care of"))

    # Add a default tab if no agents are available
    if not tab_bar_data:
        tab_bar_data.append(stx.TabBarItemData(id="No agent", title="No agent", description="Please add agent"))

    # Select the active agent tab
    chosen_agent_name = stx.tab_bar(data=tab_bar_data, default=0)

    with st.container(height=window_height - 330):
        if chosen_agent_name in st.session_state.agent_workspace_map:
            workspace_tabs_name = list(st.session_state.agent_workspace_map[chosen_agent_name].keys())
            if "file_upload" in workspace_tabs_name:
                workspace_tabs_name.extend(["preview markdown file"])

            if len(workspace_tabs_name) != 0:
                with st.container(border=False):
                    workspace_name = st.selectbox(
                        "select observation",
                        workspace_tabs_name,
                    )

                if workspace_name == "file_upload":
                    i = 1
                    for message in st.session_state.agent_workspace_map[chosen_agent_name][workspace_name]:
                        base64_data = message["file_content"]
                        _bytes = base64.b64decode(base64_data.encode(encoding="utf-8"))
                        print(f"{i}.{message}")
                        st.download_button(
                            label=f"Download {message['file_name']} file",
                            file_name=message["file_name"],
                            data=_bytes,
                            use_container_width=True,
                            key=message["file_name"] + str(i),
                        )
                        i += 1
                elif workspace_name == "preview markdown file":
                    file_list = [
                        file
                        for file in st.session_state.agent_workspace_map[chosen_agent_name]["file_upload"]
                        if file["file_name"].endswith(".md")
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
                            st.markdown(content)
                else:
                    st.write(st.session_state.agent_workspace_map[chosen_agent_name][workspace_name])
    float_parent()


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


def handle_message(agent_name: str, message: Message):
    agent_name = agent_name.lower()

    def add_to_workspace(agent_name, env_handle_type, message):
        if message["content"].startswith("```json"):
            print(message["content"][7:-3])
            message["content"] = json.loads(message["content"][7:-3])
        if agent_name not in st.session_state.agent_workspace_map:
            st.session_state.agent_workspace_map[agent_name] = {}
        if env_handle_type not in st.session_state.agent_workspace_map[agent_name]:
            st.session_state.agent_workspace_map[agent_name][env_handle_type] = []
        st.session_state.agent_workspace_map[agent_name][env_handle_type].append(message)

    if message["env_handle_type"] in [
        EnvironmentHandleType.COMMAND,
        EnvironmentHandleType.CONTROL,
        EnvironmentHandleType.THOUGHT,
        EnvironmentHandleType.BASE_ACTION_MESSAGE,
        EnvironmentHandleType.FILE_UPLOAD,
    ]:
        add_to_workspace(agent_name, message["env_handle_type"], message)
        print("handel other")
    elif message["env_handle_type"] == EnvironmentHandleType.COMUNICATION:
        st.session_state.chat_messages.append(
            {"role": message["send_from"], "content": message["send_to"] + message["content"]}
        )
        print("handle communcate")
    else:
        print("handel error")


def fetch_message_from_backend():
    try:
        response = requests.get(
            "http://localhost:5000/get_message", params={"position": st.session_state.current_message_id}
        )
        if response.status_code == 200:
            data = response.json()
            message = data["message"]
            next_position_tag = data["next_position_tag"]
            agent_name = data["agent_name"]
            new_message = bool(data["new_message"])
            if new_message:
                message = json.loads(message)
                handle_message(agent_name, message)
                st.session_state.current_message_id = next_position_tag
                st.rerun()
        else:
            st.error("Failed to get message from the backend.")
    except Exception as e:
        st.error(f"An error occurred while fetching message from the backend: {str(e)}")


def start_polling():
    """Start polling the backend for new messages"""
    while True:
        fetch_message_from_backend()
        time.sleep(3)


main()
if st.session_state.polling:
    start_polling()
