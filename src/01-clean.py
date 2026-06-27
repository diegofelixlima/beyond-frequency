"""
01-clean.py
-----------
Limpeza dos reviews brutos coletados do The Impression.

Entrada:  data/raw/*.txt
Saída:    data/processed/*.txt

Lógica:
- Remove navegação do site (header e footer)
- Mantém o conteúdo editorial: título, vibe, corpo do review, quote e wrap up
- Início do conteúdo: linha que contém "Review of"
- Fim do conteúdo: linha que contém "See The Collection"

Ferramenta de IA utilizada na análise de padrões: Claude (Anthropic)
Modelo: claude-sonnet-4-6 | Data: junho 2026
"""

import os

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"


def clean_review(text):
    """
    Extrai o conteúdo útil de um review bruto.
    Retorna o texto limpo ou None se os marcadores não forem encontrados.
    """
    lines = text.splitlines()

    start_index = None
    end_index = None

    for i, line in enumerate(lines):
        if "Review of" in line and start_index is None:
            # Inclui a linha anterior (título do review)
            start_index = max(0, i - 1)
        if "See The Collection" in line and end_index is None:
            end_index = i

    if start_index is None or end_index is None:
        return None

    cleaned_lines = lines[start_index:end_index]

    # Remove linhas vazias excessivas (mais de 2 seguidas)
    result = []
    blank_count = 0
    for line in cleaned_lines:
        stripped = line.strip()
        if stripped == "":
            blank_count += 1
            if blank_count <= 2:
                result.append("")
        else:
            blank_count = 0
            result.append(stripped)

    return "\n".join(result).strip()


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".txt") and f != ".gitkeep"]

    print(f"Arquivos encontrados em {RAW_DIR}: {len(raw_files)}\n")

    success = 0
    failed = 0

    for filename in sorted(raw_files):
        raw_path = os.path.join(RAW_DIR, filename)
        processed_path = os.path.join(PROCESSED_DIR, filename)

        with open(raw_path, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

        cleaned = clean_review(raw_text)

        if cleaned is None:
            print(f"[ERRO] Marcadores não encontrados: {filename}")
            failed += 1
            continue

        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        word_count = len(cleaned.split())
        print(f"[OK] {filename} → {word_count} palavras")
        success += 1

    print(f"\nConcluído: {success} processados, {failed} com erro.")


if __name__ == "__main__":
    main()
