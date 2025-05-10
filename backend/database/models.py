from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String, nullable=False)
    file_name = Column(String, nullable=True)
    original_image_url = Column(String, nullable=True)
    processed_image_url = Column(String, nullable=True)

    full_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    number = Column(String, nullable=True)
    category = Column(String, nullable=True)
    card_expires_date = Column(String, nullable=True)
    country = Column(String, nullable=True)
    issue_date = Column(String, nullable=True)
    expiration_date = Column(String, nullable=True)