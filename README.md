# Convert OpenAI Deep Research to PDF

Or any Markdown document for that matter.

Makes (somewhat) nice footnotes from links. And puts an appendix with QR-codes at the bottom of the document.

Requirements:

- [uv](https://github.com/astral-sh/uv) - uv will manage [Python](https://www.python.org) for you.
- [pandoc](https://pandoc.org/)
- [pdflatex](https://www.latex-project.org/get/)

Installing the requirements on macOS:

```bash
# Maybe first install `brew` from https://brew.sh
brew install pandoc
brew install basictex

# Basictex misses newunicodechar, so update the LaTeX package manager, and get the package.
sudo tlmgr update --self 
sudo tlmgr install newunicodechar
```

Create an input.md file with the markdown content.

```bash
uv run markdown-qr.py
open output.pdf
```
