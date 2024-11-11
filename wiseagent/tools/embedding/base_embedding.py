"""
Author: Huang Weitao
Date: 2024-11-03 16:55:17
LastEditors: Huang Weitao
LastEditTime: 2024-11-03 16:56:07
Description: 
"""

from abc import abstractmethod


class BaseEmbedding:
    @abstractmethod
    def embed(self, input):
        """Returns a vector representation of the input."""
