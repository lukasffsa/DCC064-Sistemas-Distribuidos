import asyncio, websockets, cv2, base64, json, time

CAM_ID = "cam-01"
BROKER_URI = "ws://127.0.0.1:8765"

async def stream():
    cap = cv2.VideoCapture(0)
    async with websockets.connect(BROKER_URI) as ws:
        await ws.send(json.dumps({"type": "register", "node": CAM_ID, "role": "camera"}))
        print(f"[{CAM_ID}] conectado ao broker")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            payload = json.dumps({
                "type": "frame",
                "node": CAM_ID,
                "timestamp": time.time(),
                "data": base64.b64encode(buf).decode()
            })
            await ws.send(payload)
            await asyncio.sleep(1/30)
    cap.release()

asyncio.run(stream())