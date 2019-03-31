pandoc \
    manual.md \
    --to=html5 \
    --output=manual.html \
    --template=manual-template.html \
    --standalone \
    --css=base.css \
    --css=manual.css \
    --toc \
    --number-sections \
    -V "title:gTimeCalc Manual" \
    -V "toctitle:Table of contents" \
    -V "pagetitle:gTimeCalc Manual"
