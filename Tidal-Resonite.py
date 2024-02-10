import asyncio
import websockets
import json
import psutil
import win32gui
import win32process
import time
import sys
import os
import requests
import coverpy
from datetime import datetime
from colorama import Fore, Style

# Initialize colorama
import colorama
colorama.init()

# Initialize coverpy
coverpy = coverpy.CoverPy()
limit = 1

async def send_data(websocket, data):
    await websocket.send(data)

async def handle_client(websocket, path):
    pprint("Client connected" , color=Fore.GREEN)

    previous_title = ""
    try:
        while True:
            tidal_title = find_tidal()
            if tidal_title:
                if tidal_title != previous_title:
                    try:
                        song, artist = tidal_title.split(" - ")
                        # Fetch image URL using coverpy
                        result = coverpy.get_cover(f"{song} {artist}", limit)
                        artwork_url = result.artwork(512)
                        # Construct data with image URL
                        data = f"Song: {song} | Artist: {artist} | {artwork_url}"
                        pprint(f"Currently Listening to {song} by {artist}", color=Fore.GREEN)
                        await send_data(websocket, data)
                        previous_title = tidal_title
                    except ValueError:
                        pass  # Ignore invalid song format
            else:
                pprint("Nothing Playing")
                await send_data(websocket, "Nothing Playing")

            await asyncio.sleep(0.05)
    except websockets.ConnectionClosed:
        pprint("Client disconnected" , color=Fore.RED)

def pprint(txt, color=None):
    color_code = color if color else ""
    reset_code = Style.RESET_ALL if color else ""
    sys.stdout.write(
        f'{color_code}{datetime.now().strftime("%H:%M:%S")} => {txt}{reset_code}\n'
    )

def enum_windows():
    windows = []

    def enum_callback(hwnd, results):
        results.append((hwnd, win32gui.GetWindowText(hwnd), win32process.GetWindowThreadProcessId(hwnd)[1]))

    win32gui.EnumWindows(enum_callback, windows)
    return windows

def find_tidal():
    window = enum_windows()
    for hwnd, title, pid in window:
        try:
            process = psutil.Process(pid)
            if process.name() == "TIDAL.exe":
                if title == "" or title == "Default IME" or title == "MSCTFIME UI":
                    continue
                return title
        except:
            pass

if __name__ == "__main__":
    start_server = websockets.serve(handle_client, "localhost", 1050)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
