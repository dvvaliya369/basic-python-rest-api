"""
Simple mock implementations of flask-restx for demonstration when the package is not available
"""

import functools
from flask import Blueprint

class MockApi:
    def __init__(self, blueprint, **kwargs):
        self.blueprint = blueprint
        self.models = {}
        
    def add_namespace(self, namespace):
        pass
        
    def model(self, name, fields_dict):
        self.models[name] = fields_dict
        return fields_dict

class MockResource:
    pass

class MockNamespace:
    def __init__(self, name, **kwargs):
        self.name = name
        
    def route(self, path):
        def decorator(cls):
            return cls
        return decorator
        
    def doc(self, description):
        def decorator(func):
            return func
        return decorator
        
    def expect(self, model):
        def decorator(func):
            return func
        return decorator
        
    def marshal_with(self, model, **kwargs):
        def decorator(func):
            return func
        return decorator
        
    def param(self, name, description):
        def decorator(cls):
            return cls
        return decorator

class MockFields:
    @staticmethod
    def String(**kwargs):
        return {'type': 'string', **kwargs}
        
    @staticmethod
    def Boolean(**kwargs):
        return {'type': 'boolean', **kwargs}
        
    @staticmethod
    def DateTime(**kwargs):
        return {'type': 'string', 'format': 'date-time', **kwargs}
        
    @staticmethod
    def Nested(model, **kwargs):
        return {'type': 'object', **kwargs}
        
    @staticmethod
    def Raw(**kwargs):
        return {'type': 'object', **kwargs}

class MockParser:
    def __init__(self):
        self.arguments = []
        
    def add_argument(self, name, **kwargs):
        self.arguments.append({'name': name, **kwargs})
        return self
