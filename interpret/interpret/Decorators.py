import re
from functools import wraps


def move_operands(func):
    @wraps(func)
    def check(**kwargs):
        if len(kwargs["arg"][0]) > 3:
            return False
        elif check_var(kwargs["arg"][0][2]) and (
            check_int(kwargs["arg"][1][2])
            or check_string(kwargs["arg"][1][2])
            or check_bool(kwargs["arg"][1][2])
            or check_var(kwargs["arg"][1][2])
        ):
            return "VarSymb"
        return False

    return check


def move_types(func):
    @wraps(func)
    def check(**kwargs):
        if kwargs["arg"][0][1] == "var":
            if not check_var(kwargs["arg"][0][2]):
                return False

        for i in range(2):
            if kwargs["arg"][i][1] == "string":
                if not check_string(kwargs["arg"][i][2]):
                    return False
            elif kwargs["arg"][i][1] == "int":
                if not check_int(kwargs["arg"][i][2]):
                    return False
            elif kwargs["arg"][i][1] == "bool":
                if not check_bool(kwargs["arg"][i][2]):
                    return False
            elif kwargs["arg"][i][1] == "nil":
                if not check_nil(kwargs["arg"][i][2]):
                    return False
            elif kwargs["arg"][i][1] == "var":
                if not check_var(kwargs["arg"][i][2]):
                    return False
        return True

    return check


def no_operands(func):
    @wraps(func)
    def check(**kwargs):
        if len(kwargs["arg"]) == 0:
            return "NoOperands"
        return False

    return check


def check_int(digit):
    return re.match("^[-+]?[0-9]+", digit)


def check_string(string):  # TODO: poresit escape sekvence
    return re.match("^[a-z]*$", string)


def check_bool(boolean):
    return re.match("(false|true)", boolean)


def check_var(var):
    return re.match("(GF|LF|TF)@[a-z]+", var)


def check_nil(nil):
    return re.match("nil", nil)
