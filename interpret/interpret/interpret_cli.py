import xml.etree.ElementTree as ElementTree
import collections
import re


class XML:
    def __init__(self, xml_file):
        self._xml_file = xml_file

    @property
    def tree(self):
        return ElementTree.parse(self._xml_file)

    def check_xml_structure(self):
        root = self.tree.getroot()
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

    def parse_instruction(self):
        tree = []
        root = self.tree.getroot()
        instruction = None
        for i in range(len(root)):
            arguments_list = []
            opcode = root[i].attrib["opcode"]
            order = root[i].attrib["order"]
            if len(root[i].getchildren()) > 0:
                for child in root[i].getchildren():
                    instruction = collections.namedtuple("instruction", "order opcode arguments")
                    arg_number = child.tag
                    type_of_arg = child.attrib["type"]
                    text = child.text
                    arguments_list.extend([(arg_number, type_of_arg, text)])
                    instruction = instruction(order=order, opcode=opcode, arguments=arguments_list)
            else:
                instruction = collections.namedtuple("instruction", "order opcode arguments")
                instruction = instruction(order=order, opcode=opcode, arguments=arguments_list)
            tree.append(instruction)
        return tree
