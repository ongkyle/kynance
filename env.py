import json

from dotenv import load_dotenv
import os


def ensure_env_vars(vars):
    load_dotenv()
    for var in vars:
        try:
            ensure_env_var(var)
        except EnvVarNotFoundException as e:
            raise e


def ensure_env_var(var):
    val = os.getenv(var, default=None)
    if val is None:
        raise EnvVarNotFoundException(var)


def parse_env_var(var):
    try:
        var = json.loads(os.getenv(var))
    except json.decoder.JSONDecodeError as _:
        var = os.getenv(var)
    return var


class EnvVarNotFoundException(Exception):
    def __init__(self, var):
        self.var = var
        self.message = f"Error: {self.var} not found."
