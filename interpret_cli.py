import xml.etree.ElementTree as ElementTree


class XML:

    def __init__(self, xml_file):
        self.tree = ElementTree.parse(xml_file)

    def parse(self):
        tmp = {}
        tree = {}
        root = self.tree.getroot()
        for i in range(len(root)):
            for y in range(len(root[i])):
                tmp["type"] = root[i][y].attrib["type"]
                tmp["instruction"] = root[i].attrib["opcode"]
                tmp["argument"] = root[i][y].text
                tree[i] = tmp
        return tree

    def return_order(self):
        order = 0
        for child in self.tree.getroot():
            order = child.attrib
        return order["order"]


test = XML("./test.xml")
print(test.parse())
