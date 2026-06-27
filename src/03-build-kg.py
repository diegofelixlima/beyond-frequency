"""
03-build-kg.py
--------------
Construção do grafo de conhecimento a partir das triplas extraídas.

Entrada:  data/processed/triples/*.json
Saída:    data/processed/kg/fashion_kg.graphml

Tecnologia: NetworkX (grafo em memória, sem banco de dados)
Nota: NetworkX é uma simplificação para fins de reprodutibilidade.
A implementação completa da dissertação utilizará Neo4j.

Ferramenta de IA utilizada: Claude (Anthropic)
Modelo Claude: claude-sonnet-4-6 | Data: junho 2026
"""

import os
import json
import networkx as nx

TRIPLES_DIR = "data/processed/triples"
KG_DIR = "data/processed/kg"
KG_FILE = os.path.join(KG_DIR, "fashion_kg.graphml")


def build_graph(triples_dir):
    """
    Constrói um grafo direcionado a partir de todos os arquivos de triplas.
    Cada aresta carrega o tipo de relação e a fonte (marca/review).
    """
    G = nx.DiGraph()

    json_files = [
        f for f in os.listdir(triples_dir)
        if f.endswith(".json") and f != ".gitkeep"
    ]

    print(f"Arquivos de triplas encontrados: {len(json_files)}\n")

    total_triples = 0

    for filename in sorted(json_files):
        filepath = os.path.join(triples_dir, filename)
        source = filename.replace(".json", "")

        with open(filepath, "r", encoding="utf-8") as f:
            triples = json.load(f)

        for triple in triples:
            subject = triple.get("subject", "").strip()
            relation = triple.get("relation", "").strip()
            obj = triple.get("object", "").strip()

            if not subject or not relation or not obj:
                continue

            G.add_node(subject)
            G.add_node(obj)
            G.add_edge(subject, obj, relation=relation, source=source)
            total_triples += 1

        print(f"[OK] {filename} → {len(triples)} triplas adicionadas ao grafo")

    return G, total_triples


def print_stats(G):
    """
    Exibe estatísticas básicas do grafo construído.
    """
    print(f"\n--- Estatísticas do Grafo ---")
    print(f"Nós (entidades):  {G.number_of_nodes()}")
    print(f"Arestas (relações): {G.number_of_edges()}")

    # Top 10 entidades mais conectadas
    degree = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\nTop 10 entidades mais conectadas:")
    for node, deg in degree:
        print(f"  {node}: {deg} conexões")

    # Tipos de relação presentes
    relations = set(data["relation"] for _, _, data in G.edges(data=True))
    print(f"\nTipos de relação no grafo ({len(relations)}):")
    for r in sorted(relations):
        print(f"  {r}")


def main():
    os.makedirs(KG_DIR, exist_ok=True)

    G, total_triples = build_graph(TRIPLES_DIR)

    print(f"\nTotal de triplas no grafo: {total_triples}")
    print_stats(G)

    nx.write_graphml(G, KG_FILE)
    print(f"\nGrafo salvo em: {KG_FILE}")


if __name__ == "__main__":
    main()
