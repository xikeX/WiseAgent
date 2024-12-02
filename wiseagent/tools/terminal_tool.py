"""
Author: Huang Weitao
Date: 2024-10-23 14:24:14
LastEditors: Huang Weitao
LastEditTime: 2024-10-23 14:24:14
Description:  
"""
import asyncio
import threading
import time

from wiseagent.common.const import WORKING_DIR


class TerminalTool:
    def __init__(self, shell="cmd", shell_args=None):
        self.shell = shell
        self.shell_args = shell_args if shell_args is not None else []
        self.process = None
        self.reader = None
        self.writer = None
        self.loop = asyncio.new_event_loop()
        self.stop_event = threading.Event()
        self.is_running = False

    def start(self):
        """Starts the shell process and the event loop."""
        self.thread = threading.Thread(target=self._run_event_loop)
        self.thread.daemon = True
        self.thread.start()
        self.is_running = True
        time.sleep(1)
        respond = self.run_command("activate deeplearning")
        print(respond)

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start_shell())
        self.loop.run_forever()
        self.loop.close()

    async def _start_shell(self, cwd=None):
        if cwd is None:
            cwd = str(WORKING_DIR.resolve())
        self.process = await asyncio.create_subprocess_exec(
            self.shell,
            *self.shell_args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd
        )
        self.reader = self.process.stdout
        self.writer = self.process.stdin

    def run_command(self, command):
        if self.is_running is False:
            self.start()
        if self.writer and not self.writer.is_closing():
            self.writer.write((command + "\n").encode())
            asyncio.run_coroutine_threadsafe(self.writer.drain(), self.loop)
            respond = self.read_terminal()
            return respond
        else:
            raise RuntimeError("Shell process is not running or the writer is closed.")

    def read_terminal(self, timeout=1):
        """Reads the output from the shell process."""
        future = asyncio.run_coroutine_threadsafe(self._read(timeout), self.loop)
        return future.result()

    async def _read(self, timeout):
        """Reads the output from the shell process asynchronously."""
        respond = ""
        while True:
            try:
                line = await asyncio.wait_for(self.reader.readline(), timeout)
                respond += line.decode("gbk")
            except asyncio.TimeoutError:
                break
        return respond

    def close(self):
        """Closes the shell process and the event loop."""
        if self.writer:
            self.writer.close()
        if self.process:
            try:
                self.process.terminate()
                future = asyncio.run_coroutine_threadsafe(self.process.wait(), self.loop)
                future.result()  # Wait for the process to terminate
            except ProcessLookupError:
                # The terminal process may have already exited
                pass

        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.stop_event.set()
        self.thread.join()
