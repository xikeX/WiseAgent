"""
Author: Huang Weitao
Date: 2024-10-24 11:29:05
LastEditors: Huang Weitao
LastEditTime: 2024-10-24 11:32:59
Description: 
"""
import os
import tempfile
import unittest

from wiseagent.action.normal_action.editor import EditorAction


class TestEditorAction(unittest.TestCase):
    def setUp(self):
        self.editor = EditorAction()
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.test_dir.name, "test.txt")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_read_text(self):
        test_content = "This is a test file."
        with open(self.test_file, "w") as f:
            f.write(test_content)
        result = self.editor.read_text(self.test_file)
        self.assertIn(test_content, result)

    def test_replace_content(self):
        test_content = "Hello, world!"
        new_content = "Hello, Python!"
        with open(self.test_file, "w") as f:
            f.write(test_content)
        result = self.editor.replace_content(self.test_file, test_content, new_content)
        self.assertIn("[Observe] Replace content in file successfully\n[End Observe]", result)
        with open(self.test_file, "r") as f:
            self.assertEqual(f.read(), new_content)

    def test_insert_content(self):
        pre_line = "Hello,"
        new_content = "Welcome to Python."
        with open(self.test_file, "w") as f:
            f.write(pre_line + "\nworld!")
        result = self.editor.insert_content(self.test_file, pre_line, new_content)
        self.assertIn("[Observe] Insert content in file successfully\n[End Observe]", result)
        with open(self.test_file, "r") as f:
            lines = f.read()
            lines = lines.split("\n")
            self.assertEqual(lines[1], new_content)


if __name__ == "__main__":
    unittest.main()
