# AI Tool Usage Documentation

## Beyond Frequency: Knowledge Graphs for Fashion Trend Analysis

Declaração de uso de ferramentas de IA em conformidade com a Portaria CNPq nº 2.664/2026.
Todo o conteúdo gerado com auxílio de IA foi revisado e validado pelo autor,
que assume integral responsabilidade pelo conteúdo da publicação.

---

## 1. Claude (Anthropic) — Assistência ao Desenvolvimento

| Campo | Valor |
|---|---|
| Ferramenta | Claude (Anthropic) |
| Modelo | claude-sonnet-4-6 |
| Acesso | claude.ai (interface web, projeto dedicado) |
| Período de uso | junho 2026 |

### Finalidades

| Etapa | Finalidade |
|---|---|
| Desenvolvimento dos scripts | Geração e revisão de src/01-clean.py, src/02-extract-triples.py, src/03-build-kg.py, src/04-query.py |
| Análise dos dados brutos | Identificação de padrões de limpeza nos arquivos data/raw/*.txt |
| Estruturação do pipeline | Organização do repositório e definição da sequência de etapas |
| Redação do artigo | Revisão estilística — texto escrito pelo autor e refinado com auxílio da ferramenta |
| Notebook | Geração de notebooks/experiment.ipynb |

### Observações

- A avaliação Likert foi realizada exclusivamente pelo autor
- Todas as decisões metodológicas (tipos de relação, critérios de avaliação, escopo do corpus) foram tomadas pelo autor
- Claude não teve acesso aos dados brutos de reviews nem aos resultados do experimento

---

## 2. OpenAI API — Extração de Triplas e Consulta ao Grafo

| Campo | Valor |
|---|---|
| Ferramenta | OpenAI API |
| Modelo | gpt-4o-mini |
| Temperatura | 0 (determinístico) |
| Acesso | API direta, sem frameworks de orquestração |
| Período de uso | junho 2026 |

---

### 2.1 Script 02-extract-triples.py

**Finalidade:** extração de triplas semânticas dos reviews processados.

**System Prompt:**

```
You are a fashion domain expert specialized in knowledge graph construction.
Your task is to extract semantic triples from fashion show reviews.

Definition being used:
A fashion trend is a recurring semantic pattern — expressed by entities
(garments, colors, materials, silhouettes, cultural references) and relations
between them — that shows increased frequency and co-occurrence in specialized
publications within a defined time interval, being recognizable and validatable
by domain experts.

Extract triples in the format:
{"subject": "entity", "relation": "RELATION_TYPE", "object": "entity"}

Use clear relation types such as:
- USES_MATERIAL (e.g., collection USES_MATERIAL organza)
- REFERENCES_CULTURE (e.g., collection REFERENCES_CULTURE 1970s)
- FEATURES_SILHOUETTE (e.g., collection FEATURES_SILHOUETTE oversized)
- ASSOCIATED_WITH (e.g., silhouette ASSOCIATED_WITH femininity)
- DESIGNED_BY (e.g., collection DESIGNED_BY designer_name)
- PRESENTED_AT (e.g., collection PRESENTED_AT London Fashion Week)
- USES_COLOR (e.g., collection USES_COLOR burgundy)
- INSPIRED_BY (e.g., collection INSPIRED_BY artist_name)
- CO_OCCURS_WITH (e.g., material CO_OCCURS_WITH technique)

Rules:
- Extract only what is explicitly stated in the text
- Use concise, lowercase entities (except proper nouns)
- Return ONLY a valid JSON array, no explanations, no markdown
- Extract between 10 and 25 triples per review
```

**User Prompt (aplicado a cada review):**

```
Extract semantic triples from this fashion show review:

[conteúdo do review processado]
```

---

### 2.2 Script 04-query.py — Condição A (LLM-only)

**Finalidade:** geração de respostas baseadas em texto bruto.

**Prompt:**

```
You are a fashion analyst. Read the following fashion show review and answer
the question. Answer based only on what is explicitly stated in the text.

Review:
[texto bruto do review]

Question: [pergunta de avaliação]
```

---

### 2.3 Script 04-query.py — Condição B (KG+LLM)

**Finalidade:** geração de respostas baseadas no grafo de conhecimento.

**Prompt:**

```
You are a fashion analyst with access to a structured knowledge graph.
The knowledge graph contains semantic triples extracted from fashion show reviews.
Use the knowledge graph to answer the question with explicit references to the relations.

Knowledge Graph (semantic triples):
[subgrafo em JSON]

Question: [pergunta de avaliação]

Answer based only on what is explicitly represented in the knowledge graph.
Reference specific entities and relations from the graph in your answer.
```

---

### 2.4 Perguntas de Avaliação Utilizadas

- **P1** (intra-documento): "What are the dominant trends in this collection?"
- **P2** (intra-documento): "What relations between elements characterize these trends?"
- **P3** (inter-documento): "What trends dominated London AW25?"

---

## 3. Parâmetros de Reprodutibilidade

| Parâmetro | Valor |
|---|---|
| Modelo de extração de triplas | gpt-4o-mini |
| Modelo de consulta | gpt-4o-mini |
| Temperatura | 0 |
| Max tokens | 1000 |
| Plataforma de execução | OpenAI API direta |
| Ambiente | Google Colab |

> **Nota:** Temperatura=0 maximiza o determinismo, mas variações mínimas entre versões
> do modelo gpt-4o-mini podem ocorrer. Os artefatos originais do experimento estão
> preservados em `results/`.
