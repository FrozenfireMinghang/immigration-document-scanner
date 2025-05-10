from pydantic import BaseModel
from typing import Optional

class SaveRequest(BaseModel):
    id: Optional[int]
    document_type: str
    file_name: Optional[str]
    original_image_url: Optional[str]
    processed_image_url: Optional[str]

    full_name: Optional[str]
    date_of_birth: Optional[str] = None
    number: Optional[str] = None
    category: Optional[str] = None
    card_expires_date: Optional[str] = None
    country: Optional[str] = None
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None