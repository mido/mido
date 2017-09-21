from collections import namedtuple
from .__about__ import __version__

VersionInfo = namedtuple('VersionInfo',
                         ['major', 'minor', 'micro', 'releaselevel', 'serial'])


def _make_version_info(version):
    if '-' in version:
        version, releaselevel = version.split('-')
    else:
        releaselevel = ''

    major, minor, micro = map(int, version.split('.'))

    return VersionInfo(major, minor, micro, releaselevel, 0)


version_info = _make_version_info(__version__)
