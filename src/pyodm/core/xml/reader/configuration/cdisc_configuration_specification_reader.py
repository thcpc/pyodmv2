from pyodm.core.xml.reader.abstract_configuration_reader import AbstractConfigurationReader
from pyodm.exceptions import CdiscDefineRequiredException

import lxml.etree as Etree


class CdiscConfigurationSpecificationReader(AbstractConfigurationReader):

    def load_cdisc_definition(self, registry, files: list[str]):
        for file in files:
            xml_tree = Etree.parse(file)
            root = xml_tree.getroot()
            cdisc = self._find_cdisc(root)
            if cdisc is None: raise CdiscDefineRequiredException(f"{file} 没有定义 CDISC 节点")
            for name, clazz_info in self._cdisc_loader(cdisc).items():
                registry.registry_cdisc(name, clazz_info)

    def _find_cdisc(self, element):
        if element.tag.lower() == "CDISC".lower():
            return element
        else:
            for sub_element in element:
                x = self._find_cdisc(sub_element)
                if x: return x

    def _cdisc_loader(self, cdisc):
        # result = {"root": cdisc.attrib.get("cdiscRoot")}
        result = {}
        for sub_element in cdisc:
            result[sub_element.tag] = {
                "clazz": sub_element.attrib.get("clazz"),
                "modulePath": sub_element.attrib.get("modulePath")
            }
        return result
