import argparse
import re
import sys

from Decorators import (
    move_operands,
    move_types,
    no_operands,
    var,
    symb,
    symb_types,
    label,
    arithmetic_operation,
    arithmetic_operation_symb,
    relational_operation_symb,
    int2char_var,
    str2int_symb,
    read_type,
    check_int,
    check_string,
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
                self.CheckLabel(instruction)
            instruction = self.GetInstruction()
        self.instructionPointer.ResetPointer()

    def ChooseOperationCodeFromXml(self):
        table = SymbolTable()
        instruction = self.GetInstruction()

        while instruction is not None:
            self.CheckInstructionInXml(instruction)
            if instruction.opcode == KeyWords.MOVE.name:
                self.CheckMove(instruction, table)
            elif (
                    instruction.opcode == KeyWords.CREATEFRAME.name
                or instruction.opcode == KeyWords.PUSHFRAME.name
                or instruction.opcode == KeyWords.POPFRAME.name
            ):
                self.CheckFrameInstructionAndModifySymbTable(instruction, table)
            elif instruction.opcode == KeyWords.DEFVAR.name:
                self.CheckDefvarAndModifySmybTable(instruction, table)
            elif instruction.opcode == KeyWords.PUSHS.name:
                self.CheckPushsAndModifyStack(instruction, table)
            elif instruction.opcode == KeyWords.POPS.name:
                self.CheckPopsAndModifyStack(instruction, table)
            elif instruction.opcode == KeyWords.CALL.name:
                self.CheckCallAndGoToLabel(instruction)
            elif instruction.opcode == KeyWords.RETURN.name:
                self.CheckReturn(instruction)
            elif (
                instruction.opcode == KeyWords.ADD.name
                or instruction.opcode == KeyWords.SUB.name
                or instruction.opcode == KeyWords.MUL.name
                or instruction.opcode == KeyWords.IDIV.name
            ):
                self.CheckArithmeticOperation(instruction, table)
            elif (
                instruction.opcode == KeyWords.LT.name
                or instruction.opcode == KeyWords.GT.name
                or instruction.opcode == KeyWords.EQ.name
            ):
                self.CheckRelationalOperation(instruction, table)
            elif (
                instruction.opcode == KeyWords.AND.name
                or instruction.opcode == KeyWords.OR.name
                or instruction.opcode == KeyWords.NOT.name
            ):
                self.CheckBooleanOperation(instruction, table)
            elif instruction.opcode == KeyWords.INT2CHAR.name:
                self.CheckIntToChar(instruction, table)
            elif instruction.opcode == KeyWords.STRI2INT.name:
                self.CheckStrToInt(instruction, table)
            elif instruction.opcode == KeyWords.WRITE.name:
                self.CheckWrite(instruction, table)
            elif instruction.opcode == KeyWords.CONCAT.name:
                self.CheckConcat(xml[self.i], table)
            elif instruction.opcode == KeyWords.READ.name:
                self.CheckRead(instruction, table)
            elif instruction.opcode == KeyWords.STRLEN.name:
                self.CheckStrlen(instruction, table)
            elif instruction.opcode == KeyWords.GETCHAR.name:
                self.CheckGetchar(instruction, table)
            elif instruction.opcode == KeyWords.SETCHAR.name:
                self.CheckSetchar(instruction, table)
            elif instruction.opcode == KeyWords.TYPE.name:
                self.CheckType(instruction, table)
            elif instruction.opcode == KeyWords.JUMP.name:
                self.CheckJump(instruction)
            elif (
                instruction.opcode == KeyWords.JUMPIFEQ.name
                or instruction.opcode == KeyWords.JUMPIFNEQ.name
            ):
                self.CheckJumpIfEq(instruction, table)
            elif instruction.opcode == KeyWords.EXIT.name:
                self.CheckExit(instruction)
            elif instruction.opcode == KeyWords.DPRINT.name:
                self.CheckDPrint(instruction, table)
            elif instruction.opcode == KeyWords.BREAK.name:
                self.CheckBreak(instruction)
            instruction = self.GetInstruction()

    def CheckDefvarAndModifySmybTable(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 1)
        changedSymbolTable = DefvarOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperationAndExecute()
        self.SetSymbolTableForAllInstructions(changedSymbolTable)

    def CheckFrameInstructionAndModifySymbTable(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 0)
        changedSymbolTable = OperationWithNoOperands(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperationAndExecute()
        self.SetSymbolTableForAllInstructions(changedSymbolTable)

    def CheckMove(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 2)
        changedSymbolTable = MoveOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckPushsAndModifyStack(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 1)
        PushsOperation(instruction.opcode, instruction.arguments,
                       self._xml_file, table).CheckOperation()

    def CheckPopsAndModifyStack(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 1)
        varPoppedFromStack = PopsOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckCallAndGoToLabel(self, instruction):
        checkNumberOfArguments(instruction.arguments, 1)
        CallOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()

    def CheckReturn(self, instruction):
        checkNumberOfArguments(instruction.arguments, 0)
        ReturnOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()

    def CheckArithmeticOperation(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 3)
        changedSymbolTable = ArithmeticOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckRelationalOperation(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 3)
        changedSymbolTable = RelationalOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckBooleanOperation(self, instruction, table):
        if instruction.opcode != KeyWords.NOT.name:
            checkNumberOfArguments(instruction.arguments, 3)
        else:
            checkNumberOfArguments(instruction.arguments, 2)
        changedSymbolTable = BooleanOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckIntToChar(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 2)
        changedSymbolTable = IntToCharOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckStrToInt(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 3)
        changedSymbolTable = StrToIntOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckWrite(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 1)
        WriteOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckConcat(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 3)
        ConcatOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckStrlen(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 2)
        StrlenOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckGetchar(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 3)
        GetCharOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckSetchar(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 3)
        SetCharOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckType(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 2)
        TypeOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckLabel(self, instruction):
        checkNumberOfArguments(instruction.arguments, 1)
        LabelOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()

    def CheckJump(self, instruction):
        checkNumberOfArguments(instruction.arguments, 1)
        JumpOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()

    def CheckJumpIfEq(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 3)
        JumpIfEqOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckExit(self, instruction):
        checkNumberOfArguments(instruction.arguments, 1)
        ExitOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()

    def CheckDPrint(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 1)
        DPrintOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()

    def CheckBreak(self, instruction):
        checkNumberOfArguments(instruction.arguments, 0)
        BreakOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()

    def CheckRead(self, instruction, table):
        checkNumberOfArguments(instruction.arguments, 2)
        changedSymbolTable = ReadOperation(
            instruction.opcode, instruction.arguments, self.xml_file, table, self.read_file
        ).CheckOperation()

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


class MoveOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @move_operands
    def AreOperandsOk(arg):
        return arg

    @staticmethod
    @move_types
    def AreOperandsTypeOk(arg):
        return arg

    def CheckOperation(self):
        if not (
            self.AreOperandsOk(arg=self.Arguments) and self.AreOperandsTypeOk(arg=self.Arguments)
        ):
            exit(33)
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
    def IsOperandOk(arg):
        return arg

    @staticmethod
    @symb_types
    def IsOperandTypeOk(arg):
        return arg

    def CheckOperation(self):
        if not (self.IsOperandOk(arg=self.Arguments) and self.IsOperandTypeOk(arg=self.Arguments)):
            exit(33)
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
        if not (self.IsOperandOk(arg=self.Arguments)):
            exit(33)
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

    @staticmethod
    @no_operands
    def IsOperationOk(arg):
        return arg

    def CheckOperationAndExecute(self):
        if not self.IsOperationOk(arg=self.Arguments):
            exit(33)
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
        if not self.AreOperandsOk(arg=self.Arguments):
            exit(33)
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
    @arithmetic_operation
    def AreOperandsOk(arg):
        return arg

    @staticmethod
    @arithmetic_operation_symb
    def AreOperandsTypeOk(arg):
        return arg

    def CheckOperation(self):
        if not (
            self.AreOperandsOk(arg=self.Arguments)
            and self.AreOperandsTypeOk(arg=self.Arguments[1])
            and self.AreOperandsTypeOk(arg=self.Arguments[2])
        ):
            exit(33)
        if not (self.Arguments[0][1] == "int" and self.Arguments[1][1] == "int"
                or self.Arguments[0][1] == "var" and self.Arguments[1][1] == "var"):
            exit(53)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        if self.Arguments[0][1] == "var" and self.Arguments[1][1] == "var":
            op1 = checkType(self.Arguments[1][2])
            op2 = checkType(self.Arguments[2][2])
            symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
            op1 = symbolTable.GetOperandFromSymbolTable(op1)
            op1 = int(op1.value)
            op2 = symbolTable.GetOperandFromSymbolTable(op2)
            op2 = int(op2.value)

        if self.Arguments[0][1] == "int" and self.Arguments[1][1] == "int":
            op1 = int(self.Arguments[0][2])
            op2 = int(self.Arguments[1][2])

        if self.Opcode == KeyWords.ADD.name:
            symbol.setTokenValue(op1 + op2)
        elif self.Opcode == KeyWords.SUB.name:
            symbol.setTokenValue(op1 - op2)
        elif self.Opcode == KeyWords.MUL.name:
            symbol.setTokenValue(op1 * op2)
        elif self.Opcode == KeyWords.IDIV.name:
            try:
                symbol.setTokenValue(int(op1 / op2))
            except ZeroDivisionError:
                exit(57)
        return symbolTable


class RelationalOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @arithmetic_operation
    def AreOperandsOk(arg):
        return arg

    @staticmethod
    @relational_operation_symb
    def AreOperandsTypeOk(arg):
        return arg

    def CheckOperation(self):
        if not (
            self.AreOperandsOk(arg=self.Arguments)
            and self.AreOperandsTypeOk(arg=self.Arguments[1])
            and self.AreOperandsTypeOk(arg=self.Arguments[2])
        ):
            exit(33)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    @staticmethod
    def convertType(arg):
        if arg[1] == "int":
            return int(arg[2])
        elif arg[1] == "string":
            return arg[2]
        elif arg[1] == "bool":
            return bool(arg[2])

    def Execute(self, symbolTable):
        nil_return = None
        op1 = checkType(self.Arguments[1][2])
        op2 = checkType(self.Arguments[2][2])
        if self.Arguments[1][1] == "var" and self.Arguments[2][1] == "var":
            symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
            op1 = symbolTable.GetOperandFromSymbolTable(op1)
            op2 = symbolTable.GetOperandFromSymbolTable(op2)
            if op1.type_of_var != op2.type_of_var:
                if op1.type_of_var == "nil" or op2.type_of_var == "nil":
                    nil_return = False
                else:
                    exit(53)
            if op1.type_of_var == "int" and op2.type_of_var == "int":
                op1 = int(op1.value)
                op2 = int(op2.value)
            elif op1.type_of_var == "bool" and op2.type_of_var == "bool":
                if op1.value == "true":
                    op1 = 1
                elif op1.value == "false":
                    op1 = 0
                if op2.value == "true":
                    op2 = 1
                elif op2.value == "false":
                    op2 = 0
            elif op1.type_of_var == "string" and op2.type_of_var == "string":
                op1 = str(op1.value)
                op2 = str(op2.value)
            elif op1.type_of_var == "nil" and op2.type_of_var == "nil":
                op1 = str(op1.value)
                op2 = str(op2.value)
        else:
            op1 = self.convertType(self.Arguments[1])
            op2 = self.convertType(self.Arguments[2])
            if self.Arguments[1][1] != self.Arguments[2][1]:
                if self.Arguments[1][1] == "nil" or self.Arguments[2][1] == "nil":
                    nil_return = False
                else:
                    exit(53)

        if self.Arguments[1][1] == "nil" and self.Opcode != KeyWords.EQ.name:
            exit(53)

        if self.Opcode == KeyWords.LT.name:
            symbol.setTokenValue(op1 < op2)
        elif self.Opcode == KeyWords.GT.name:
            symbol.setTokenValue(op1 > op2)
        elif self.Opcode == KeyWords.EQ.name:
            if nil_return:
                symbol.setTokenValue(False)
            else:
                symbol.setTokenValue(op1 == op2)
        return symbolTable


class BooleanOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file, table):
        self.Opcode = Opcode
        self.Arguments = Arguments
        self.table = table
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @arithmetic_operation
    def AreOperandsOk(arg):
        return arg

    @staticmethod
    @relational_operation_symb
    def AreOperandsTypeOk(arg):
        return arg

    def CheckOperation(self):
        if self.Opcode == KeyWords.NOT.name and not (
            self.AreOperandsOk(arg=self.Arguments) and self.AreOperandsTypeOk(arg=self.Arguments[1])
        ):
            exit(33)
        elif self.Opcode != KeyWords.NOT.name and not (
            self.AreOperandsOk(arg=self.Arguments)
            and self.AreOperandsTypeOk(arg=self.Arguments[1])
            and self.AreOperandsTypeOk(arg=self.Arguments[2])
        ):
            exit(33)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)

        if self.Arguments[0][1] == "var" and self.Arguments[1][1] == "var":
            if self.Opcode != KeyWords.NOT.name:
                op1 = symbolTable.GetOperandFromSymbolTable(self.Arguments[1][2])
                op2 = symbolTable.GetOperandFromSymbolTable(self.Arguments[2][2])
                if op1.type_of_var != "bool" or op1.type_of_var != "bool":
                    exit(53)
                op1 = op1.value
                op2 = op2.value
            else:
                op1 = symbolTable.GetOperandFromSymbolTable(self.Arguments[1][2])
                if op1.type_of_var != "bool":
                    exit(53)
                op1 = op1.value

        if self.Arguments[1][1] == "bool" and self.Arguments[2][1] == "bool":
            op1 = checkType(self.Arguments[1][2])
            op2 = checkType(self.Arguments[2][2])
            if not isinstance(op1, bool) or not isinstance(op2, bool):
                exit(53)
            op1 = self.Arguments[0][2]
            op2 = self.Arguments[1][2]

        if self.Opcode == KeyWords.AND.name:
            if op1 == 'false' and op2 == 'true':
                symbol.setTokenValue('false')
            else:
                symbol.setTokenValue(op1 and op2)
        elif self.Opcode == KeyWords.OR.name:
            symbol.setTokenValue(op1 or op2)
        elif self.Opcode == KeyWords.NOT.name:
            symbol.setTokenValue(str(not op1).lower())
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
    @int2char_var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        if not (self.IsSymbOk(arg=self.Arguments[1]) and self.IsVarOk(arg=self.Arguments)):
            exit(33)
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
    @arithmetic_operation
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        if not (
            self.IsSymb2Ok(arg=self.Arguments[2])
            and self.IsSymb1Ok(arg=self.Arguments[1])
            and self.IsVarOk(arg=self.Arguments)
        ):
            exit(33)
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
    @arithmetic_operation
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        if not (self.IsTypeOk(arg=self.Arguments[1]) and self.IsVarOk(arg=self.Arguments)):
            exit(33)
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
                token = Token(symbol.name, "bool", "bool" + "@" + inputData)
            else:
                token = Token(symbol.name, "bool", "bool" + "@" + "false")
            symbol.setTokenValue(token)
        elif self.Arguments[1][2] == "int":
            if check_int(inputData):
                token = Token(symbol.name, "int", "int" + "@" + inputData)
            else:
                token = Token(symbol.name, "int", "int" + "@" + "0")
            symbol.setTokenValue(token)
        elif self.Arguments[1][2] == "string":
            if check_string(inputData):
                token = Token(symbol.name, "string", "string" + "@" + inputData)
            else:
                token = Token(symbol.name, "string", "string" + "@" + "")
            symbol.setTokenValue(token)
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

    @staticmethod
    @symb_types
    def IsOperandTypeOk(arg):
        return arg

    def CheckOperation(self):
        if not (self.IsOperandOk(arg=self.Arguments) and self.IsOperandTypeOk(arg=self.Arguments)):
            exit(33)
        symbolTable = self.InitSymbolTable(self.table)
        self.Execute(symbolTable)

    def Execute(self, symbolTable):
        if self.Arguments[0][1] == "var":
            symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
            op = symbol.__dict__["value"]
        else:
            op = checkType(self.Arguments[0][2])

        if isinstance(op, bool):
            if op:
                op = "true"
            else:
                op = "false"
        elif isinstance(op, str):
            op = self.CheckEscape(op)

        print(op, end="")

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
    @arithmetic_operation
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        if not (
            self.IsSymbOk(arg=self.Arguments[2])
            and self.IsSymbOk(arg=self.Arguments[1])
            and self.IsVarOk(arg=self.Arguments)
        ):
            exit(33)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        op1 = checkType(self.Arguments[1][2])
        op2 = checkType(self.Arguments[2][2])
        symbol.setTokenValue(op1 + op2)
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
    @int2char_var
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        if not (self.IsSymbOk(arg=self.Arguments[1]) and self.IsVarOk(arg=self.Arguments)):
            exit(33)
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        if self.Arguments[1][1] == "var":
            symbol = symbolTable.FindInSymbTable(self.Arguments[1])
            op = symbol.__dict__["value"]
        else:
            op = checkType(self.Arguments[1][2])
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
        try:
            symbol.setTokenValue(len(op))
        except TypeError:
            exit(53)
        return symbolTable


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
    @arithmetic_operation
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        if not (
            self.IsSymb2Ok(arg=self.Arguments[2])
            and self.IsSymb1Ok(arg=self.Arguments[1])
            and self.IsVarOk(arg=self.Arguments)
        ):
            exit(33)
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
    @arithmetic_operation
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        if not (
            self.IsSymb2Ok(arg=self.Arguments[2])
            and self.IsSymb1Ok(arg=self.Arguments[1])
            and self.IsVarOk(arg=self.Arguments)
        ):
            exit(33)
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
    @move_operands
    def IsSymbOk(arg):
        return arg

    @staticmethod
    @symb_types
    def IsVarOk(arg):
        return arg

    def CheckOperation(self):
        if not (self.IsSymbOk(arg=self.Arguments) and self.IsVarOk(arg=self.Arguments)):
            exit(33)
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
        if not self.IsLabelOk(arg=self.Arguments):
            exit(33)
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
        if not self.IsLabelOk(arg=self.Arguments):
            exit(33)
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
        if not (
            self.IsLabelOk(arg=self.Arguments)
            and self.IsSymbolTypeOk(arg=self.Arguments[1])
            and self.IsSymbolTypeOk(arg=self.Arguments[2])
        ):
            exit(33)
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

    @staticmethod
    @no_operands
    def AreOperandsOk(arg):
        return arg

    def CheckOperation(self):
        if not self.AreOperandsOk(arg=self.Arguments):
            exit(33)
        self.Execute()

    def Execute(self):
        self.instructionPointer.Return()

    """
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
    """


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
        if not self.IsLabelOk(arg=self.Arguments):
            exit(33)
        self.Execute()

    def Execute(self):
        self.instructionPointer.GoToLabel(self.Arguments[0][2])


class ExitOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @arithmetic_operation_symb
    def IsIntOk(arg):
        return arg

    def CheckOperation(self):
        if self.Arguments[0][1] != "int":
            exit(57)
        if not self.IsIntOk(arg=self.Arguments[0]):
            exit(33)

        if int(self.Arguments[0][2]) <= 49:
            exit(int(self.Arguments[0][2]))


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
        if not self.IsSymbOk(arg=self.Arguments):
            exit(33)

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
