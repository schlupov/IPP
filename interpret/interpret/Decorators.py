import re
from functools import wraps


def move_operands(func):
    @wraps(func)
    def check(**kwargs):
        if len(kwargs["arg"]) > 2:
            return False
        elif check_var(kwargs["arg"][0][2]) and (
            check_int(kwargs["arg"][1][2])
            or check_string(kwargs["arg"][1][2])
            or check_bool(kwargs["arg"][1][2])
            or check_var(kwargs["arg"][1][2])
            or check_nil(kwargs["arg"][1][2])
        ):
            return "MoveOperation"
        return False

    return check


def arithmetic_operation(func):
    @wraps(func)
    def check(**kwargs):
        if len(kwargs["arg"]) > 3:
            return False
        elif kwargs["arg"][0][1] == "var" and check_var(kwargs["arg"][0][2]):
            return "Arithmetic"
        return False

    return check


def int2char_var(func):
    @wraps(func)
    def check(**kwargs):
        if len(kwargs["arg"]) > 2:
            return False
        elif kwargs["arg"][0][1] == "var" and check_var(kwargs["arg"][0][2]):
            return "Var"
        return False

    return check


def var(func):
    @wraps(func)
    def check(**kwargs):
        if len(kwargs["arg"]) > 1:
            return False
        elif kwargs["arg"][0][1] == "var" and check_var(kwargs["arg"][0][2]):
            return "Var"
        return False

    return check


def label(func):
    @wraps(func)
    def check(**kwargs):
        if kwargs["arg"][0][1] == "label" and check_label(kwargs["arg"][0][2]):
            return "Label"
        return False

    return check


def symb(func):
    @wraps(func)
    def check(**kwargs):
        if kwargs["arg"][0][1] == "var":
            if not check_var(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "string":
            if not check_string(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "int":
            if not check_int(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "bool":
            if not check_bool(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "nil":
            if not check_nil(kwargs["arg"][0][2]):
                return False
        return True

    return check


def str2int_symb(func):
    @wraps(func)
    def check(**kwargs):
        if kwargs["arg"][1] == "string":
            if not check_string(kwargs["arg"][2]):
                return False
        return "Symb"

    return check


def arithmetic_operation_symb(func):
    @wraps(func)
    def check(**kwargs):
        if kwargs["arg"][1] == "int":
            if not check_int(kwargs["arg"][2]):
                return False
        return "Symb"

    return check


def relational_operation_symb(func):
    @wraps(func)
    def check(**kwargs):
        if kwargs["arg"][1] == "string":
            if not check_string(kwargs["arg"][2]):
                return False
        elif kwargs["arg"][1] == "int":
            if not check_int(kwargs["arg"][2]):
                return False
        elif kwargs["arg"][1] == "bool":
            if not check_bool(kwargs["arg"][2]):
                return False
        return "Symb"

    return check


def symb_types(func):
    @wraps(func)
    def check(**kwargs):
        if kwargs["arg"][0][1] == "var":
            if not check_var(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "string":
            if not check_string(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "int":
            if not check_int(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "bool":
            if not check_bool(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "nil":
            if not check_nil(kwargs["arg"][0][2]):
                return False
        elif kwargs["arg"][0][1] == "var":
            if not check_var(kwargs["arg"][0][2]):
                return False
        return True

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
            return "OperationWithNoOperands"
        return False

    return check


def check_int(digit):
    return re.match(r"^[-+]?[0-9]+", digit)


def check_string(string):
    return re.match(r"^([a-zA-Z\u0021\u0022\u0024-\u005B\u005D-\uFFFF]|(\u005C[0-9]{3})*)*$", string)


def check_bool(boolean):
    return re.match("(false|true)", boolean)


def check_label(label):
    return re.match(r"^([a-zA-Z]|-|[_$&%*])([a-zA-Z]|-|[_$&%*]|[0-9]+)+$", label)


def check_var(var):
    return re.match(r"^(GF|LF|TF)@([a-zA-Z]|-|[_$&%*])([a-zA-Z]|-|[_$&%*]|[0-9]+)+$", var)


def check_nil(nil):
    return re.match("nil", nil)

