
import uvicorn
from rgb_control import *
from threading import Thread
from asyncio import run
from fastapi import FastAPI

app = FastAPI()


Thread(target=run, args=(connect(),)).start()


@app.post('/set/')
async def set_color_and_brightness(color: str, brightness: str):
    
    print(color, brightness)
    await set_color(color)
    await set_brightness(brightness)
    return {'status': 'ok'}


@app.post('/set_state/')
async def set_state(status: bool):
    
    print('status:', status)
    if status:
        await power_on()
    else:
        await power_off()
    return {'status': 'ok'}


if __name__ == "__main__":
    uvicorn.run(
        "app",
        host="localhost",
        port=9988,
        reload=True,
    )
