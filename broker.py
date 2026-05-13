import asyncio
import websockets
import json

# [SD02] Arquitetura Centralizada: O Broker atua como o Coordenador central do sistema.
# Armazenamos as conexões ativas para garantir a Transparência de Localização.
viewers = {}
cameras = {}


async def handler(ws):
    """
    Tratador de conexões (Entidade de Protocolo).
    Gerencia o ciclo de vida de câmeras e visualizadores.
    """
    try:
        # [SD04] Marshaling: Recebe a mensagem inicial estruturada em JSON.
        raw = await ws.recv()
        msg = json.loads(raw)
        role = msg.get("role")
        node = msg.get("node")

        if role == "camera":
            # [SD05] Registro no Sistema de Nomeação local do Broker.
            cameras[node] = ws
            print(f"[BROKER - SD05] Câmera registrada: {node}")

            try:
                # Loop de recepção de frames (Stream de Dados).
                async for data in ws:
                    # [SD02] Distribuição: Encaminha os dados da câmera para todos os Viewers.
                    # list() é usado para evitar erro de concorrência se a lista mudar durante o loop.
                    for viewer_id, viewer_ws in list(viewers.items()):
                        try:
                            await viewer_ws.send(data)
                        except websockets.exceptions.ConnectionClosed:
                            # Limpeza automática de conectores inativos.
                            viewers.pop(viewer_id, None)
            except websockets.exceptions.ConnectionClosed:
                print(f"[BROKER] Conexão com a câmera {node} perdida.")
            finally:
                cameras.pop(node, None)

        elif role == "viewer":
            viewers[node] = ws
            print(f"[BROKER - SD02] Viewer conectado: {node}")

            try:
                # [SD08] Exclusão Mútua: Mantém a conexão aberta sem "atropelar" outras.
                # O viewer apenas aguarda dados enviados pelo loop da câmera acima.
                await ws.wait_closed()
            finally:
                # [SD06] Gerenciamento de Componentes: Remove o viewer ao desconectar.
                viewers.pop(node, None)
                print(f"[BROKER] Viewer {node} desconectado.")

    except Exception as e:
        print(f"[BROKER - ERRO] Falha na comunicação: {e}")


async def main():
    # [SD04] Conector: Abre um Socket de Fluxo (TCP) na porta 8765.
    # 0.0.0.0 permite que o Broker aceite conexões externas (essencial para Docker).
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("[BROKER - SD04] Servidor rodando na porta 8765...")
        # Mantém o serviço rodando indefinidamente.
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[BROKER] Encerrando serviço...")
