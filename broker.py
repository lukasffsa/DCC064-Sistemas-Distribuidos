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
        print(f"[BROKER] camera registrada: {node}")
        try:
            async for data in ws:
                for viewer_node, viewer_ws in list(clients.items()):
                    try:
                        await viewer_ws.send(data)
                    except websockets.ConnectionClosed:
                        clients.pop(viewer_node, None)
        finally:
            cameras.pop(node, None)

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