import os
import contextlib


@contextlib.contextmanager
def cd(path):
    '''Creates the path if it doesn't exist'''
    old_dir = os.getcwd()
    try:
        os.makedirs(path)
    except OSError:
        pass
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


class SetDefault(object):
    '''Context manager like getattr, but yields a default value,
    and sets on the instance on exit:

    with SetDefault(obj, attrname, []) as attr:
        attr.append('something')
    print obj.something
    '''
    def __init__(self, obj, attr, default_val):
        self.obj = obj
        self.attr = attr
        self.default_val = default_val

    def __enter__(self):
        val = getattr(self.obj, self.attr, self.default_val)
        self.val = val
        return val

    def __exit__(self, exc_type, exc_value, traceback):
        setattr(self.obj, self.attr, self.val)


class DictSetDefault(object):
    '''Context manager like getattr, but yields a default value,
    and sets on the instance on exit:

    with DictSetDefault(somedict, key, []) as attr:
        attr.append('something')
    print obj['something']
    '''
    def __init__(self, obj, key, default_val):
        self.obj = obj
        self.key = key
        self.default_val = default_val

    def __enter__(self):
        val = self.obj.get(self.key, self.default_val)
        self.val = val
        return val

    def __exit__(self, exc_type, exc_value, traceback):
        self.obj[self.key] = self.val

