"""
02-extract-triples.py
---------------------
Extração de triplas semânticas dos reviews processados via OpenAI API.

Entrada:  data/processed/*.txt
Saída:    data/processed/triples/*.json

Modelo: gpt-4o-mini
Temperatura: 0 (determinístico)
Ferramenta de IA utilizada: Claude (Anthropic)
Modelo Claude: claude-sonnet-4-6 | Data: junho 2026

Variáveis de ambiente necessárias:
- OPENAI_API_KEY: chave de API da OpenAI (nunca commitar no repositório)
"""

import os
import json
from openai import OpenAI

PROCESSED_DIR = "data/processed"
TRIPLES_DIR = "data/processed/triples"

# Definição operacional de tendência de moda usada no prompt
FASHION_TREND_DEFINITION = """
A fashion trend is a recurring semantic pattern — expressed by entities 
(garments, colors, materials, silhouettes, cultural references) and relations 
between them — that shows increased frequency and co-occurrence in specialized 
publications within a defined time interval, being recognizable and validatable 
by domain experts.
"""

SYSTEM_PROMPT = f"""You are a fashion domain expert specialized in knowledge graph construction.
Your task is to extract semantic triples from fashion show reviews.

Definition being used:
{FASHION_TREND_DEFINITION}

Extract triples in the format:
{{"subject": "entity", "relation": "RELATION_TYPE", "object": "entity"}}

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
"""


def extract_triples(client, text, filename):
    """
    Envia o texto do review para o LLM e retorna as triplas extraídas.
    """
    user_prompt = f"Extract semantic triples from this fashion show review:\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    # Remove markdown code blocks se presentes
    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]

    triples = json.loads(raw_output)
    return triples


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERRO] OPENAI_API_KEY não encontrada. Configure a variável de ambiente.")
        return

    client = OpenAI(api_key=api_key)
    os.makedirs(TRIPLES_DIR, exist_ok=True)

    processed_files = [
        f for f in os.listdir(PROCESSED_DIR)
        if f.endswith(".txt") and f != ".gitkeep"
    ]

    print(f"Arquivos encontrados em {PROCESSED_DIR}: {len(processed_files)}\n")

    success = 0
    failed = 0

    for filename in sorted(processed_files):
        processed_path = os.path.join(PROCESSED_DIR, filename)
        triples_filename = filename.replace(".txt", ".json")
        triples_path = os.path.join(TRIPLES_DIR, triples_filename)

        with open(processed_path, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"Processando: {filename}")

        triples = extract_triples(client, text, filename)

        with open(triples_path, "w", encoding="utf-8") as f:
            json.dump(triples, f, ensure_ascii=False, indent=2)

        print(f"[OK] {filename} → {len(triples)} triplas extraídas")
        success += 1

    print(f"\nConcluído: {success} processados, {failed} com erro.")
    print(f"Triplas salvas em: {TRIPLES_DIR}")


if __name__ == "__main__":
    main()
