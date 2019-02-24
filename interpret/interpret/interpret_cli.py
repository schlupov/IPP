import xml.etree.ElementTree as ElementTree
import collections


class XML:
    def __init__(self, xml_file):
        self.tree = ElementTree.parse(xml_file)

    def parse_instruction(self):
        tree = []
        root = self.tree.getroot()
        instruction = None
        for i in range(len(root)):
            arguments_list = []
            for y in range(len(root[i])):
                opcode = root[i].attrib["opcode"]
                arg_number = root[i][y].tag
                type_of_arg = root[i][y].attrib["type"]
                text = root[i][y].text
                order = root[i].attrib["order"]
                instruction = collections.namedtuple(
                    "instruction", "order opcode arguments"
                )
                arguments_list.extend([(arg_number, type_of_arg, text)])
                instruction = instruction(
                    order=order, opcode=opcode, arguments=arguments_list
                )
            tree.append(instruction)
        return tree


test = XML("./test.xml")

for instruction in test.parse_instruction():
    print(instruction.arguments)


