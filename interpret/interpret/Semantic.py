from enum import Enum

from interpret.Decorators import check_int, check_bool, check_string, check_nil


class SymbolTable:

    def __init__(self):
        self.GlobalFrame = dict()
        self.LocalFrame = list()
        self.TemporaryFrame = None

    @staticmethod
    def Frame(arguments):
        frame, var = arguments[2].split('@')
        return frame, var

    def GetFrame(self, frame):
        if frame == "GF":
            return self.GlobalFrame
        elif frame == "LF":
            if len(self.LocalFrame) == 0:
                exit(55)
            return self.LocalFrame[-1]
        elif frame == "TF":
            return self.TemporaryFrame
        else:
            exit(33)

    def InsertIntoSymbolTable(self, arguments):
        frame, var = self.Frame(arguments[0])
        symbol_table = self.GetFrame(frame)
        symbol = Token(var)
        if symbol_table is None:
            exit(55)
        if var in symbol_table.keys():
            exit(54)
        symbol_table[var] = symbol
        return symbol_table

    def GetVarFromSymbTable(self, arguments):
        frame, var = self.Frame(arguments[0])
        symbolTable = self.GetFrame(frame)
        if symbolTable is None:
            exit(55)
        if var in symbolTable.keys():
            symbol = symbolTable[var]
            return symbol
        exit(54)

    def CreateFrame(self):
        self.TemporaryFrame = dict()

    def PushFrame(self):
        if self.TemporaryFrame is None:
            exit(55)
        self.LocalFrame.append(self.TemporaryFrame)
        self.TemporaryFrame = None

    def PopFrame(self):
        if len(self.LocalFrame) == 0:
            exit(55)
        self.TemporaryFrame = self.LocalFrame.pop()


class DataType(Enum):
    INT = 1,
    BOOL = 2,
    STRING = 3


class Token:

    def __init__(self, name, type_of_var=None, value=None):
        self.name = name
        self.type_of_var = type_of_var
        self.value = value

    def __eq__(self, other):
        return self.name == other.name

    def setTokenValue(self, valueToBeSet):
        if isinstance(valueToBeSet, Token):
            self.type_of_var = valueToBeSet.type_of_var
            self.value = valueToBeSet.value
        elif isinstance(valueToBeSet, bool):
            self.type_of_var = DataType.BOOL.name
            self.value = valueToBeSet
        elif isinstance(valueToBeSet, int):
            self.type_of_var = DataType.INT.name
            self.value = valueToBeSet
        elif isinstance(valueToBeSet, str):
            self.type_of_var = DataType.STRING.name
            self.value = valueToBeSet
        else:
            exit(52)


def checkType(value):
    if check_int(value):
        return int(value)
    elif check_bool(value):
        return value
    elif check_string(value):
        return value
    return False


def checkNumberOfArguments(Arguments, number):
    if len(Arguments) == number:
        return True
    exit(33)