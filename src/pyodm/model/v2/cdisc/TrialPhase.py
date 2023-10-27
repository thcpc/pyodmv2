import pyodm.model.definition as Model
import pyodm.model.meta.cdisc_odm_entity as Meta


class TrialPhase(Meta.CdiscODMEntity):
    """
    https://wiki.cdisc.org/display/ODM2/TrialPhase
    """
    
    Value = Model.Attribute()
    
    
    Description = Model.OneElement()
    
