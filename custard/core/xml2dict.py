# -*- coding=utf-8
import xml.etree.ElementTree


class Xml2Dict(dict):
    def __init__(self, parent_node):
        if parent_node.items():
            self.update_dict(dict(parent_node.items()))
        for element in parent_node:
            if len(element):
                adict = Xml2Dict(element)
                self.update_dict({element.tag: adict})
            elif element.items():
                element_attrib = element.items()
                if element.text:
                    element_attrib.append((element.tag, element.text))
                self.update_dict({element.tag: dict(element_attrib)})
            else:
                self.update_dict({element.tag: element.text})

    def update_dict(self, adict):
        for key in adict:
            if key in self:
                value = self.pop(key)
                if type(value) is not list:
                    lst = []
                    lst.append(value)
                    lst.append(adict[key])
                    self.update({key: lst})
                else:
                    value.append(adict[key])
                    self.update({key: value})
            else:
                self.update({key: adict[key]})


if __name__ == "__main__":
    s = """<?xml version="1.0" encoding="utf-8" ?>
    <result xmlns= "wqa.bai.com">
        <count n="1">10</count>
        <data><id>1</id><name>test1</name></data>
        <data><id>2</id><name>test2</name></data>
        <data><id>3</id><name>test3</name></data>
    </result>"""
    root = xml.etree.ElementTree.fromstring(s)
    xmldict = Xml2Dict(root)
    print(xmldict)
