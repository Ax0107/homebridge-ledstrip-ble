
import uvicorn
from rgb_control import connect, power_on, power_off, set_brightness, set_color
from threading import Thread
from asyncio import run
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CBModel(BaseModel):
    color: str
    brightness: str
    
class SModel(BaseModel):
    status: bool


@app.post('/set/')
async def set_color_and_brightness(data: CBModel):
    
    print(data.color, data.brightness)
    await set_color(data.color)
    await set_brightness(data.brightness)
    return {'status': 'ok'}


@app.post('/set_state/')
async def set_state(data: SModel):
    
    print('status:', data.status)
    if data.status:
        await power_on()
    else:
        await power_off()
    return {'status': 'ok'}


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="localhost",
        port=9988,
        reload=True,
    )
