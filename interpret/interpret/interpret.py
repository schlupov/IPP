import argparse
import re
import sys

from Decorators import (
    move_types,
    var,
    symb,
    label,
    arithmetic_operation_symb,
    relational_operation_symb,
    str2int_symb,
    read_type,
    check_int,
    check_string,
    boolean_operation_symb,
    check_label,
    check_bool,
    check_nil,
    check_var,
    check_type
)
from KeyWords import KeyWords
from Semantic import SymbolTable, checkType, checkNumberOfArguments
from xml_reader import XML
from Semantic import Token


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class InstuctionPointer:
    def __init__(self):
        self.ip = 0
        self.labels = dict()
        self.callStack = Stack()

    def NewLabel(self, Label):
        if Label in self.labels:
            exit(52)
        self.labels[Label] = self.ip

    def GoToLabel(self, Label):
        if Label not in self.labels:
            exit(52)
        self.callStack.push(self.ip)
        self.ip = self.labels[Label]

    def Return(self):
        if self.callStack.isEmpty():
            exit(56)
        self.ip = self.callStack.pop()

    def ResetPointer(self):
        self.ip = 0
        self.callStack = Stack()


class InstructionBase(XML):
    classSymbolTable = None
    stack = Stack()
    instructionPointer = InstuctionPointer()
    read_op = False

    def __init__(self, read_file=None, xml_file=None):
        self.read_file = read_file
        self.xml_file = xml_file
        super().__init__(xml_file)

    @classmethod
    def SetSymbolTableForAllInstructions(cls, symbol_tab):
        cls.classSymbolTable = symbol_tab

    def GetInstruction(self):
        xml = self.GetElementsFromXml()
        if self.instructionPointer.ip < len(xml):
            ins = xml[self.instructionPointer.ip]
            self.instructionPointer.ip += 1
            return ins
        return None

    def FindAllLabels(self):
        instruction = self.GetInstruction()
        while instruction is not None:
            if instruction.opcode == KeyWords.LABEL.name:
                checkNumberOfArguments(instruction.arguments, 1)
                LabelOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()
            instruction = self.GetInstruction()
        self.instructionPointer.ResetPointer()

    def ChooseOperationCodeFromXml(self):
        table = SymbolTable()
        instruction = self.GetInstruction()

        while instruction is not None:
            self.CheckInstructionInXml(instruction)
            if instruction.opcode == KeyWords.MOVE.name:
                checkNumberOfArguments(instruction.arguments, 2)
                MoveOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif (
                    instruction.opcode == KeyWords.CREATEFRAME.name
                or instruction.opcode == KeyWords.PUSHFRAME.name
                or instruction.opcode == KeyWords.POPFRAME.name
            ):
                checkNumberOfArguments(instruction.arguments, 0)
                changedSymbolTable = OperationWithNoOperands(
                    instruction.opcode, instruction.arguments, self._xml_file, table
                ).CheckOperationAndExecute()
                self.SetSymbolTableForAllInstructions(changedSymbolTable)
            elif instruction.opcode == KeyWords.DEFVAR.name:
                checkNumberOfArguments(instruction.arguments, 1)
                changedSymbolTable = DefvarOperation(
                    instruction.opcode, instruction.arguments, self._xml_file, table
                ).CheckOperationAndExecute()
                self.SetSymbolTableForAllInstructions(changedSymbolTable)
            elif instruction.opcode == KeyWords.PUSHS.name:
                checkNumberOfArguments(instruction.arguments, 1)
                PushsOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.POPS.name:
                checkNumberOfArguments(instruction.arguments, 1)
                PopsOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.CALL.name:
                checkNumberOfArguments(instruction.arguments, 1)
                CallOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()
            elif instruction.opcode == KeyWords.RETURN.name:
                checkNumberOfArguments(instruction.arguments, 0)
                ReturnOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()
            elif (
                instruction.opcode == KeyWords.ADD.name
                or instruction.opcode == KeyWords.SUB.name
                or instruction.opcode == KeyWords.MUL.name
                or instruction.opcode == KeyWords.IDIV.name
            ):
                checkNumberOfArguments(instruction.arguments, 3)
                ArithmeticOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif (
                instruction.opcode == KeyWords.LT.name
                or instruction.opcode == KeyWords.GT.name
                or instruction.opcode == KeyWords.EQ.name
            ):
                checkNumberOfArguments(instruction.arguments, 3)
                RelationalOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif (
                instruction.opcode == KeyWords.AND.name
                or instruction.opcode == KeyWords.OR.name
                or instruction.opcode == KeyWords.NOT.name
            ):
                if instruction.opcode != KeyWords.NOT.name:
                    checkNumberOfArguments(instruction.arguments, 3)
                else:
                    checkNumberOfArguments(instruction.arguments, 2)
                BooleanOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.INT2CHAR.name:
                checkNumberOfArguments(instruction.arguments, 2)
                IntToCharOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.STRI2INT.name:
                checkNumberOfArguments(instruction.arguments, 3)
                StrToIntOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.WRITE.name:
                checkNumberOfArguments(instruction.arguments, 1)
                WriteOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.CONCAT.name:
                checkNumberOfArguments(instruction.arguments, 3)
                ConcatOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.READ.name:
                checkNumberOfArguments(instruction.arguments, 2)
                ReadOperation(instruction.opcode, instruction.arguments, self.xml_file, table, self.read_file).CheckOperation()
            elif instruction.opcode == KeyWords.STRLEN.name:
                checkNumberOfArguments(instruction.arguments, 2)
                StrlenOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.GETCHAR.name:
                checkNumberOfArguments(instruction.arguments, 3)
                GetCharOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.SETCHAR.name:
                checkNumberOfArguments(instruction.arguments, 3)
                SetCharOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.TYPE.name:
                checkNumberOfArguments(instruction.arguments, 2)
                TypeOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.JUMP.name:
                checkNumberOfArguments(instruction.arguments, 1)
                JumpOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()
            elif (
                instruction.opcode == KeyWords.JUMPIFEQ.name
                or instruction.opcode == KeyWords.JUMPIFNEQ.name
            ):
                checkNumberOfArguments(instruction.arguments, 3)
                JumpIfEqOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.EXIT.name:
                checkNumberOfArguments(instruction.arguments, 1)
                ExitOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.DPRINT.name:
                checkNumberOfArguments(instruction.arguments, 1)
                DPrintOperation(instruction.opcode, instruction.arguments, self._xml_file, table).CheckOperation()
            elif instruction.opcode == KeyWords.BREAK.name:
                checkNumberOfArguments(instruction.arguments, 0)
                BreakOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()
            instruction = self.GetInstruction()

    def CheckInstructionInXml(self, instruction):
        if (
            not self.IsKeyword(instruction.opcode)
            or re.match("^[0-9]+$", instruction.order) is None
        ):
            exit(32)

    @staticmethod
    def IsKeyword(opcode):
        for keyword in KeyWords:
            if keyword.name == opcode:
                return keyword.name

    def InitSymbolTable(self, table):
        self.SetSymbolTableForAllInstructions(table)
        return self.classSymbolTable

    @staticmethod
    def check_syntax(arg, integer=False, string=False, boolean=False, nil=False, var=False, type=False, label=False):
        if arg[1] == "int" and integer:
            if check_int(arg[2]) is not None:
                return True
        elif arg[1] == "string" and string:
            if check_string(arg[2]) is not None:
                return True
        elif arg[1] == "bool" and boolean:
            if check_bool(arg[2]) is not None:
                return True
        elif arg[1] == "nil" and nil:
            if check_nil(arg[2]) is not None:
                return True
        elif arg[1] == "var" and var:
            if check_var(arg[2]) is not None:
                return True
        elif arg[1] == "type" and type:
            if check_type(arg[2]) is not None:
                return True
        elif arg[1] == "label" and label:
            if check_label(arg[2]) is not None:
                return True
        exit(32)


class MoveOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @move_types
    def AreOperandsTypeOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        if not (self.AreOperandsTypeOk(arg=self.Arguments)):
            exit(32)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbolFromSymbTable = symbolTable.GetVarFromSymbTable(self.Arguments)
        token = Token(symbolFromSymbTable.name, self.Arguments[1][1], self.Arguments[1][2])
        symbolFromSymbTable.setTokenValue(token)
        return symbolTable


class PushsOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @symb
    def IsOperandTypeOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsOperandTypeOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        self.Execute(symbolTable)

    def Execute(self, symbolTable):
        if self.Arguments[0][1] == "var":
            frame = symbolTable.GetFrame(self.Arguments[0][2].split('@')[0])
            if frame is None:
                exit(55)
            symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
            if symbol.value is not None:
                InstructionBase.stack.push(symbol.value)
            else:
                exit(56)
        else:
            InstructionBase.stack.push(self.Arguments[0][2])


class PopsOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @var
    def IsOperandOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        if not self.IsOperandOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        if not InstructionBase.stack.isEmpty():
            variabelFromStack = InstructionBase.stack.pop()
            variableFromXml = self.Arguments[0][2].split("@")[1]
            symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
            token = Token(variableFromXml, self.Arguments[0][1].upper(), variabelFromStack)
            symbol.setTokenValue(token)
            return symbolTable
        exit(56)


