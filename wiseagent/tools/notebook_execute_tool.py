import base64
from queue import Empty
from uuid import uuid4

import nbformat as nbf
from jupyter_client import KernelManager


class JupyterNotebookTool:
    def __init__(self):
        self.is_running = False

    def start(self):
        self.km = KernelManager(kernel_name="python3")
        self.km.start_kernel()  # 启动内核
        self.kc = self.km.client()
        self.kc.start_channels()
        self.notebook = nbf.v4.new_notebook()
        self.is_running = True

    def execute_code(self, code):
        """
        Execute code in a notebook
        Args:
            code (str): Code to execute
        """
        try:
            if not self.is_running:
                self.start()
            # Add code to notebook
            code_cell = nbf.v4.new_code_cell(source=code)
            self.notebook["cells"].append(code_cell)

            # Send execution request
            msg_id = self.kc.execute(code)

            # Wait for reply
            reply = self.kc.get_shell_msg(timeout=None)
            if reply["content"]["status"] == "error":
                print("Execution error:")
                for line in reply["content"]["traceback"]:
                    print(line)
                return "\n".join(reply["content"]["traceback"]), []

            # Get execution result
            output = []
            temp = []
            img_list = []
            while True:
                try:
                    msg = self.kc.get_iopub_msg(timeout=1)  # timeout in seconds
                    result = self.handle_message(code_cell, msg)
                    if "display_data" in msg["msg_type"]:
                        img_list.append(result)
                    else:
                        output.append(result)
                        temp.append(msg)
                except Empty:
                    # The queue is empty, execute finished
                    break
                except Exception as e:
                    print(f"An error occurred while getting iopub message: {e}")
                    break
            return "".join(output), img_list
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Traceback:")
            import traceback

            traceback.print_exc()
            return str(e), []

    def handle_message(self, code_cell, msg):
        output_type = msg["msg_type"]
        content = msg["content"]

        if output_type == "stream":
            stream_output = nbf.v4.new_output(output_type="stream", name=content["name"], text=content["text"])
            code_cell["outputs"].append(stream_output)
            return content["text"]
        elif output_type == "execute_result":
            execute_result = nbf.v4.new_output(
                output_type="execute_result", data=content["data"], execution_count=content["execution_count"]
            )
            code_cell["outputs"].append(execute_result)
            return content["data"]["text/plain"]
        elif output_type == "display_data":
            display_data = nbf.v4.new_output(
                output_type="display_data", data=content["data"], metadata=content["metadata"]
            )
            code_cell["outputs"].append(display_data)
            return content["data"]
        elif output_type == "error":
            error_output = nbf.v4.new_output(
                output_type="error", ename=content["ename"], evalue=content["evalue"], traceback=content["traceback"]
            )
            code_cell["outputs"].append(error_output)
            return "\n".join(content["traceback"])
        else:
            return ""

    def save_notebook(self, filename):
        """Save the notebook to a file"""
        with open(filename, "w", encoding="utf-8") as f:
            nbf.write(self.notebook, f)

    def shutdown(self):
        """Close the kernel and channels"""
        self.kc.stop_channels()
        self.km.shutdown_kernel(now=True)
