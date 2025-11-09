from fastapi import FastAPI, HTTPException, Query
import time
import random
import psutil
import os
from typing import List, Dict
import threading

app = FastAPI(
    title="API de Testes de Carga",
    description="API criada para simular problemas de desempenho em testes de carga: latência, erros, vazamento de memória, uso de CPU, etc.",
    version="1.0"
)

# Variável global para simular vazamento de memória
MEMORY_LEAK = []

# Contador de requisições para simular degradação progressiva
REQUEST_COUNTER = 0

# Lock para operações seguras em threads
memory_lock = threading.Lock()

@app.get("/")
def home():
    return {
        "message": "Bem-vindo à API de Testes de Carga!",
        "endpoints": [
            "/produtos",
            "/pagamentos",
            "/usuarios/{id}",
            "/admin/relatorios",
            "/status",
            "/config/latencia?delay=1",
            "/config/erro?rate=0.1",
            "/config/vazamento?enable=true",
            "/config/cpu?load=50"
        ]
    }

# --- 1. Endpoint: Produtos (com latência controlável) ---
@app.get("/produtos")
def get_produtos(
    delay: float = Query(0, description="Atraso artificial em segundos"),
    error_rate: float = Query(0, description="Taxa de erro (0.0 a 1.0)")
):
    """
    Simula um endpoint de listagem de produtos com:
    - Atraso configurável
    - Taxa de erro configurável
    """
    if random.random() < error_rate:
        raise HTTPException(status_code=500, detail="Erro interno simulado no serviço de produtos")

    time.sleep(delay)

    return {
        "produtos": [
            {"id": i, "nome": f"Produto {i}", "preco": round(random.uniform(10, 1000), 2)}
            for i in range(1, 21)
        ],
        "total": 20
    }


# --- 2. Endpoint: Pagamentos (crítico, deve falhar sob pico) ---
@app.post("/pagamentos")
def processar_pagamento():
    """
    Simula processamento de pagamento com:
    - Alta latência sob carga
    - Possível falha sob estresse
    - Uso de CPU
    """
    global REQUEST_COUNTER
    REQUEST_COUNTER += 1

    # Degradar desempenho com o número de requisições
    if REQUEST_COUNTER > 100:
        time.sleep(0.5 + (REQUEST_COUNTER - 100) * 0.01)  # Latência cresce

    # Simular uso de CPU (loop ocupado)
    start = time.time()
    while time.time() - start < 0.1:
        pass  # Ocupa CPU por 100ms

    # Aumenta a chance de erro com carga
    if REQUEST_COUNTER > 200 and random.random() < 0.3:
        raise HTTPException(status_code=503, detail="Serviço de pagamento sobrecarregado")

    return {"status": "sucesso", "id_pagamento": random.randint(1000, 9999), "tempo_processado_ms": 150}


# --- 3. Endpoint: Usuário (com vazamento de memória opcional) ---
@app.get("/usuarios/{user_id}")
def get_usuario(user_id: int):
    """
    Simula endpoint de usuário com possível vazamento de memória.
    """
    global MEMORY_LEAK

    # Simular vazamento de memória se ativado
    with memory_lock:
        MEMORY_LEAK.append(' ' * 1024 * 100)  # Aloca 100KB

    time.sleep(0.05)
    return {
        "id": user_id,
        "nome": f"Usuário {user_id}",
        "email": f"user{user_id}@test.com"
    }


# --- 4. Endpoint: Admin (lento, com I/O simulado) ---
@app.get("/admin/relatorios")
def gerar_relatorio():
    """
    Simula um relatório pesado com alto uso de I/O e tempo de processamento.
    """
    time.sleep(2)  # Simula processamento lento
    return {
        "relatorio": "Vendas Mensais",
        "dados": [random.randint(100, 1000) for _ in range(100)],
        "gerado_em": time.time()
    }


# --- 5. Endpoint: Status (monitoramento) ---
@app.get("/status")
def status():
    """
    Retorna métricas de saúde do sistema.
    Útil para monitorar durante testes.
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    cpu_percent = process.cpu_percent()

    return {
        "uptime_requests": REQUEST_COUNTER,
        "memory_rss_mb": round(memory_info.rss / 1024 / 1024, 2),
        "memory_leak_simulated_size_mb": round(len(MEMORY_LEAK) * 100 / 1024, 2),
        "cpu_usage_percent": cpu_percent,
        "active_threads": threading.active_count(),
        "simulated_issues": [
            "Latência configurável",
            "Erros 5xx sob carga",
            "Vazamento de memória",
            "Uso de CPU artificial",
            "Degradão com tempo"
        ]
    }


# --- 6. Configuração Dinâmica (para testes controlados) ---
@app.get("/config/latencia")
def set_latencia(delay: float = Query(1.0)):
    """Introduz atraso fixo em todas as próximas requisições."""
    time.sleep(delay)
    return {"delay_applied": delay}

@app.get("/config/erro")
def set_erro(rate: float = Query(0.0)):
    """Define taxa de erro para endpoints críticos."""
    if random.random() < rate:
        raise HTTPException(status_code=500, detail="Erro configurado")
    return {"error_rate": rate}

@app.get("/config/vazamento")
def toggle_vazamento(enable: bool = True):
    """Ativa ou desativa vazamento de memória."""
    global MEMORY_LEAK
    if enable:
        # Continua vazando
        pass
    else:
        # Limpa (em cenários reais, não seria possível)
        MEMORY_LEAK.clear()
    return {"memory_leak_enabled": enable}

@app.get("/config/cpu")
def stress_cpu(load: int = Query(50, description="Carga de CPU em % (10-100)")):
    """Simula uso de CPU por um tempo."""
    duration = 5  # segundos
    end_time = time.time() + duration
    cycles = 0
    while time.time() < end_time:
        # Ocupa CPU proporcionalmente à carga
        if random.random() * 100 < load:
            _ = [random.random() for _ in range(1000)]
        cycles += 1
    return {"cpu_stress": f"{load}%", "duration_seconds": duration, "cycles": cycles}