class OperationWithNoOperands(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    def CheckOperationAndExecute(self):
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        if self.Opcode == KeyWords.CREATEFRAME.name:
            symbolTable.CreateFrame()
        elif self.Opcode == KeyWords.PUSHFRAME.name:
            symbolTable.PushFrame()
        elif self.Opcode == KeyWords.POPFRAME.name:
            symbolTable.PopFrame()
        return symbolTable


class DefvarOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @var
    def AreOperandsOk(arg):
        return arg

    def CheckOperationAndExecute(self):
        self.check_syntax(self.Arguments[0], var=True)
        if not self.AreOperandsOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbolTable.InsertIntoSymbolTable(self.Arguments)
        return symbolTable


class ArithmeticOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @var
    def AreOperandsOk(arg):
        return arg

    @staticmethod
    @arithmetic_operation_symb
    def AreOperandsTypeOk(arg):
        return arg

    def CheckOperation(self):
        if not self.AreOperandsOk(arg=self.Arguments):
            exit(32)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        self.check_syntax(self.Arguments[2], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.AreOperandsTypeOk(arg=self.Arguments[1]) or not self.AreOperandsTypeOk(arg=self.Arguments[2]):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        if self.Arguments[1][1] == "var" and self.Arguments[2][1] == "var":
            op1 = checkType(self.Arguments[1][2])
            op2 = checkType(self.Arguments[2][2])
            op1 = symbolTable.GetOperandFromSymbolTable(op1)
            op2 = symbolTable.GetOperandFromSymbolTable(op2)
            if op1.type_of_var != "int" or op2.type_of_var != "int":
                exit(53)
            op1 = int(op1.value)
            op2 = int(op2.value)
        elif self.Arguments[1][1] == "int" and self.Arguments[2][1] == "int":
            op1 = int(self.Arguments[1][2])
            op2 = int(self.Arguments[2][2])
        elif (self.Arguments[1][1] == "var" and self.Arguments[2][1] == "int") \
                or (self.Arguments[1][1] == "int" and self.Arguments[2][1] == "var"):
            if self.Arguments[1][1] == "var":
                op1 = checkType(self.Arguments[1][2])
                op1 = symbolTable.GetOperandFromSymbolTable(op1)
                op1 = int(op1.value)
                op2 = int(self.Arguments[2][2])
            else:
                op2 = checkType(self.Arguments[1][2])
                op2 = symbolTable.GetOperandFromSymbolTable(op2)
                op2 = int(op2.value)
                op1 = int(self.Arguments[2][2])
        else:
            exit(53)

        if self.Opcode == KeyWords.ADD.name:
            symbol.setTokenValue(op1 + op2)
        elif self.Opcode == KeyWords.SUB.name:
            symbol.setTokenValue(op1 - op2)
        elif self.Opcode == KeyWords.MUL.name:
            symbol.setTokenValue(op1 * op2)
        elif self.Opcode == KeyWords.IDIV.name:
            try:
                symbol.setTokenValue(int(op1 // op2))
            except ZeroDivisionError:
                exit(57)
        return symbolTable


class RelationalOperation(InstructionBase):
    nil_return = None

    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @var
    def AreOperandsOk(arg):
        return arg

    @staticmethod
    @relational_operation_symb
    def AreOperandsTypeOk(arg):
        return arg

    def CheckOperation(self):
        if not self.AreOperandsOk(arg=self.Arguments):
            exit(32)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        self.check_syntax(self.Arguments[2], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.AreOperandsTypeOk(arg=self.Arguments[1]) or not self.AreOperandsTypeOk(arg=self.Arguments[2]):
            exit(53)
        if (self.Arguments[1][1] == "nil" or self.Arguments[2][1] == "nil") and self.Opcode != KeyWords.EQ.name:
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    @staticmethod
    def convertType(arg):
        if arg[1] == "int":
            return int(arg[2])
        elif arg[1] == "string":
            return arg[2]
        elif arg[1] == "nil":
            return arg[2]
        elif arg[1] == "bool":
            if arg[2] == "true":
                return 1
            elif arg[2] == "false":
                return 0
            return arg[2]

    def extractValue(self, symbolTable):
        if self.Arguments[0][1] == "var":
            var = symbolTable.GetVarFromSymbTable(self.Arguments)
        else:
            exit(53)

        if self.Arguments[1][1] == "var" and self.Arguments[2][1] == "var":
            op1 = symbolTable.GetOperandFromSymbolTable(self.Arguments[1][2])
            op2 = symbolTable.GetOperandFromSymbolTable(self.Arguments[2][2])
            if op1.type_of_var != op2.type_of_var:
                if (op1.type_of_var == "nil" or op2.type_of_var == "nil") and self.Opcode == KeyWords.EQ.name:
                    RelationalOperation.nil_return = False
                else:
                    exit(53)
            op1 = op1.value
            op2 = op2.value
        elif self.Arguments[1][1] == "var":
            op1 = symbolTable.GetOperandFromSymbolTable(self.Arguments[1][2])
            op2 = self.convertType(self.Arguments[2])
            if op1.type_of_var.lower() != self.Arguments[2][1] and self.Opcode != KeyWords.EQ.name:
                exit(53)
            op1 = op1.value
        elif self.Arguments[2][1] == "var":
            op1 = self.convertType(self.Arguments[1])
            op2 = symbolTable.GetOperandFromSymbolTable(self.Arguments[2][2])
            if self.Arguments[1][1] != op2.type_of_var.lower() and self.Opcode != KeyWords.EQ.name:
                exit(53)
            op2 = op2.value
        else:
            op1 = self.convertType(self.Arguments[1])
            op2 = self.convertType(self.Arguments[2])
            if self.Arguments[1][1] != self.Arguments[2][1] and self.Opcode != KeyWords.EQ.name:
                exit(53)
        return op1, op2, var

    def Execute(self, symbolTable):
        op1, op2, var = self.extractValue(symbolTable)

        if type(op1) != type(op2):
            if (op1 == "nil" or op2 == "nil") and self.Opcode == KeyWords.EQ.name:
                RelationalOperation.nil_return = False
            else:
                exit(53)

        if self.Opcode == KeyWords.LT.name:
            var.setTokenValue(op1 < op2)
        elif self.Opcode == KeyWords.GT.name:
            var.setTokenValue(op1 > op2)
        elif self.Opcode == KeyWords.EQ.name:
            if RelationalOperation.nil_return:
                var.setTokenValue(False)
            else:
                var.setTokenValue(op1 == op2)
        return symbolTable


class BooleanOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @var
    def AreOperandsOk(arg):
        return arg

    @staticmethod
    @boolean_operation_symb
    def AreOperandsTypeOk(arg):
        return arg

    @staticmethod
    def convertType(arg):
        if arg[1] == "bool":
            if arg[2] == "true":
                return 1
            elif arg[2] == "false":
                return 0
        else:
            exit(53)

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        self.check_syntax(self.Arguments[2], var=True, integer=True, string=True, boolean=True, nil=True)
        if self.Opcode == KeyWords.NOT.name \
                and not self.AreOperandsOk(arg=self.Arguments) \
                or not self.AreOperandsTypeOk(arg=self.Arguments[1]):
            exit(53)
        elif self.Opcode != KeyWords.NOT.name \
                and not self.AreOperandsOk(arg=self.Arguments) \
                or not self.AreOperandsTypeOk(arg=self.Arguments[1]) \
                or not self.AreOperandsTypeOk(arg=self.Arguments[2]):
                exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def extractValue(self, symbolTable):
        if self.Arguments[0][1] == "var":
            var = symbolTable.GetVarFromSymbTable(self.Arguments)
        else:
            exit(53)

        if self.Arguments[1][1] == "var" and self.Arguments[2][1] == "var":
            op1 = symbolTable.GetOperandFromSymbolTable(self.Arguments[1][2])
            op2 = symbolTable.GetOperandFromSymbolTable(self.Arguments[2][2])
            if op1.type_of_var != "bool" or op2.type_of_var != "bool":
                exit(53)
            op1 = op1.value
            op2 = op2.value
        elif self.Arguments[1][1] == "var":
            op1 = symbolTable.GetOperandFromSymbolTable(self.Arguments[1][2])
            if op1.type_of_var != "bool":
                exit(53)
            op1 = op1.value
            op2 = self.convertType(self.Arguments[2])
        elif self.Arguments[2][1] == "var":
            op1 = self.convertType(self.Arguments[1])
            op2 = symbolTable.GetOperandFromSymbolTable(self.Arguments[2][2])
            if op2.type_of_var != "bool":
                exit(53)
            op2 = op2.value
        else:
            op1 = self.convertType(self.Arguments[1])
            op2 = self.convertType(self.Arguments[2])
        return op1, op2, var

    def Execute(self, symbolTable):
        if self.Opcode != KeyWords.NOT.name:
            op1, op2, var = self.extractValue(symbolTable)

        if self.Opcode == KeyWords.NOT.name:
            if self.Arguments[0][1] == "var":
                var = symbolTable.GetVarFromSymbTable(self.Arguments)
            else:
                exit(53)

            if self.Arguments[1][1] == "bool":
                op1 = self.Arguments[1][2]
            elif self.Arguments[1][1] == "var":
                op1 = symbolTable.GetOperandFromSymbolTable(self.Arguments[1][2])
                if op1.type_of_var != "bool":
                    exit(53)
                op1 = op1.value
            else:
                exit(53)

        if self.Opcode == KeyWords.AND.name:
            if op1 == 'false' and op2 == 'true':
                var.setTokenValue('false')
            else:
                var.setTokenValue(op1 and op2)
        elif self.Opcode == KeyWords.OR.name:
            if op1 == 'false' and op2 == 'true':
                var.setTokenValue('true')
            else:
                var.setTokenValue(op1 or op2)
        elif self.Opcode == KeyWords.NOT.name:
            if op1 == "true":
                op1 = False
            else:
                op1 = True
            var.setTokenValue(str(op1).lower())
        return symbolTable


class IntToCharOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @arithmetic_operation_symb
    def IsSymbOk(arg):
        return arg

    @staticmethod
    @var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsSymbOk(arg=self.Arguments[1]) or not self.IsVarOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        op = checkType(self.Arguments[1][2])
        try:
            char = chr(op)
        except ValueError:
            exit(58)
        symbol.setTokenValue(char)
        return symbolTable


class StrToIntOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @arithmetic_operation_symb
    def IsSymb2Ok(arg):
        return arg

    @staticmethod
    @str2int_symb
    def IsSymb1Ok(arg):
        return arg

    @staticmethod
    @var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        self.check_syntax(self.Arguments[2], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsSymb2Ok(arg=self.Arguments[2]) or not self.IsSymb1Ok(arg=self.Arguments[1]) \
                or not self.IsVarOk(arg=self.Arguments):
                exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        op1 = checkType(self.Arguments[1][2])
        op2 = checkType(self.Arguments[2][2])
        try:
            char_ord = ord(op1[op2])
        except IndexError:
            exit(58)
        symbol.setTokenValue(char_ord)
        return symbolTable


class ReadOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table, read_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, read_file, xml_file)

    @staticmethod
    @read_type
    def IsTypeOk(arg):
        return arg

    @staticmethod
    @var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], type=True)
        if not self.IsTypeOk(arg=self.Arguments[1] or not self.IsVarOk(arg=self.Arguments)):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        if self.read_file is None:
            inputData = input()
        else:
            inputData = open(self.read_file, 'r')
            inputData = str(inputData.readline())

        if self.Arguments[1][2] == "bool":
            if inputData.lower() == "true":
                token = Token(symbol.name, "bool", inputData.lower())
            else:
                token = Token(symbol.name, "bool", "false")
            symbol.setTokenValue(token)
        elif self.Arguments[1][2] == "int":
            if check_int(inputData):
                token = Token(symbol.name, "int", inputData)
            else:
                token = Token(symbol.name, "int", "0")
            symbol.setTokenValue(token)
        elif self.Arguments[1][2] == "string":
            if check_string(inputData):
                token = Token(symbol.name, "string", inputData)
            else:
                token = Token(symbol.name, "string", "")
            symbol.setTokenValue(token)
        InstructionBase.read_op = True
        return symbolTable


class WriteOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @symb
    def IsOperandOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsOperandOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        self.Execute(symbolTable)

    def Execute(self, symbolTable):
        if self.Arguments[0][1] == "var":
            symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
            if symbol.type_of_var == "var":
                op = symbolTable.GetOperandFromSymbolTable(symbol.value)
                op = op.value
            else:
                op = symbol.value
        else:
            op = checkType(self.Arguments[0][2])

        if isinstance(op, bool):
            if op:
                op = "true"
            else:
                op = "false"
        elif isinstance(op, str):
            if not InstructionBase.read_op:
                op = self.CheckEscape(op)

        if op is not None:
            print(op, end="")
        else:
            exit(56)

    @staticmethod
    def CheckEscape(s):
        s = re.sub(r"\x5c([0-9][0-9][0-9])", lambda w: chr(int(w.group(1))), s)
        return s


class ConcatOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @str2int_symb
    def IsSymbOk(arg):
        return arg

    @staticmethod
    @var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        self.check_syntax(self.Arguments[2], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsSymbOk(arg=self.Arguments[2]) \
                or not self.IsSymbOk(arg=self.Arguments[1]) \
                or not self.IsVarOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        if self.Arguments[1][1] == "var" and self.Arguments[2][1] == "var":
            symbol1 = symbolTable.FindInSymbTable(self.Arguments[1])
            symbol2 = symbolTable.FindInSymbTable(self.Arguments[2])
            if symbol1.type_of_var != "string" or symbol2.type_of_var != "string":
                if symbol1.type_of_var is None or symbol2.type_of_var is None:
                    exit(56)
                exit(53)
            symbol2 = symbol2.value
            symbol1 = symbol1.value
        elif self.Arguments[1][1] == "var" and self.Arguments[2][1] == "string":
            symbol1 = symbolTable.FindInSymbTable(self.Arguments[1])
            symbol2 = self.Arguments[2][2]
            if symbol1.type_of_var != "string":
                if symbol1.type_of_var is None:
                    exit(56)
                exit(53)
            symbol1 = symbol1.value
        elif self.Arguments[1][1] == "string" and self.Arguments[2][1] == "var":
            symbol1 = self.Arguments[1][2]
            symbol2 = symbolTable.FindInSymbTable(self.Arguments[2])
            if symbol2.type_of_var != "string":
                if symbol2.type_of_var is None:
                    exit(56)
                exit(53)
            symbol2 = symbol2.value
        elif self.Arguments[1][1] == "string" and self.Arguments[2][1] == "string":
            symbol1 = self.Arguments[1][2]
            symbol2 = self.Arguments[2][2]
        else:
            exit(53)
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        symbol.setTokenValue(symbol1 + symbol2)
        return symbolTable


class StrlenOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @str2int_symb
    def IsSymbOk(arg):
        return arg

    @staticmethod
    @var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsSymbOk(arg=self.Arguments[1]) or not self.IsVarOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        if self.Arguments[1][1] == "var":
            symbol = symbolTable.FindInSymbTable(self.Arguments[1])
            op = symbol.value
            if not InstructionBase.read_op:
                op = self.CheckEscape(op)
            if symbol.type_of_var != "string":
                if symbol.type_of_var is None:
                    exit(56)
                exit(53)
        elif self.Arguments[1][1] == "string":
            op = self.Arguments[1][2]
            if not InstructionBase.read_op:
                op = self.CheckEscape(op)
        else:
            exit(53)
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        try:
            symbol.setTokenValue(len(op))
        except TypeError:
            exit(56)
        return symbolTable

    @staticmethod
    def CheckEscape(s):
        s = re.sub(r"\x5c([0-9][0-9][0-9])", lambda w: chr(int(w.group(1))), s)
        return s


class GetCharOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @arithmetic_operation_symb
    def IsSymb2Ok(arg):
        return arg

    @staticmethod
    @str2int_symb
    def IsSymb1Ok(arg):
        return arg

    @staticmethod
    @var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        self.check_syntax(self.Arguments[2], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsSymb2Ok(arg=self.Arguments[2]) \
                or not self.IsSymb1Ok(arg=self.Arguments[1]) \
                or not self.IsVarOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        op1 = checkType(self.Arguments[1][2])
        op2 = checkType(self.Arguments[2][2])
        try:
            char_ord = op1[op2]
        except IndexError:
            exit(58)
        symbol.setTokenValue(char_ord)
        return symbolTable


class SetCharOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @arithmetic_operation_symb
    def IsSymb1Ok(arg):
        return arg

    @staticmethod
    @str2int_symb
    def IsSymb2Ok(arg):
        return arg

    @staticmethod
    @var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        self.check_syntax(self.Arguments[2], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsSymb2Ok(arg=self.Arguments[2]) \
                or not self.IsSymb1Ok(arg=self.Arguments[1]) \
                or not self.IsVarOk(arg=self.Arguments):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        op1 = checkType(self.Arguments[1][2])
        op2 = checkType(self.Arguments[2][2])
        try:
            newsymbol = self.change_char(symbol.__dict__["value"], op1, op2)
        except IndexError:
            exit(58)
        symbol.setTokenValue(newsymbol)
        return symbolTable

    @staticmethod
    def change_char(s, p, r):
        return s[:p] + r + s[p + 1:]


class TypeOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @var
    def IsVarOk(arg):
        return arg

    @staticmethod
    @relational_operation_symb
    def IsSymbOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsVarOk(arg=self.Arguments) or not self.IsSymbOk(arg=self.Arguments[1]):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        if self.Arguments[1][1] == "var":
            symbol2 = symbolTable.FindInSymbTable(self.Arguments[1])
            if symbol2.__dict__["value"] is not None:
                op = symbol2.__dict__["type_of_var"].lower()
            else:
                op = ""
        else:
            op = self.Arguments[1][1]
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)

        try:
            symbol.setTokenValue(op)
        except TypeError:
            exit(53)
        return symbolTable


class LabelOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @label
    def IsLabelOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], label=True)
        if not self.IsLabelOk(arg=self.Arguments):
            exit(53)
        self.Execute()

    def Execute(self):
        self.instructionPointer.NewLabel(self.Arguments[0][2])


class JumpOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @label
    def IsLabelOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], label=True)
        if not self.IsLabelOk(arg=self.Arguments):
            exit(53)
        self.Execute()

    def Execute(self):
        self.instructionPointer.GoToLabel(self.Arguments[0][2])


class JumpIfEqOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @relational_operation_symb
    def IsSymbolTypeOk(arg):
        return arg

    @staticmethod
    @label
    def IsLabelOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], label=True)
        self.check_syntax(self.Arguments[1], var=True, integer=True, string=True, boolean=True, nil=True)
        self.check_syntax(self.Arguments[2], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsLabelOk(arg=self.Arguments) \
                or not self.IsSymbolTypeOk(arg=self.Arguments[1]) \
                or not self.IsSymbolTypeOk(arg=self.Arguments[2]):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        op1 = None
        op2 = None
        if self.Arguments[1][1] == "var":
            if self.Arguments[2][1] == "var":
                symbol2 = symbolTable.FindInSymbTable(self.Arguments[1])
                symbol3 = symbolTable.FindInSymbTable(self.Arguments[2])
                if symbol2.__dict__["value"] is None or symbol3.__dict__["value"] is None:
                    exit(56)
                elif symbol2.__dict__["type_of_var"] != symbol3.__dict__["type_of_var"]:
                    exit(53)
                op1 = symbol2.__dict__["value"]
                op2 = symbol3.__dict__["value"]
            else:
                exit(53)
        else:
            op1 = self.Arguments[1][2]
            op2 = self.Arguments[2][2]
            self.checkTypeEquals()

        if self.Opcode == "JUMPIFEQ":
            if op1 == op2:
                self.instructionPointer.GoToLabel(self.Arguments[0][2])
        elif self.Opcode == "JUMPIFNEQ":
            if op1 != op2:
                self.instructionPointer.GoToLabel(self.Arguments[0][2])

    def checkTypeEquals(self):
        if self.Arguments[1][1] != self.Arguments[2][1]:
            exit(53)


class ReturnOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
        InstructionBase.__init__(self, xml_file)

    def CheckOperation(self):
        self.Execute()

    def Execute(self):
        self.instructionPointer.Return()


class CallOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @label
    def IsLabelOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], label=True)
        if not self.IsLabelOk(arg=self.Arguments):
            exit(53)
        self.Execute()

    def Execute(self):
        self.instructionPointer.GoToLabel(self.Arguments[0][2])


class ExitOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @arithmetic_operation_symb
    def IsIntOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsIntOk(arg=self.Arguments[0]):
            exit(53)

        if self.Arguments[0][1] == "int":
            if int(self.Arguments[0][2]) >= 0 and int(self.Arguments[0][2]) <= 49:
                exit(int(self.Arguments[0][2]))
            else:
                exit(57)
        elif self.Arguments[0][1] == "var":
            symbolTable = self.InitSymbolTable(self.table)
            op1 = symbolTable.GetOperandFromSymbolTable(self.Arguments[0][2])
            exitCode = int(op1.value)
            if exitCode >= 0 and exitCode <= 49:
                exit(exitCode)
            else:
                exit(57)
        else:
            exit(53)


class DPrintOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @symb
    def IsSymbOk(arg):
        return arg

    def CheckOperation(self):
        self.check_syntax(self.Arguments[0], var=True, integer=True, string=True, boolean=True, nil=True)
        if not self.IsSymbOk(arg=self.Arguments):
            exit(53)

        if self.Arguments[0][1] == "var":
            symbolTable = self.InitSymbolTable(self.table)
            self.Execute(symbolTable)
        else:
            sys.stderr.write(self.Arguments[0][2])

    def Execute(self, symbolTable):
        symbol = symbolTable.FindInSymbTable(self.Arguments[0])
        if symbol.__dict__["value"] is None:
            sys.stderr.write("")
        else:
            sys.stderr.write(symbol.__dict__["value"])


class BreakOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
        InstructionBase.__init__(self, xml_file)

    def CheckOperation(self):
        self.Execute()

    def Execute(self):
        sys.stderr.write(str(self.instructionPointer.ip))
        sys.stderr.write("\n")


def parse_arguments():
    rp_parser = argparse.ArgumentParser(add_help=False)
    rp_parser.add_argument("--source")
    rp_parser.add_argument("--input")
    rp_parser.add_argument("--help", action="store_true")
    arguments = rp_parser.parse_args()
    return arguments


if __name__ == "__main__":
    arguments = parse_arguments()
    if arguments.help and not (arguments.source or arguments.input):
        print("Interpret nacita XML reprezentaci kodu IPPcode19 a provadi interpretaci na stdout")
        exit(0)
    elif arguments.help and (arguments.source or arguments.input):
        exit(10)

    if arguments.source is None:
        xml = "stdin"
    else:
        xml = arguments.source
    input_xml = InstructionBase(xml_file=xml, read_file=arguments.input)
    if not input_xml.check_xml_structure():
        exit(32)
    input_xml.FindAllLabels()
    input_xml.ChooseOperationCodeFromXml()
