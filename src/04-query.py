"""
04-query.py
-----------
Experimento comparativo: LLM-only vs KG+LLM.

Para cada review e para o corpus completo, as perguntas são feitas em duas condições:
- Condição A (LLM-only): texto bruto enviado diretamente ao LLM
- Condição B (KG+LLM): subgrafo relevante consultado e enviado ao LLM

Perguntas intra-documento (por review):
- P1: What are the dominant trends in this collection?
- P2: What relations between elements characterize these trends?

Pergunta inter-documento (corpus completo):
- P3: What trends dominated London AW25?

Entrada:  data/processed/*.txt (Condição A)
          data/processed/kg/fashion_kg.graphml (Condição B)
Saída:    results/condition_a/*.txt
          results/condition_b/*.txt

Modelo: gpt-4o-mini | Temperatura: 0
Ferramenta de IA utilizada: Claude (Anthropic)
Modelo Claude: claude-sonnet-4-6 | Data: junho 2026
"""

import os
import json
import networkx as nx
from openai import OpenAI

PROCESSED_DIR = "data/processed"
KG_FILE = "data/processed/kg/fashion_kg.graphml"
RESULTS_A = "results/condition_a"
RESULTS_B = "results/condition_b"

QUESTIONS = {
    "P1": "What are the dominant trends in this collection?",
    "P2": "What relations between elements characterize these trends?",
}
QUESTION_P3 = "What trends dominated London AW25?"


# ─── Condição A: LLM-only ────────────────────────────────────────────────────

def query_llm_only(client, text, question):
    """
    Envia o texto bruto + pergunta diretamente ao LLM.
    """
    prompt = f"""You are a fashion analyst. Read the following fashion show review and answer the question.
Answer based only on what is explicitly stated in the text.

Review:
{text}

Question: {question}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


# ─── Condição B: KG+LLM ──────────────────────────────────────────────────────

def get_subgraph_context(G, source_filter=None):
    """
    Extrai o subgrafo relevante do KG como contexto estruturado para o LLM.
    Se source_filter for fornecido, filtra arestas por fonte (review específico).
    """
    triples = []
    for u, v, data in G.edges(data=True):
        if source_filter and data.get("source") != source_filter:
            continue
        triples.append({
            "subject": u,
            "relation": data.get("relation", ""),
            "object": v,
            "source": data.get("source", "")
        })
    return triples


def query_kg_llm(client, triples, question):
    """
    Envia o subgrafo estruturado + pergunta ao LLM.
    """
    kg_context = json.dumps(triples, ensure_ascii=False, indent=2)

    prompt = f"""You are a fashion analyst with access to a structured knowledge graph.
The knowledge graph contains semantic triples extracted from fashion show reviews.
Use the knowledge graph to answer the question with explicit references to the relations.

Knowledge Graph (semantic triples):
{kg_context}

Question: {question}

Answer based only on what is explicitly represented in the knowledge graph.
Reference specific entities and relations from the graph in your answer.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


# ─── Execução principal ───────────────────────────────────────────────────────

def save_result(directory, filename, question_id, condition, answer):
    """
    Salva a resposta em arquivo de texto estruturado.
    """
    os.makedirs(directory, exist_ok=True)
    output_path = os.path.join(directory, f"{filename}_{question_id}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"FILE: {filename}\n")
        f.write(f"QUESTION: {question_id}\n")
        f.write(f"CONDITION: {condition}\n")
        f.write(f"{'='*60}\n\n")
        f.write(answer)
    return output_path


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERRO] OPENAI_API_KEY não encontrada.")
        return

    client = OpenAI(api_key=api_key)

    # Carrega o grafo
    if not os.path.exists(KG_FILE):
        print(f"[ERRO] Grafo não encontrado: {KG_FILE}")
        print("Execute 03-build-kg.py primeiro.")
        return

    G = nx.read_graphml(KG_FILE)
    print(f"Grafo carregado: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas\n")

    # Lista de reviews processados
    processed_files = [
        f for f in os.listdir(PROCESSED_DIR)
        if f.endswith(".txt") and f != ".gitkeep"
    ]

    print(f"Reviews encontrados: {len(processed_files)}\n")
    print("=" * 60)

    # ── P1 e P2: Perguntas intra-documento ────────────────────────
    for filename in sorted(processed_files):
        filepath = os.path.join(PROCESSED_DIR, filename)
        base = filename.replace(".txt", "")

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        source_key = base
        subgraph_triples = get_subgraph_context(G, source_filter=source_key)

        print(f"\nReview: {filename}")
        print(f"Triplas no subgrafo: {len(subgraph_triples)}")

        for q_id, question in QUESTIONS.items():
            print(f"  [{q_id}] {question}")

            # Condição A
            answer_a = query_llm_only(client, text, question)
            save_result(RESULTS_A, base, q_id, "LLM-only", answer_a)
            print(f"    → Condição A salva")

            # Condição B
            answer_b = query_kg_llm(client, subgraph_triples, question)
            save_result(RESULTS_B, base, q_id, "KG+LLM", answer_b)
            print(f"    → Condição B salva")

    # ── P3: Pergunta inter-documento ───────────────────────────────
    print(f"\n{'='*60}")
    print(f"[P3] {QUESTION_P3}")

    # Condição A: todos os textos concatenados
    all_texts = []
    for filename in sorted(processed_files):
        filepath = os.path.join(PROCESSED_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            all_texts.append(f.read())
    full_corpus = "\n\n---\n\n".join(all_texts)

    answer_a_p3 = query_llm_only(client, full_corpus, QUESTION_P3)
    save_result(RESULTS_A, "corpus_lfw_aw25", "P3", "LLM-only", answer_a_p3)
    print("  → Condição A (P3) salva")

    # Condição B: grafo completo
    all_triples = get_subgraph_context(G)
    answer_b_p3 = query_kg_llm(client, all_triples, QUESTION_P3)
    save_result(RESULTS_B, "corpus_lfw_aw25", "P3", "KG+LLM", answer_b_p3)
    print("  → Condição B (P3) salva")

    print(f"\n{'='*60}")
    print("Experimento concluído.")
    print(f"Resultados salvos em:")
    print(f"  {RESULTS_A}/")
    print(f"  {RESULTS_B}/")


if __name__ == "__main__":
    main()
