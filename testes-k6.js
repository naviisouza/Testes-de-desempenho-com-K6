import http from 'k6/http';
import { check, sleep } from 'k6';
import { normalDistributionStages } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

const PERFIS = {
  navegante: {
    peso: 0.5,
    cenarios: [
      { endpoint: '/produtos?delay=0.2&error_rate=0.05', peso: 0.4, pausa: [1, 3] },
      { endpoint: '/usuarios/1', peso: 0.3, pausa: [2, 4] },
      { endpoint: '/status', peso: 0.2, pausa: [1, 2] },
      { endpoint: '/config/latencia?delay=0.5', peso: 0.1, pausa: [3, 5] }
    ]
  },
  comprador: {
    peso: 0.3,
    cenarios: [
      { endpoint: '/produtos?delay=0.1&error_rate=0.1', peso: 0.2, pausa: [1, 3] },
      { endpoint: '/pagamentos', peso: 0.5, pausa: [2, 4] },
      { endpoint: '/status', peso: 0.3, pausa: [1, 2] }
    ]
  },
  robo: {
    peso: 0.2,
    cenarios: [
      { endpoint: '/status', peso: 0.5, pausa: [0.1, 0.5] },
      { endpoint: '/config/cpu?load=80', peso: 0.5, pausa: [0.1, 0.5] }
    ]
  }
};

export const options = {
  scenarios: {
    ramp_up: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 50 },
        { duration: '2m', target: 100 },
        { duration: '1m', target: 0 }
      ],
      exec: 'testeDinamico'
    },
    spike: {
      executor: 'constant-vus',
      vus: 100,
      duration: '30s',
      exec: 'testeDinamico',
      startTime: '4m'
    },
    endurance: {
      executor: 'constant-vus',
      vus: 100,
      duration: '30m',
      exec: 'testeDinamico',
      startTime: '5m'
    }
  },
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    'http_req_duration{endpoint:/pagamentos}': ['p(95)<3000'],
    http_req_failed: ['rate<0.01']
  },
  summaryTrendStats: ['avg', 'min', 'max', 'p(90)', 'p(95)', 'p(99)']
};

export function testeDinamico() {
  const perfil = escolherPerfil();
  const cenario = escolherCenario(perfil.cenarios);
  const endpoint = cenario.endpoint;
  const endpointTag = endpoint.split('?')[0];

  let res;
  if (endpoint === '/pagamentos') {
    res = http.post(`http://localhost:8000${endpoint}`, {}, {
      tags: {
        endpoint: endpointTag,
        perfil: getPerfilName(perfil),
        tipo: 'transacao'
      }
    });
  } else {
    res = http.get(`http://localhost:8000${endpoint}`, {
      tags: {
        endpoint: endpointTag,
        perfil: getPerfilName(perfil),
        tipo: 'navegacao'
      }
    });
  }

  check(res, {
    'status 200': (r) => r.status === 200,
    'tempo < 2s': (r) => r.timings.duration < 2000
  });

  const [min, max] = cenario.pausa;
  const media = (min + max) / 2;
  const desvio = (max - min) / 4;
  const pausa = Math.max(0.1, normalDistributionStages(media, desvio));
  sleep(pausa);
}

function escolherPerfil() {
  const rand = Math.random();
  let acumulado = 0;
  for (const [_, perfil] of Object.entries(PERFIS)) {
    acumulado += perfil.peso;
    if (rand <= acumulado) return perfil;
  }
  return PERFIS.navegante;
}

function escolherCenario(cenarios) {
  const rand = Math.random();
  let acumulado = 0;
  for (const cenario of cenarios) {
    acumulado += cenario.peso;
    if (rand <= acumulado) return cenario;
  }
  return cenarios[0];
}

function getPerfilName(perfil) {
  if (perfil === PERFIS.navegante) return 'navegante';
  if (perfil === PERFIS.comprador) return 'comprador';
  if (perfil === PERFIS.robo) return 'robo';
  return 'desconhecido';
}
