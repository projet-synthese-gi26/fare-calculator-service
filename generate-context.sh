#!/bin/bash

OUTPUT_FILE="context.txt"
SCRIPT_NAME=$(basename "$0")

echo "# Contexte du Projet Flask : $(basename "$(pwd)")" > "$OUTPUT_FILE"
echo "Généré le : $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "## Arborescence du projet" >> "$OUTPUT_FILE"
echo "\`\`\`" >> "$OUTPUT_FILE"

if command -v tree &> /dev/null; then
    tree -L 4 --dirsfirst -I "$SCRIPT_NAME|$OUTPUT_FILE|__pycache__|venv|.git|dist|migrations" >> "$OUTPUT_FILE"
else
    echo "Commande 'tree' manquante. Utiliser : sudo apt install tree" >> "$OUTPUT_FILE"
    ls -R >> "$OUTPUT_FILE"
fi

echo "\`\`\`" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "## Fichiers Clés et Config" >> "$OUTPUT_FILE"

add_key_file() {
    if [ -f "$1" ]; then
        echo "" >> "$OUTPUT_FILE"
        echo "### Fichier : \`$1\`" >> "$OUTPUT_FILE"
        lang="${1##*.}"
        case "$lang" in
            py) lang="python" ;;
            json) lang="json" ;;
            cfg|ini|env) lang="ini" ;;
        esac
        echo "\`\`\`$lang" >> "$OUTPUT_FILE"
        cat "$1" >> "$OUTPUT_FILE"
        echo "\`\`\`" >> "$OUTPUT_FILE"
    fi
}

add_key_file "requirements.txt"
add_key_file "app.py"
add_key_file ".env.example"
add_key_file "config.py"
add_key_file "wsgi.py"

echo "" >> "$OUTPUT_FILE"
echo "## Aperçu des fichiers sources" >> "$OUTPUT_FILE"

find . -type f -name "*.py" ! -path "./venv/*" ! -path "./__pycache__/*" -print0 | while IFS= read -r -d '' file; do
    if [[ "$(file -b --mime-type "$file")" == text/* ]]; then
        echo "" >> "$OUTPUT_FILE"
        echo "### Fichier : \`$file\`" >> "$OUTPUT_FILE"
        echo "\`\`\`python" >> "$OUTPUT_FILE"
        cat "$file" >> "$OUTPUT_FILE"
        echo "\`\`\`" >> "$OUTPUT_FILE"
    fi
done

echo "✅ Fichier '$OUTPUT_FILE' généré avec succès !"
