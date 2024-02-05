from rich.box import HEAVY_HEAD
from rich.style import Style
from rich.table import Table
from rich.console import Console
from sys import platform
import typing as t
import csv
import os.path


class BaseInfo:
    """
    Hold basic operations shared between all device info classes
    """
    def __init__(self):
        self.OS = platform
        self.table = None
        self.console = None
        self.table_title = ''
        self.col_names = []

    def init_table(self, title: str, column_names):
        """
        Initialize the table; so create it and init the column names
        """
        pass

    def create_styled_table(self, title: str) -> None:
        """
        Creates a custom rich styled table, which all outputs share.
        """
        pass

    def prepare_table(self, column_names):
        """
        Add the specified column names to the table
        """
        pass

    def print_table(self):
        """
        Print the result table to stdout
        """
        pass

    def format_bytes(self, size: t.Union[str, int], device: str = ''):
        """
        Format an integer representing a byte value into a nicer format.
        Depending on the users system, formatting is done either using base10 conversion (Ubuntu and MacOS)
        or base2 (Windows and most other Linux distros).
        Examples:
            512 = 512 B
            123456 = 1MB
        """
       pass

    @staticmethod
    def hz_to_hreadable_string(hz: int) -> str:
        """
        Transforms hertz into a human readable string with attached appropriate unit

        :param: number of hertz
        :return: human readable formatted string of hertz with unit
        """
        pass

    def determine_base_conversion_factor(self, device: str) -> int:
        """
        MacOS and Linux Ubuntu (disk storage) are using base10 unit conversion when it comes to some sort of storage (like file sizes or memory size)
        Most other OS (Linux distros and Windows) are using base2 instead.

        So to convert bytes to other units (like KB or KiB), base10 will use a factor of 1000 where base2 will use a factor of 1024!
        """
        pass