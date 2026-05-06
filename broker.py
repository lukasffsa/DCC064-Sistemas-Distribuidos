import asyncio, websockets, json

clients = {}
cameras = {}

async def handler(ws):
    raw = await ws.recv()
    msg = json.loads(raw)
    role = msg.get("role")
    node = msg.get("node")

    if role == "camera":
        cameras[node] = ws
        print(f"[BROKER] câmera registrada: {node}")
        async for data in ws:
            for viewer_ws in list(clients.values()):
                try:
                    await viewer_ws.send(data)
                except:
                    pass

    elif role == "viewer":
        clients[node] = ws
        print(f"[BROKER] viewer conectado: {node}")
        try:
            await ws.wait_closed()
        finally:
            clients.pop(node, None)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("[BROKER] rodando na porta 8765...")
        await asyncio.Future()

asyncio.run(main())