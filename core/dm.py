import asyncio
import websockets
import concurrent.futures
import json
from insights import pipeline


async def get_public_msg():
    uri = "ws://127.0.0.1:8066/ws/publicMsg"
    reconnect_attempts = 0
    max_reconnect_attempts = 3  # 可以根据需要设置最大重连次数

    while True:
        try:
            async with websockets.connect(uri, max_size=10 * 1024 * 1024) as websocket:
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    while True:
                        response = await websocket.recv()
                        datas = json.loads(response)
                        for data in datas["data"]:
                            if data["IsSender"] != "0":
                                print('self-send message, pass')
                                print(data)
                                continue
                            input_data = {
                                "user_id": data["StrTalker"],
                                "type": "publicMsg",
                                "content": data["Content"],
                                "addition": data["MsgSvrID"]
                            }
                            await loop.run_in_executor(pool, pipeline, input_data)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed with exception: {e}")
            reconnect_attempts += 1
            if reconnect_attempts <= max_reconnect_attempts:
                print(f"Reconnecting attempt {reconnect_attempts}...")
                await asyncio.sleep(5)  # 等待一段时间后重试
            else:
                print("Max reconnect attempts reached. Exiting.")
                break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

# 使用asyncio事件循环运行get_public_msg coroutine
asyncio.run(get_public_msg())
