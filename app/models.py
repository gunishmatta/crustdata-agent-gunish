from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class FAQ(Base):
    __tablename__ = 'faq'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, index=True)
    answer = Column(Text)

class APIDocumentation(Base):
    __tablename__ = 'api_documentation'
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, unique=True, index=True)
    description = Column(Text)
    method = Column(String)
    parameters = Column(JSON)

class Region(Base):
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True, index=True)
    region_name = Column(String, unique=True, index=True)
    country_name = Column(String)
