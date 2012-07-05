# -*- coding: utf-8 -*-

__all__ = ['ask']

from .http import Request, RouteState
from ..utils.storage import VariableStorage


def ask(application, url, method='get', data=None,
        headers=None, additional_env=None, additional_data=None):
    env = VariableStorage(additional_env or {})
    #TODO: may be later process cookies separatly
    env.request = Request.blank(url, POST=data, headers=headers)
    env._route_state = RouteState(env.request)
    data = VariableStorage(additional_data or {})
    return application(env, data)
