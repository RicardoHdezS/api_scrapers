from sqlalchemy import Column, String, DateTime, Integer, Text, null
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()

class IcapsulaData(base):
    __tablename__ = "INTELITE_ICAPSULA"

    CAPCLAVE = Column(Integer, primary_key=True)
    CAPTITULO = Column(String)
    CAPTEXTCOMP = Column(Text)
    CAPTEXTSINT = Column(Text)
    CAPURLORIGINAL = Column(String)
    CAPFCAPTURA = Column(DateTime)
    CAPFCAPSULA = Column(DateTime)
    CAPFMODIF = Column(DateTime)
    CAPNOMBRE = Column(String)
    CAPMEDIO = Column(Integer)
    CAPTESTIGO = Column(String)
    CAPTENDENCIA2 = Column(String, default=null())
    CAPINTENTOS = Column(String)
    CAPAUTOR = Column(Integer)
    CAPMODIF = Column(Integer)
    CAPAMBITO = Column(Integer)
    CAPESTADO = Column(Integer)
    CAPTIPOMEDIO = Column(Integer)
    CAPCLASIFICACION = Column(Integer)
    CAPTERMINADO = Column(String)
    CAPCOMENTARIO = Column(String)
    CAPPERSISTENT = Column(String)
    CAPORIGEN = Column(String)
class IclippingPlutem(base):
    __tablename__ = "CLIPPING_ICLIPPINGPLUTEM"

    CPTCLIPPING = Column(Integer, primary_key=True)
    CPTCAPTEMA = Column(Integer)
class IclippingImagen(base):
    __tablename__ = "CLIPPING_ICLIPPINGIMAGEN"

    CIMCLIPPING = Column(Integer, primary_key=True)
    CIMNOMBREARCHIVO = Column(String)
class IcapsulaSequence(base):
    __tablename__ = "Secuencia_Icapsula"

    Secuencia_capclave = Column(Integer, primary_key=True)
class WitnessSequence(base):
    __tablename__ = "Secuencia_Testigos"

    Secuencia_Testigos = Column(Integer, primary_key=True)
class IfteNombre(base):
    __tablename__ = "INTELITE_IFTENOMBRE"

    FNOCLAVE = Column(Integer, primary_key=True)
    FNOMEDIO = Column(Integer)
    FNOESTADO = Column(Integer)
