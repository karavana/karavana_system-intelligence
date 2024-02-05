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
        self.table_title = title
        self.col_names = column_names
        self.create_styled_table(title)
        self.prepare_table(column_names)

    def create_styled_table(self, title: str) -> None:
        """
        Creates a custom rich styled table, which all outputs share.
        """
        self.table = Table(show_header=True, header_style="bold magenta")
        self.table.title = title
        self.table.box = HEAVY_HEAD

    def prepare_table(self, column_names):
        """
        Add the specified column names to the table
        """
        for col_name in column_names:
            self.table.add_column(col_name)

    def print_table(self):
        """
        Print the result table to stdout
        """
        self.console = Console()
        self.console.print(self.table)

    def format_bytes(self, size: t.Union[str, int], device: str = ''):
        """
        Format an integer representing a byte value into a nicer format.
        Depending on the users system, formatting is done either using base10 conversion (Ubuntu and MacOS)
        or base2 (Windows and most other Linux distros).
        Examples:
            512 = 512 B
            123456 = 1MB
        """
        base_conversion_factor = self.determine_base_conversion_factor(device=device)
        conversion = {1000: ['B', 'KB', 'MB', 'GB', 'TB'],
                      1024: ['B', 'KiB', 'MiB', 'GiB', 'TiB']}
        if not size or size == 'NA':
            return ''
        if isinstance(size, str):
            # on some systems and linux distros, some of the values may be pre-formatted (like 128 KiB)
            # therefore, they don't need to be casted and formatted
            try:
                size = float(size)
            except ValueError:
                return size
        i = 0
        while size > base_conversion_factor and i + 1 < len(conversion[base_conversion_factor]):
            i += 1
            size /= base_conversion_factor

        # Dynamically adjust formatting based on the value
        if size % 1 == 0:  # If the size is effectively an integer
            formatted_size = f'{int(size)}'
        else:
            # Adjust the number of decimal places based on the precision needed
            formatted_size = f'{size:.2f}'.rstrip('0').rstrip('.')
        
        return f'{formatted_size} {conversion[base_conversion_factor][i]}'

    @staticmethod
    def hz_to_hreadable_string(hz: int) -> str:
        """
        Transforms hertz into a human readable string with attached appropriate unit

        :param: number of hertz
        :return: human readable formatted string of hertz with unit
        """
        # Convert to a float for more natural scaling
        if not isinstance(hz, int):
            try:
                hz = int(hz)
            except:
                raise ValueError(f"Expected an integer, got {type(hz)}")

        units = ['Hz', 'kHz', 'MHz', 'GHz', 'THz']
        magnitude = 0

        while hz >= 1000 and magnitude < len(units) - 1:
            magnitude += 1
            hz /= 1000.0
        
        return f'{hz:.2f} {units[magnitude]}'

        # Return the formatted string with the appropriate unit
        return f"{hz:.2f} {units[unit_index]}"

    def determine_base_conversion_factor(self, device: str) -> int:
        """
        MacOS and Linux Ubuntu (disk storage) are using base10 unit conversion when it comes to some sort of storage (like file sizes or memory size)
        Most other OS (Linux distros and Windows) are using base2 instead.

        So to convert bytes to other units (like KB or KiB), base10 will use a factor of 1000 where base2 will use a factor of 1024!
        """
        return 1000 if self.OS in ['darwin', 'linux_ubuntu'] else 1024
