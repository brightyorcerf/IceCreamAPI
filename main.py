from fastapi import FastAPI
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI(root_path="/api/v1")

inventory: List[Dict[str, Any]] = [
    {
        "scoopID": "1",
        "flavor": "Triple Fudge Brownie",
        "churnedAt": datetime.now(),
        "bestBefore": datetime.now()
    }, 
    {
        "scoopID": "2",
        "flavor": "Midnight Mint Chip",
        "churnedAt": datetime.now(),
        "bestBefore": datetime.now()
    }
]

@app.get("/")
async def welcomeToParlor():
    return {"message": "welcome to the Ice Cream API!"}

@app.get("/flavors")
async def readFlavors(): 
    return {"menu": inventory}

@app.get("/flavors/{id}")
async def readFlavor(id: int):
    return {"menu": id}