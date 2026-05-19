import asyncio, websockets, cv2, base64, json, numpy as np

BROKER_URI = "ws://127.0.0.1:8765"

async def receive():
    async with websockets.connect(BROKER_URI) as ws:
        await ws.send(json.dumps({"type": "register", "node": "viewer-01", "role": "viewer"}))
        print("[VIEWER] aguardando frames...")
        async for raw in ws:
            msg = json.loads(raw)
            if msg.get("type") != "frame":
                continue
            arr = np.frombuffer(base64.b64decode(msg["data"]), dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                continue
            cv2.putText(frame, f"{msg['node']}", (10,25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,200,100), 2)
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()

asyncio.run(receive())