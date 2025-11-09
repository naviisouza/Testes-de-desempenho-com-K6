## Descrição

Este sistema será ideal para um **tutorial prático de testes de carga**, permitindo experimentar falhas típicas como:
- Latência alta
- Vazamento de memória
- Gargalos de CPU
- Erros sob carga (5xx)
- Comportamento instável em picos de tráfego
- Degradão com escalabilidade

### 📦 Requisitos
```bash
pip install fastapi uvicorn psutil
```

## ⚙️ Configuração do Ambiente

Crie um ambiente virtual

```bash
python3 -m venv venv
```

Ative o ambiente virtual

```bash
source venv/bin/activate
```


## ▶️ Como Executar

```bash
uvicorn main:app --reload --port 8000
```

Acesse:
- `http://localhost:8000` → Documentação automática (Swagger)
- `http://localhost:8000/docs` → Swagger UI interativo


Desativar o ambiente virtual

```bash
deactivate
```
configurar uma taxa de erro
http://localhost:8000/config/erro?rate=0.1

configurar uma latência
http://localhost:8000/config/latencia?delay=1

configurar um uso de cpu (padrão 50%)
http://localhost:8000/config/cpu

configurar vazamento de memória
http://localhost:8000/config/vazamento