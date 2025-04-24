import sys
import collections

# Fix for Python 3.10+ where collections ABCs were moved to collections.abc
if sys.version_info >= (3, 10) and not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Mapping = collections.abc.Mapping
    collections.Iterable = collections.abc.Iterable
    collections.Iterator = collections.abc.Iterator
    collections.Sequence = collections.abc.Sequence
