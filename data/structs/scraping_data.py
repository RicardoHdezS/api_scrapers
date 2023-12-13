from pydantic import BaseModel
from datetime import datetime

class ItemScraper(BaseModel):

    identifier_scraping: str
    news_publication_date: datetime
    news_modified_date: datetime
    db_insert_date: datetime
    db_update_date: datetime
    news_url: str
    news_section: str
    news_head_title: str
    news_author: str
    news_content: str
    twitter: str = None
    news_cve_medio: int
    news_media_id: int
    news_taxonomy_name: str