# Relatório Técnico — Teste de Desempenho com K6

## Objetivo

Avaliar o desempenho da API sob diferentes condições de uso, simulando perfis reais de usuários e cenários extremos de carga. O teste foi realizado com capacidade total de **100 usuários simultâneos**, conforme os requisitos da atividade.

---

## Requisitos de Desempenho

- **SLA**: p95 < 2s para endpoints críticos
- **Capacidade**: suportar 100 usuários simultâneos
- **Disponibilidade**: taxa de erro < 1%

---

## Cenários de Teste

### 1. Carga Progressiva (Ramp-Up)
- Crescimento gradual de usuários: 0 → 50 → 100 VUs
- Objetivo: observar o comportamento do sistema sob aumento progressivo de carga

### 2. Pico de Demanda (Spike)
- 100 VUs simultâneos por 30 segundos
- Objetivo: simular um pico abrupto de demanda

### 3. Resistência (Endurance)
- 100 VUs constantes por 30 minutos
- Objetivo: testar a estabilidade do sistema sob uso prolongado

---

## Perfis de Usuários

- **Navegante**: acessa produtos e status com pausas leves
- **Comprador**: realiza transações e acessa endpoints mais pesados
- **Robo**: monitora status e força carga de CPU

Cada perfil possui:
- Probabilidade de ocorrência (`peso`)
- Conjunto de endpoints específicos
- Intervalos de pausa simulando comportamento humano (think time e pacing time)

---

## Métricas Coletadas

### 1. Tempos de Resposta (`http_req_duration`)
| Métrica        | Valor Obtido     | SLA Definido | Status     |
|----------------|------------------|--------------|------------|
| Média geral    | 8.66s            | —            | ❌ Alta    |
| p90            | 16.14s           | —            | ❌ Alta    |
| p95            | 20.82s           | < 2s         | ❌ Violado |
| p99            | 27.2s            | —            | ❌ Alta    |
| `/pagamentos` p95 | 24.41s        | < 3s         | ❌ Violado |

---

### 2. Throughput (`http_reqs`)
- Total de requisições: **12.106**
- Taxa média: **5.70 requisições/segundo**
- Durante o Spike: pico de **122.63 req/s** (em outro teste)

---

### 3. Taxa de Erro (`http_req_failed`)
| Tipo de erro | Valor Obtido 	          | Limite | Status      |
|--------------|--------------------------|--------|-------------|
| Total        | 5.94%        	          | < 1%   |❌Violado   |
| 4xx          | não registrado           | —      | —           |
| 5xx          | 503 (Service Unavailable)| —      |⚠️Crítico   |
| Timeouts     | não registrado           | —      | —           |

---

## Análise e Identificação

### 1. Pontos de Saturação
- O sistema começou a degradar a partir de **50 VUs** no Ramp-Up
- No Spike e Endurance, o tempo de resposta ultrapassou 20s e surgiram erros 503

### 2. Gargalo Primário
- Indícios de gargalo no **backend** (tempo de espera alto)
- Possível sobrecarga de **CPU ou banco de dados**
- Endpoint `/pagamentos` é o mais afetado

### 3. Comportamento sob Estresse
- A API respondeu com status 200, mas com **latência extrema**
- Durante o Spike, surgiram erros 503 e tempo médio acima de 20s
- No Endurance, o sistema manteve estabilidade funcional, mas com desempenho ruim

---

## Correlação das Métricas

| Relação                             | Observação                                                              |
|-------------------------------------|-------------------------------------------------------------------------|
| Número de VUs × Tempo de resposta   | Quanto maior o número de VUs, maior o tempo de resposta (de 8s até 27s) |
| Taxa de erro × Carga do sistema     | Erros 503 surgem com carga acima de 50 VUs                              |
| Throughput × Utilização de recursos | Throughput caiu quando tempo de resposta subiu e erros apareceram       |

---

## Conclusão

O teste de carga revelou que a API **não atende aos requisitos de desempenho definidos**:

- SLA de tempo foi violado em todos os cenários
- Taxa de erro ultrapassou o limite de 1%
- Endpoint crítico `/pagamentos` apresentou gargalo evidente

Apesar de funcional, o sistema **não está preparado para uso em escala real** sem otimizações.

---

## Recomendações Técnicas

- Aumentar número de workers no servidor (ex: `uvicorn --workers 4`)
- Implementar cache e fila de requisições
- Otimizar o endpoint `/pagamentos`
- Monitorar uso de CPU, memória e banco durante testes
- Reavaliar arquitetura para suportar 100+ usuários simultâneos

---
