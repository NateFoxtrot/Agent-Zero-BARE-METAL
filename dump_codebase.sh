#!/bin/bash
cd ~/agent-zero
OUTPUT_FILE="agent_zero_codebase.txt"

echo "Dump of Agent Zero Codebase" > "$OUTPUT_FILE"
echo "Generated on $(date)" >> "$OUTPUT_FILE"
echo "----------------------------------------" >> "$OUTPUT_FILE"

# Find relevant files: Python, Shell, Docker, JSON, Markdown, YAML
# We exclude venv, pycache, and git directories
find . -maxdepth 5 -not -path '*/.*' -not -path '*/__pycache__*' -not -path '*/venv*' -not -path '*/node_modules*' \
    \( -name "*.py" -o -name "*.sh" -o -name "*Dockerfile*" -o -name "requirements.txt" -o -name "*.md" -o -name "*.json" -o -name "*.yml" \) | sort | while read -r file; do
    
    echo "FILE_START: $file" >> "$OUTPUT_FILE"
    echo "Content of $file:" >> "$OUTPUT_FILE"
    echo "----------------------------------------" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "FILE_END: $file" >> "$OUTPUT_FILE"
    echo "----------------------------------------" >> "$OUTPUT_FILE"
done

echo "Dump complete. Output saved to ~/agent-zero/$OUTPUT_FILE"
