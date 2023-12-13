from data.structs.scraping_data import ItemScraper
from utils.methods import ScrapersInstance
from utils.logger import logger
from fastapi import FastAPI

# uvicorn main:app {--reload} --host {IP}

app = FastAPI()
scrapers = ScrapersInstance()

@app.get("/hello/{name}")
async def hello_world(name: str):
    return ({"message": f"Hello {name}"})

@app.post("/scrapers/")
async def analize_data(item: ItemScraper):
    logger.info(f"Website: {item.news_taxonomy_name}")
    return {"result" : scrapers.validate_data(item)}
