from jinja2.environment import Environment
from jinja2.ext import Extension

def is_truthy(v):
    return v.lower() in [ 'true', '1', 'yes', 'y' ]

class FilterExtension(Extension):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        environment.tests["truthy"] = is_truthy
