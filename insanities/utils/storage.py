# -*- coding: utf-8 -*-

class VariableStorage(dict):

    def as_dict(self):
        # for compatibility
        return dict(self)

    def __getattr__(self, k):
        return self[k]

    def __delattr__(self, k):
        del self[k]

    def __setattr__(self, k, v):
        self[k] = v

    def __repr__(self):
        return repr(self._dict_)

    def __call__(self, **kwargs):
        self.update(**kwargs)
        return self


