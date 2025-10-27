from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading

class CountUpdate(BaseModel):
    value: int

app = FastAPI()
count = 0
lock = threading.Lock()
total_visits = 0
reset_count = 0
maximum = 2**63 - 1

async def atomic_inc_reset():
    global reset_count
    with lock:
        reset_count +=1        

async def atomic_inc_total():
    global total_visits
    with lock:
        total_visits +=1

async def atomic_inc_count():
    global count 
    with lock:
        count += 1

async def atomic_reset_count():
    global count
    with lock:
        count = 0

async def atomic_set_count(value: int):
    global count
    with lock:
        count = value

@app.get("/counter/visit")
async def counter_visit():
    await atomic_inc_count()
    await atomic_inc_total()
    atomic_inc_count()
    atomic_inc_total()
    if count > maximum:
        raise ValueError("count overflow")
    if total_visits > maximum:
        raise ValueError("total visits overflow")
    return {"count": count, "message": "string"}

@app.get("/counter/current")
async def counter_current():
    return {"count": count}

@app.get("/counter/reset")
async def counter_reset():
    await atomic_reset_count()
    await atomic_inc_reset()
    atomic_inc_reset()
    if reset_count > maximum:
        raise ValueError("reset overflow")
    count = 0
    return {"count": count, "message": "reset"}

@app.get("/counter/stats")
async def counter_stats():
    return {"total_visits": total_visits, "reset_count": reset_count}

@app.post("/counter/set/{value}")
async def counter_set(value: int):
    if value > maximum:
        raise ValueError("value is too big")
    count = value

    await atomic_set_count(value)
    
    return {"count": count, "message": "updated"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "counter"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


