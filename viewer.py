import asyncio
import websockets
import cv2
import base64
import json
import numpy as np
import time
import os

# [SD05] Transparência de Localização:
# Busca o endereço do Broker via variável de ambiente ou usa o localhost como padrão.
BROKER_URI = os.getenv("BROKER_URI", "ws://127.0.0.1:8765")
VIEWER_ID = os.getenv("VIEWER_ID", "viewer-01")


async def receive():
    """
    Entidade de Protocolo: Lado Receptor (Viewer).
    Responsável por receber, desserializar e exibir o stream de vídeo.
    """
    print(f"[{VIEWER_ID}] Tentando conectar ao broker em {BROKER_URI}...")

    # [SD03] Tratamento de Falhas: Loop de reconexão para lidar com quedas do Broker.
    while True:
        try:
            async with websockets.connect(BROKER_URI) as ws:
                # [SD05] Registro: Notifica o sistema de nomeação do Broker sobre seu papel de viewer.
                registration = {"type": "register", "node": VIEWER_ID, "role": "viewer"}
                await ws.send(json.dumps(registration))
                print(f"[{VIEWER_ID}] Conectado ao broker. Aguardando frames...")

                async for raw in ws:
                    # [SD04] Unmarshaling: Decodifica o envelope JSON recebido do conector.
                    msg = json.loads(raw)

                    if msg.get("type") != "frame":
                        continue

                    # [SD07] Sincronização de Relógios (Cálculo de Latência):
                    # Calcula o atraso delta (δ) comparando o tempo de chegada (T2) com o de captura (T1).
                    t1 = msg.get("timestamp", 0)
                    t2 = time.time()
                    latencia = t2 - t1

                    # [SD04] Unmarshaling (Representação): Converte Base64 (texto) de volta para binário.
                    data_binario = base64.b64decode(msg["data"])
                    arr = np.frombuffer(data_binario, dtype=np.uint8)

                    # Reconstrói a imagem original.
                    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

                    # Exibe informações do nó de origem e a latência calculada no frame.
                    cv2.putText(
                        frame,
                        f"Node: {msg['node']}",
                        (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )

                    # [SD07] Exibição da latência (importante para demonstrar na apresentação).
                    cv2.putText(
                        frame,
                        f"Latencia: {latencia:.3f}s",
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 255),
                        2,
                    )

                    cv2.imshow("Monitoramento de Seguranca - SD", frame)

                    # Interrompe o loop se a tecla 'q' for pressionada.
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print(f"[{VIEWER_ID}] Encerrando visualização...")
                        return

        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError):
            # [SD03] Resiliência: Aguarda antes de tentar nova conexão com o Medium.
            print(
                f"[{VIEWER_ID}] Conexão perdida com o Broker. Tentando reconectar em 5s..."
            )
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[{VIEWER_ID}] Erro crítico: {e}")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        asyncio.run(receive())
    except KeyboardInterrupt:
        print(f"\n[{VIEWER_ID}] Finalizando visualizador...")
