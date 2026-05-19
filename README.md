# DCC064-Sistemas-Distribuidos

Rodar em terminais separados

### Modo sem Docker (original)

- python broker.py
- python camera-server.py
- python viewer.py

### modo com Docker (Windows + Docker Desktop/WSL2)

Neste modo o broker roda em um container. A camera e o viewer rodam no host
porque o `cv2.imshow` nao abre janela dentro do container no Windows.

#### passo a passo para iniciantes

1. Abra o Docker Desktop e aguarde ficar "Running".

2. Abra um terminal na pasta do projeto e suba o broker:

```
docker compose up --build
```

Deixe esse terminal aberto mostrando os logs do broker.

3. Em outro terminal, instale as dependencias (uma vez):

```
pip install -r requirements.txt
```

4. Ainda nesse segundo terminal, rode a camera:

```
python camera-server.py
```

5. Em um terceiro terminal, rode o viewer:

```
python viewer.py
```

6. Para parar tudo:

- No terminal do viewer, pressione `q` na janela da camera.
- No terminal do broker, pressione `Ctrl+C`.
- No terminal da camera, pressione `Ctrl+C`.
