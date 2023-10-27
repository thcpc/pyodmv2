from lxml import etree

import pyodm.model.definition as Model
import pyodm.model.meta.cdisc_odm_entity as Meta
from pyodm.core.xml.writer.write_status import WriteStatus
from pyodm.exceptions import XmlWriterException


def cdisc(model):
    def __inner__(func):
        def __wrapper__(self, cdisc, element):
            if isinstance(cdisc, model):
                status = func(self, cdisc, element)
                if status == WriteStatus.IGNORE: return WriteStatus.IGNORE
            else:
                return WriteStatus.PASS
            return WriteStatus.OK

        return __wrapper__

    return __inner__


class CdiscXmlWriter:

    def __init__(self, cdisc):
        self.cdisc = cdisc
        self.file_path = "test.xml"

    def write(self):

        if not isinstance(self.cdisc, Meta.CdiscODMEntity):
            raise XmlWriterException("cdisc should instance of CdiscODMEntity")
        element = etree.Element(self.cdisc.name)

        for action in [self._entity, self._many_element, self._one_element]:
            status = action(cdisc=self.cdisc, element=element)
            if status != WriteStatus.PASS: break
        dump_tree = etree.ElementTree(element=element)
        dump_tree.write(self.file_path, pretty_print=True, encoding="utf-8")

    def cdisc_model(self, unknown) -> bool:
        return isinstance(unknown, Meta.CdiscODMEntity) or \
               isinstance(unknown, Model.Attribute) or \
               isinstance(unknown, Model.OneElement) or \
               isinstance(unknown, Model.ManyElements)

    @cdisc(model=Meta.CdiscODMEntity)
    def _entity(self, cdisc, element: etree._Element = None) -> WriteStatus:
        element = etree.Element(cdisc.name) if element is None else element
        if not cdisc.is_blank():
            element.text = cdisc.value
        for name, cdisc_instance in vars(cdisc).items():
            if not self.cdisc_model(cdisc_instance): continue
            self._vars_cdisc(cdisc_instance, element=element)

    @cdisc(model=Model.Attribute)
    def _attribute(self, cdisc: Model.Attribute, element: etree._Element):
        if cdisc.no_use(): return WriteStatus.IGNORE
        element.attrib[cdisc.name] = cdisc.value

    @cdisc(model=Model.OneElement)
    def _one_element(self, cdisc: Model.OneElement, element: etree._Element) -> WriteStatus:
        if cdisc.no_use(): return WriteStatus.IGNORE
        for name, cdisc_instance in vars(cdisc).items():
            if not self.cdisc_model(cdisc_instance): continue
            if not cdisc.is_blank(): element.text = cdisc.value
            self._vars_cdisc(cdisc_instance, element)

    @cdisc(model=Model.ManyElements)
    def _many_element(self, cdisc: Model.ManyElements, element: etree._Element) -> WriteStatus:
        if cdisc.no_use(): return WriteStatus.IGNORE
        for e in cdisc.array:
            self._entity(e, etree.SubElement(element, cdisc.name))

    def _vars_cdisc(self, cdisc, element: etree._Element):
        for action in [self._attribute, self._many_element, self._one_element]:
            status = action(cdisc=cdisc, element=element)
            if status != WriteStatus.PASS: break
        if status == WriteStatus.PASS:
            self._entity(cdisc, etree.SubElement(element, cdisc.name))
