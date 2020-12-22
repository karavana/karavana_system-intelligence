import logging
import subprocess
from sys import platform
import typing as t
from rich import print

from .base_info import BaseInfo
from .util.unit_conversion_util import hz_to_hreadable_string
from .util.process_util import is_process_accessible

_LOG = logging.getLogger(__name__)

try:
    import cpuinfo
except ImportError:
    cpuinfo = None
    print('[bold yellow]Unable to import package cpuinfo. CPU information may be limited.')
except Exception:  # noqa E722
    # raise Exception("py-cpuinfo currently only works on X86 and some ARM CPUs.")
    cpuinfo = None  # pylint: disable = invalid-name
    print('[bold red]Package cpuinfo does not support this system!')

try:
    import pint
except ImportError:
    pint = None
    print('[bold yellow]Unable to import package pint. CPU information may be limited.')

try:
    import psutil
except ImportError:
    psutil = None
    print('[bold yellow]Unable to import package psutil. CPU and Network information may be limited.')


class CpuInfo(BaseInfo):
    """
    Bla
    """

    def __init__(self):
        super().__init__()
        self.CPU = cpuinfo is not None and pint is not None
        self.CPU_CLOCK = psutil is not None
        self.CPU_CORES = psutil is not None
        self.OS = platform

    def query_cpu(self, **_) -> t.Mapping[str, t.Any]:
        """
        Get information about CPU present in the system.
        """
        if not self.CPU:
            return {}
        cpu = cpuinfo.get_cpu_info()
        clock_current, clock_min, clock_max = self.query_cpu_clock()
        logical_cores, physical_cores = self.query_cpu_cores()
        cache = dict(self._get_cache_sizes(cpu))
        for level, hz in cache.items():
            cache[level] = hz_to_hreadable_string(hz)

        return {
            'vendor_id_raw': cpu.get('vendor_id_raw'),
            'hardware_raw': cpu.get('hardware_raw') if self.OS == 'linux' else '',
            'brand_raw': cpu.get('brand_raw'),
            'arch': cpu.get('arch'),
            'logical_cores': str(logical_cores),
            'physical_cores': str(physical_cores),
            'clock': f'{str(clock_current)} MHz',
            'clock_min': f'{str(clock_min)} MHz',
            'clock_max': f'{str(clock_max)} MHz',
            'cache': str(cache)}

    def query_cpu_clock(self) -> t.Tuple[t.Optional[int], t.Optional[int], t.Optional[int]]:
        """
        Get current, minimum and maximum clock frequency of the CPU in the system.
        """
        if not self.CPU_CLOCK:
            return None, None, None
        try:
            cpu_clock = psutil.cpu_freq()
        except FileNotFoundError:
            return None, None, None
        if cpu_clock is None:
            return None, None, None
        return cpu_clock.current, cpu_clock.min, cpu_clock.max

    def query_cpu_cores(self) -> t.Tuple[t.Optional[int], t.Optional[int]]:
        """
        Get number of logical and physical cores of the system's CPU.
        """
        if not self.CPU_CORES:
            return None, None
        return psutil.cpu_count(), psutil.cpu_count(logical=False)

    def _get_cache_size(self, level: int, cpuinfo_data: dict) -> t.Optional[int]:
        """
        Get CPU cache size in bytes at a given level.
        If no units are provided, assume source data is in KiB.
        """
        if self.OS == 'darwin' and level != 2:
            if not is_process_accessible(['sysctl']):
                print('[bold yellow]sysctl command is not accessible! Unable to fetch detailed L1, L3 cache size information.')
            else:
                cmd = (['sysctl', 'hw', '|', 'grep', f'l{level}'])
                result = subprocess.run(cmd, timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(result)
                print(dict(result))

        else:
            raw_value = str(cpuinfo_data.get(f'l{level}_data_cache_size', cpuinfo_data.get(f'l{level}_cache_size', None)))

        if raw_value is None:
            return None
        # KB, MB: "this practice frequently leads to confusion and is deprecated"
        # see https://en.wikipedia.org/wiki/JEDEC_memory_standards
        if raw_value.endswith('KB'):
            raw_value = raw_value[:-2] + 'KiB'
        elif raw_value.endswith('MB'):
            raw_value = raw_value[:-2] + 'MiB'
        ureg = pint.UnitRegistry()
        value = ureg(raw_value)
        if isinstance(value, int):
            return value * 1024
        print(f'L{level} cache size parsed by pint: {raw_value} -> {value}')
        value = value.to('bytes')
        return int(value.magnitude)

    @staticmethod
    def _get_cache_sizes(cpuinfo_data: dict) -> t.Mapping[int, t.Optional[int]]:
        """
        Bla
        """
        return {lvl: CpuInfo._get_cache_size(lvl, cpuinfo_data) for lvl in range(1, 4)}

    def print_cpu_info(self, cpu_info: dict) -> None:
        """
        Bla
        """
        # Prettify cache
        cpu_info['cache'] = cpu_info['cache'].replace('{', '').replace('}', '')
        column_names = ['Vendor ID', 'Hardware', 'Brand', 'Architecture', 'Logical Cores', 'Physical Cores', 'Clock', 'Minimal Clock', 'Maximal Clock', 'Cache']
        self.init_table(title='Central Processing Unit', column_names=column_names)
        self.table.add_row(*cpu_info.values())
        self.print_table()
