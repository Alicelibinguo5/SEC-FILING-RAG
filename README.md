# SEC Filing RAG

Question-answering over NVIDIA 10-K PDFs with page citations.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Configure environment variables:

```bash
cp .env.example .env
```

3. Place 10-K PDFs under `data/pdfs/`.

4. Build the vector index:

```bash
python -m ingestion.ingest
```

5. Launch the UI:

```bash
streamlit run app/streamlit_app.py
```

## Environment variables

- `OPENAI_API_KEY`: required for OpenAI embeddings and chat
- `EMBEDDING_PROVIDER`: `openai` (default) or `sentence-transformers`
- `EMBEDDING_MODEL`: defaults to `text-embedding-3-small`
- `CHAT_MODEL`: defaults to `gpt-4.1-mini`
- `CHROMA_DIR`: defaults to `./chroma_db`
- `CHROMA_COLLECTION`: defaults to `sec_filings`
- `PDF_DIR`: defaults to `./data/pdfs`

## Notes

- Ingestion first detects filing sections such as `Item 1A. Risk Factors` and `Item 7. Management's Discussion and Analysis`.
- Sections are chunked into roughly 500-token windows with 100-token overlap.
- Each chunk stores filename, section title, and page-span metadata for citation and debugging.
- Answers cite supporting PDF pages as `[filename p.X]` or `[filename pp.X-Y]`.
