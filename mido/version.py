from collections import namedtuple

VersionInfo = namedtuple('VersionInfo',
                         ['major', 'minor', 'micro', 'releaselevel', 'serial'])

def _make_version_info(version):
    version, releaselevel = version.split('-')
    major, minor, micro = map(int, version.split('.'))

    return VersionInfo(major, minor, micro, releaselevel, 0)

version = '1.2.0-alpha'
version_info = _make_version_info(version)
