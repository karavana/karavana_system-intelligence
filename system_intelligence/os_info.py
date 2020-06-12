"""Functions to query the operating system."""

import platform


def query_os():
    """Get information about OS."""
    # distro = distro.linux_distribution(full_distribution_name=False)
    system = platform.platform()  # + ' ' + ' '.join(str(_) for _ in distro)}
    return system
