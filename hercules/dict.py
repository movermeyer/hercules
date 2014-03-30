class KeyClobberError(KeyError):
    pass


class NoClobberDict(dict):
    '''An otherwise ordinary dict that complains if you
    try to overwrite any existing keys.
    '''
    KeyClobberError = KeyClobberError
    def __setitem__(self, key, val):
        if key in self:
            msg = "Can't overwrite key %r in %r"
            raise KeyClobberError(msg % (key, self))
        else:
            dict.__setitem__(self, key, val)

    def update(self, otherdict=None, **kwargs):
        if otherdict is not None:
            dupes = set(otherdict) & set(self)
            for dupe in dupes:
                if self[dupe] != otherdict[dupe]:
                    msg = "Can't overwrite keys %r in %r"
                    raise KeyClobberError(msg % (dupes, self))
        if kwargs:
            for dupe in dupes:
                if self[dupe] != otherdict[dupe]:
                    msg = "Can't overwrite keys %r in %r"
                    raise KeyClobberError(msg % (dupes, self))
        dict.update(self, otherdict or {}, **kwargs)



# -----------------------------------------------------------------------------
# Dict filter class.
# -----------------------------------------------------------------------------
class NonExistentHandler(object):
    '''Raise if someone tries a dunder query that isn't supported.
    '''


class DictFilterMixin(object):
    '''
    listy = [dict(a=1), dict(a=2), dict(a=3)]
    for dicty in DictFilter(listy).filter(a=1):
        print dicty

    '''
    def filter(self, **kwargs):
        '''Assumes all the dict's items are hashable.
        '''
        # So we don't return anything more than once.
        yielded = set()

        dunder = '__'
        filter_items = set()
        for k, v in kwargs.items():
            if dunder in k:
                k, op = k.split(dunder)
                try:
                    handler = getattr(self, 'handle__%s' % op)
                except AttributeError:
                    msg = '%s has no %r method to handle operator %r.'
                    raise NonExistentHandler(msg % (self, handler, op))
                for dicty in self:
                    if handler(k, v, dicty):
                        dicty_id = id(dicty)
                        if dicty_id not in yielded:
                            yield dicty
                            yielded.add(dicty_id)
            else:
                filter_items.add((k, v))

        for dicty in self:
            dicty_items = set(dicty.items())
            if filter_items.issubset(dicty_items):
                yield dicty

    def handle__in(self, key, value, dicty):
        dicty_val = dicty[key]
        return dicty_val in value

    def handle__ne(self, key, value, dicty):
        dicty_val = dicty[key]
        return dicty_val != value


class IteratorDictFilter(IteratorWrapperBase, DictFilterMixin):
    '''A dict filter that wraps an iterator.
    '''
    pass


def iterdict_filter(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        result = f(*args, **kwargs)
        return IteratorDictFilter(result)
    return wrapped
