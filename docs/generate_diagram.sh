#!/bin/bash
# Defines the input and output
INPUT_FILE="docs/architecture_diagram.mmd"
OUTPUT_FILE="docs/architecture_diagram.png"

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js to use this script."
    exit 1
fi

echo "Generating high-quality diagram..."
echo "Input: $INPUT_FILE"
echo "Output: $OUTPUT_FILE"

# Run mermaid-cli via npx
# -w 1080: Width 1080px
# -s 2: Scale factor 2 (results in 2x resolution for high quality, ~2160px width actual image)
# -b transparent: Transparent background
# -H 1080: Height 1080px (optional, often better to let it calculate based on aspect ratio, but user asked for "similar to 1080" width)
# We use -w 1080 and -s 3 to get a very high res image that looks like 1080px layout but crisp.

npx -y @mermaid-js/mermaid-cli \
  -i "$INPUT_FILE" \
  -o "$OUTPUT_FILE" \
  -w 1080 \
  -s 2 \
  -b transparent

if [ $? -eq 0 ]; then
    echo "Success! Diagram generated at $OUTPUT_FILE"
else
    echo "Error generating diagram."
    exit 1
fi
