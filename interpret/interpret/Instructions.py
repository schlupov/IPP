import re

from interpret.Decorators import (
    move_operands,
    move_types,
    no_operands,
    var,
    symb,
    symb_types,
    label,
    arithmetic_operation,
    arithmetic_operation_symb,
    relational_operation_symb)
from interpret.KeyWords import KeyWords
from interpret.Semantic import SymbolTable, checkType, checkNumberOfArguments
from interpret.interpret_cli import XML
from interpret.Semantic import Token


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
            exit(52)
        self.ip = self.callStack.pop()

    def ResetPointer(self):
        self.ip = 0
        self.callStack = Stack()


class InstructionBase(XML):
    classSymbolTable = None
    stack = Stack()
    instructionPointer = InstuctionPointer()

    def __init__(self, xml_file):
        super().__init__(xml_file)

    @classmethod
    def SetSymbolTableForAllInstructions(cls, symbol_tab):
        cls.classSymbolTable = symbol_tab

    def ChooseOperationCodeFromXml(self):
        table = SymbolTable()
        for instruction in self.GetElementsFromXml():
            self.CheckInstructionInXml(instruction)
            if instruction.opcode == KeyWords.MOVE.name:
                self.CheckMove(instruction, table)
            elif (
                instruction.opcode == KeyWords.CREATEFRAME.name
                or instruction.opcode == KeyWords.PUSHFRAME.name
                or instruction.opcode == KeyWords.POPFRAME.name
                or instruction.opcode == KeyWords.BREAK.name
            ):
                self.CheckFrameInstructionAndModifySymbTable(instruction, table)
            elif instruction.opcode == KeyWords.DEFVAR.name:
                self.CheckDefvarAndModifySmybTable(instruction, table)
            elif instruction.opcode == KeyWords.PUSHS.name:
                self.CheckPushsAndModifyStack(instruction)
            elif instruction.opcode == KeyWords.POPS.name:
                self.CheckPopsAndModifyStack(instruction)
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

    def CheckDefvarAndModifySmybTable(self, instruction, table):
        changedSymbolTable = DefvarOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperationAndExecute()
        self.SetSymbolTableForAllInstructions(changedSymbolTable)
        self.instructionPointer.ip += 1

    def CheckFrameInstructionAndModifySymbTable(self, instruction, table):
        changedSymbolTable = OperationWithNoOperands(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperationAndExecute()
        self.SetSymbolTableForAllInstructions(changedSymbolTable)
        self.instructionPointer.ip += 1

    def CheckMove(self, instruction, table):
        changedSymbolTable = MoveOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()
        self.instructionPointer.ip += 1

    def CheckPushsAndModifyStack(self, instruction):
        PushsOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()
        self.instructionPointer.ip += 1

    def CheckPopsAndModifyStack(self, instruction):
        varPoppedFromStack = PopsOperation(
            instruction.opcode, instruction.arguments, self._xml_file
        ).CheckOperation()
        self.instructionPointer.ip += 1

    def CheckCallAndGoToLabel(self, instruction):
        CallOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()
        self.instructionPointer.ip += 1

    def CheckReturn(self, instruction):
        ReturnOperation(instruction.opcode, instruction.arguments, self._xml_file).CheckOperation()
        self.instructionPointer.ip += 1

    def CheckArithmeticOperation(self, instruction, table):
        changedSymbolTable = ArithmeticOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()
        self.instructionPointer.ip += 1

    def CheckRelationalOperation(self, instruction, table):
        changedSymbolTable = RelationalOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()
        self.instructionPointer.ip += 1

    def CheckBooleanOperation(self, instruction, table):
        changedSymbolTable = BooleanOperation(
            instruction.opcode, instruction.arguments, self._xml_file, table
        ).CheckOperation()
        print(changedSymbolTable.__dict__["LocalFrame"][0]["val"].__dict__)
        self.instructionPointer.ip += 1

    def CheckInstructionInXml(self, instruction):
        if (
            not self.IsKeyword(instruction.opcode)
            or re.match("^[0-9]+$", instruction.order) is None
        ):
            exit(33)

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
        symbolFromSymbTable = self.Execute(symbolTable)
        return symbolFromSymbTable

    def Execute(self, symbolTable):
        symbolFromSymbTable = symbolTable.GetVarFromSymbTable(self.Arguments)
        return symbolFromSymbTable


class PushsOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
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
        self.Execute()

    def Execute(self):
        InstructionBase.stack.push(self.Arguments[0][2])


class PopsOperation(InstructionBase):
    def __init__(self, Opcode, Arguments, xml_file):
        self.Opcode = Opcode
        self.Arguments = Arguments
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @var
    def IsOperandOk(arg):
        return arg

    def CheckOperation(self):
        if not (self.IsOperandOk(arg=self.Arguments)):
            exit(33)
        token = self.Execute()
        return token

    def Execute(self):
        if not InstructionBase.stack.isEmpty():
            variabelFromStack = InstructionBase.stack.pop()
            variableFromXml = self.Arguments[0][2].split("@")[1]
            token = Token(variableFromXml, self.Arguments[0][1].upper(), variabelFromStack)
            return token
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
        symbolTable = self.InitSymbolTable(self.table)
        symbolTable = self.Execute(symbolTable)
        return symbolTable

    def Execute(self, symbolTable):
        op1 = checkType(self.Arguments[1][2])
        op2 = checkType(self.Arguments[2][2])
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)
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

    def Execute(self, symbolTable):
        op1 = checkType(self.Arguments[1][2])
        op2 = checkType(self.Arguments[2][2])
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)

        if type(op1) != type(op2):
            exit(53)
        elif self.Arguments[1][1] == "nil" and self.Opcode != KeyWords.EQ.name:
            exit(53)

        if self.Opcode == KeyWords.LT.name:
            symbol.setTokenValue(op1 < op2)
        elif self.Opcode == KeyWords.GT.name:
            symbol.setTokenValue(op1 > op2)
        elif self.Opcode == KeyWords.EQ.name:
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
        if self.Opcode == KeyWords.NOT.name:
            checkNumberOfArguments(self.Arguments, 2)
        elif self.Opcode != KeyWords.NOT.name:
            checkNumberOfArguments(self.Arguments, 3)

        if self.Opcode == KeyWords.NOT.name and not (
            self.AreOperandsOk(arg=self.Arguments)
            and self.AreOperandsTypeOk(arg=self.Arguments[1])
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
        op1 = checkType(self.Arguments[1][2])
        op2 = None
        if self.Opcode != KeyWords.NOT.name:
            op2 = checkType(self.Arguments[2][2])
            if type(op1) != type(op2):
                exit(53)
            elif self.Arguments[1][1] != "bool" or self.Arguments[2][1] != "bool":
                exit(53)
        symbol = symbolTable.GetVarFromSymbTable(self.Arguments)

        if self.Opcode == KeyWords.AND.name:
            symbol.setTokenValue(op1 and op2)
        elif self.Opcode == KeyWords.OR.name:
            symbol.setTokenValue(op1 or op2)
        elif self.Opcode == KeyWords.NOT.name:
            if self.Arguments[1][1] != "bool":
                exit(53)
            symbol.setTokenValue(str(not op1).lower())
        return symbolTable


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


if __name__ == "__main__":
    input_xml = InstructionBase("./test.xml")
    if not input_xml.check_xml_structure():
        exit(33)
    input_xml.ChooseOperationCodeFromXml()
