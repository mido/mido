from collections import namedtuple
import pkg_resources

VersionInfo = namedtuple('VersionInfo',
                         ['major', 'minor', 'micro', 'releaselevel', 'serial'])


def _make_version_info(version):
    if '-' in version:
        version, releaselevel = version.split('-')
    else:
        releaselevel = ''

    major, minor, micro = map(int, version.split('.'))

    return VersionInfo(major, minor, micro, releaselevel, 0)


version = pkg_resources.require("mido")[0].version
version_info = _make_version_info(version)
