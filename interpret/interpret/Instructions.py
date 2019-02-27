import re

from interpret.Decorators import move_operands, move_types, no_operands
from interpret.KeyWords import KeyWords
from interpret.interpret_cli import XML
from interpret.Exceptions import *


class InstructionBase(XML):
    def __init__(self, xml_file):
        super().__init__(xml_file)

    def check_opcode(self):
        for instruction in self.parse_instruction():
            self.check_operation_syntax(instruction)
            if instruction.opcode == KeyWords.MOVE.name:
                opcode_class = VarSymb(instruction.opcode, instruction.arguments, self.tree)
                if not (opcode_class.check_arguments_operands(arg=instruction.arguments)
                        and opcode_class.check_arguments_types(arg=instruction.arguments)):
                    Exception(33)
            if instruction.opcode == KeyWords.CREATEFRAME.name:
                opcode_class = NoOperands(instruction.opcode, instruction.arguments, self.tree)
                if not opcode_class.check_arguments_operands(arg=instruction.arguments):
                    Exception(33)

    def check_operation_syntax(self, instruction):
        if not self.key(instruction.opcode) or re.match("^[0-9]+$", instruction.order) is None:
            Exception(33)

    @staticmethod
    def key(opcode):
        for keyword in KeyWords:
            if keyword.name == opcode:
                return keyword.name


class VarSymb(InstructionBase):
    def __init__(self, opcode, arguments, xml_file):
        self.opcode = opcode
        self.arguments = arguments
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @move_operands
    def check_arguments_operands(arg):
        return arg

    @staticmethod
    @move_types
    def check_arguments_types(arg):
        return arg


class NoOperands(InstructionBase):
    def __init__(self, opcode, arguments, xml_file):
        self.opcode = opcode
        self.arguments = arguments
        InstructionBase.__init__(self, xml_file)

    @staticmethod
    @no_operands
    def check_arguments_operands(arg):
        return arg


if __name__ == "__main__":
    input_xml = InstructionBase("./test.xml")
    if not input_xml.check_xml_structure():
        Exception(33)
    input_xml.check_opcode()
