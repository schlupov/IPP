import sys
import xml.etree.ElementTree as ElementTree
import collections
import re


class XML:
    file = True

    def __init__(self, xml_file):
        if xml_file == "stdin":
            self._xml_file = self.read_in()
            XML.file = False
        else:
            self._xml_file = xml_file

    @property
    def tree(self):
        if XML.file:
            try:
                return ElementTree.parse(self._xml_file)
            except ElementTree.ParseError:
                exit(31)
        else:
            try:
                return ElementTree.fromstring(self._xml_file)
            except ElementTree.ParseError:
                exit(31)

    @staticmethod
    def read_in():
        lines = sys.stdin.readlines()
        xml = ""
        for i in range(len(lines)):
            xml += lines[i]
        return xml

    def check_xml_structure(self):
        if XML.file:
            root = self.tree.getroot()
        else:
            root = self.tree

        if (
            len(root.attrib) > 3
            or not root.tag == "program"
            or "language" not in root.attrib.keys()
            or not root.attrib["language"] == "IPPcode19"
        ):
            return False
        for key in root.attrib.keys():
            if key not in ["language", "name", "description"]:
                return False
        for child in root:
            for i in range(len(child)):
                if (
                    "order" not in child.attrib.keys()
                    or "opcode" not in child.attrib.keys()
                    or len(child.attrib) > 2
                ):
                    return False
                elif (
                    child.attrib["order"] == ""
                    or child.attrib["opcode"] == ""
                    or child.tag != "instruction"
                ):
                    return False
                elif (
                    re.match("arg[1-3]", child[i].tag) is None
                    or "type" not in child[i].attrib.keys()
                    or child[i].attrib["type"] == ""
                ):
                    return False
        return True

    def GetElementsFromXml(self):
        tmp = []
        if XML.file:
            root = self.tree.getroot()
        else:
            root = self.tree

        instruction = None
        for i in range(len(root)):
            arguments_list = []
            opcode = root[i].attrib["opcode"].upper()
            order = root[i].attrib["order"]
            if len(root[i].getchildren()) > 0:
                for child in root[i].getchildren():
                    instruction = collections.namedtuple("instruction", "order opcode arguments")
                    arg_number = child.tag
                    type_of_arg = child.attrib["type"]
                    for key in child.attrib.keys():
                        if key != "type":
                            exit(32)
                    if child.attrib["type"] not in ["int", "string", "bool", "nil", "var", "label", "type"]:
                        exit(32)
                    text = child.text
                    arguments_list.extend([(arg_number, type_of_arg, text)])
                    instruction = instruction(order=order, opcode=opcode, arguments=arguments_list)
            else:
                instruction = collections.namedtuple("instruction", "order opcode arguments")
                instruction = instruction(order=order, opcode=opcode, arguments=arguments_list)
            tmp.append(instruction)
        tree = self.sort(tmp)
        return tree

    @staticmethod
    def sort_arguments(instruction):
        args = []
        args_check = []
        for i in range(len(instruction.arguments)):
            if instruction.arguments[i][0] == "arg1":
                args.append(instruction.arguments[0])
                args_check.append(instruction.arguments[i][0])
            elif instruction.arguments[i][0] == "arg2":
                args.append(instruction.arguments[1])
                args_check.append(instruction.arguments[i][0])
            elif instruction.arguments[i][0] == "arg3":
                args.append(instruction.arguments[2])
                args_check.append(instruction.arguments[i][0])
            else:
                exit(32)
        if len(set(args_check)) != len(args):
            exit(32)
        return args

    def sort(self, tmp):
        tree = []
        order = []
        countInstructions = len(tmp)
        for i in range(countInstructions):
            for j in range(countInstructions):
                if int(tmp[j].order) == i+1:
                    instruction = self.sort_arguments(tmp[j])
                    tmp[j] = tmp[j]._replace(arguments=instruction)
                    tree.append(tmp[j])
                    order.append(tmp[j].order)
        if len(set(order)) != len(order):
            exit(32)
        return tree
