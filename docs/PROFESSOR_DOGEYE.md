# DogEye — Professor + Treino (nao deixe a turma piorar)

O treino antigo era **aleatorio** — os alunos erravam e ninguem corrigia. Agora existe o **Professor** (`training/coach.py`).

## O que o Professor faz

| Funcao | Como ajuda |
|--------|------------|
| **Corrige erros** | Cada perda gera licao: estrategia errada para o cenario |
| **Modo correcao** | 4 erros seguidos → so treina o que funciona naquele cenario |
| **Anti-queda** | 3 ciclos piorando → turma volta ao basico (S09, S05) |
| **XP e niveis** | Aprendiz → Mestre (5 niveis) — evolucao visivel |
| **Sabedoria** | Regras provadas vao para `data/training/wisdom.json` |

## Comandos novos

```powershell
# Ver turma, niveis, sabedoria acumulada
python scripts/dogeye_continuous_training.py --coach

# Treino continuo COM professor (padrao agora)
.\run_continuous_training.ps1
```

## Arquivos do professor

- `data/training/lessons.jsonl` — licoes e correcoes
- `data/training/wisdom.json` — conhecimento validado
- `data/training/coach_state.json` — estado de cada estrategia-aluno

## Regra para a equipe

1. **Leiam** `--coach` todo dia
2. **Obedeçam** modo correcao — nao forcem estrategia que o professor bloqueou
3. **Anoteem** sabedoria: "em ranging uso S02, em trend uso S04"
4. Objetivo: **subir de nivel**, nao so rodar ciclos

**Professor ensina. Alunos evoluem. Nao deixem cair.**
