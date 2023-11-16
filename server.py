
import uvicorn
from rgb_control import connect, power_on, power_off, set_brightness, set_color
from threading import Thread
from asyncio import run
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CModel(BaseModel):
    r: int
    g: int
    b: int

class BModel(BaseModel):
    brightness: int
    
class SModel(BaseModel):
    status: bool


@app.post('/set/color')
async def set_color_api(data: CModel):
    
    print(data.r,data.g,data.b)
    await set_color(data.r, data.g, data.b)
    return {'status': 'ok'}


@app.post('/set/brightness')
async def set_brightness_api(data: BModel):
    print(data.brightness)
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
