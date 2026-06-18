import asyncio
import websockets
import cv2
import base64
import json
import time
import os

# [SD05] Transparência de Localização:
# Busca o endereço do Broker via variável de ambiente (comum em Docker) ou usa o localhost como padrão.
CAM_ID = os.getenv("CAM_ID", "cam-01")
BROKER_URI = os.getenv("BROKER_URI", "ws://127.0.0.1:8765")


async def stream():
    """
    Entidade de Protocolo: Lado Emissor (Camera).
    Responsável pela captura, serialização e streaming.
    """
    # [SD06] Gerenciamento de Componentes: Inicializa o hardware de captura local.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print(f"[{CAM_ID}] Erro: Não foi possível acessar a câmera.")
        return

    print(f"[{CAM_ID}] Tentando conectar ao broker em {BROKER_URI}...")

    # [SD03] Tratamento de Falhas: Implementa uma tentativa de conexão persistente (Retry).
    while True:
        try:
            async with websockets.connect(BROKER_URI) as ws:
                # [SD05] Registro: Notifica o sistema de nomeação do Broker sobre sua existência e papel.
                registration = {"type": "register", "node": CAM_ID, "role": "camera"}
                await ws.send(json.dumps(registration))
                print(f"[{CAM_ID}] Conectado e registrado no broker.")

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        print(f"[{CAM_ID}] Falha na captura do frame.")
                        break

                    # [SD04] Marshaling (Compactação): Codifica a imagem em JPEG para reduzir tráfego.
                    # Reduzimos a qualidade para 70% para otimizar a largura de banda.
                    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])

                    # [SD07] Sincronização Física: Anexa o timestamp atual (T1).
                    # Isso permitirá ao viewer calcular a latência (atraso delta) da rede.
                    payload = {
                        "type": "frame",
                        "node": CAM_ID,
                        "timestamp": time.time(),
                        # [SD04] Marshaling (Representação): Converte binário para Base64 (texto) para envio via JSON.
                        "data": base64.b64encode(buf).decode(),
                    }

                    # [SD04] Envio via Socket de Fluxo (TCP).
                    await ws.send(json.dumps(payload))

                    # Controla a taxa de amostragem (aprox. 30 FPS) para não sobrecarregar o Medium.
                    await asyncio.sleep(1 / 30)

        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError):
            # [SD03] Resiliência: Se o Broker cair, aguarda 5s e tenta reconectar.
            print(
                f"[{CAM_ID}] Broker indisponível. Tentando reconectar em 5 segundos..."
            )
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[{CAM_ID}] Erro inesperado: {e}")
            break

    # [SD06] Liberação de recursos ao encerrar o componente.
    cap.release()


if __name__ == "__main__":
    try:
        asyncio.run(stream())
    except KeyboardInterrupt:
        print(f"\n[{CAM_ID}] Finalizando servidor da câmera...")
