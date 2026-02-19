from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from random import randint

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
async def welcome():
    return {"message": "Welcome to the Ice Cream API!"}

#When a request comes in, FastAPI looks at URL path first

#If the customer asks for /flavors, FastAPI looks for the function tied to @app.get("/flavors").
#The @app.get("/url") is a "Decorator 

@app.get("/flavors")
async def readFlavors(): 
    return {"menu": inventory}

@app.get("/flavors/{id}")
async def readFlavor(id: str): 
    for item in inventory:
        if item.get("scoopID") == id:
            return item

    raise HTTPException(status_code=404, detail="Flavor not found in the freezer!")\

@app.post("/flavors")
async def createFlavor(body: dict[str, Any]):

    new : Any = {
        "scoopID": randint(100, 1000),
        "flavor": body.get("flavor"),
        "churnedAt": body.get("churnedAt"),
        "bestBefore": datetime.now()
    } 

    inventory.append(new)
    return {"flavor": new}

@app.put("/flavors/{id}")
async def updateFlavor(id, body: dict[str, Any]):

    for index, flavor in enumerate(inventory):
        #enumerate turn list of items to a list of numbered items
        #use any word but first parameter is what you call the idx and second is the data
        if flavor.get("scoopID") == id:
            
            updated : Any = {
                "scoopID": flavor.get("scoopID"),
                "flavor": body.get("flavor"),
                "churnedAt": flavor.get("churnedAt"),
                "bestBefore": datetime.now()
            }
            inventory[index] = updated
            return {"flavor": updated}
    raise HTTPException(status_code=404, detail="this ID is not found")\

@app.delete("/flavors/{id}")
async def deleteFlavor(id, body: dict[str, Any]):

    for index, flavor in enumerate(inventory): 
        if flavor.get("scoopID") == id:
            
            inventory.pop(index) 
            return Response(status_code=202)
    raise HTTPException(status_code=404, detail="this ID is not found")\


# fastapi dev main.py to run 

# In Node.js, we wrote something like app.get('/flavors', (req, res) => { ... })
# FastAPI uses decorators (@app.get) to do the exact same thing: maps URL path to specific function

"""
we created a RESTful API that supports:

routing: directing traffic to different functions based on URL
serialization: converting Python data (lists/dicts) into JSON
path parameters: Using {id} to let users filter data dynamically through URL.
error handling: status codes
"""

