# SEC Filing RAG: Interview Framing

This project is stronger in interviews if it is presented as an information retrieval and grounding system, not just a chatbot over PDFs.

## Project summary

I built a retrieval-augmented generation system for NVIDIA 10-K filings that extracts filing content, chunks it into searchable units, stores embeddings in a vector database, retrieves relevant evidence for a user question, and generates answers with page-level citations.

The goal was to make answers more trustworthy by grounding them in the source filing rather than relying on the language model alone.

## Strong interview framing

Instead of saying:

"I built a chatbot for SEC PDFs."

Say:

"I built a RAG pipeline for SEC filings that focuses on grounded answers, section-aware retrieval, and page-level citations. I improved retrieval quality by detecting filing sections first, chunking within those sections, and preserving source metadata through ingestion, retrieval, and answer generation."

## What this project demonstrates

- End-to-end system design across ingestion, indexing, retrieval, and generation
- Practical use of vector search with Chroma
- Document parsing with PyMuPDF
- Metadata-aware retrieval for better accuracy
- Prompt design for grounded generation with citations
- Clean modular Python architecture that is easy to extend

## Accuracy improvements to talk about

If asked how accuracy can be improved in general, the strongest answer is to discuss the full pipeline.

### 1. Better parsing

Accuracy starts with extraction quality. SEC filings often contain repeated headers, footers, tables, and broken line formatting, so noisy parsing directly hurts retrieval.

Improvements:

- Prefer SEC HTML filings when available instead of relying only on PDFs
- Remove repeated headers and footers
- Clean table-of-contents pages
- Preserve section boundaries and heading structure
- Handle tables separately from narrative text

### 2. Better retrieval

Retrieval quality matters more than just choosing a stronger LLM.

Improvements:

- Detect sections such as `Item 1A. Risk Factors` and `Item 7. MD&A`
- Route questions to relevant sections before dense retrieval
- Add hybrid retrieval using keyword search plus embeddings
- Add reranking on top retrieved chunks
- Use metadata filters such as company, filing type, fiscal year, and section

### 3. Better chunking

Chunking should follow the document structure rather than arbitrary page boundaries.

Improvements:

- Chunk inside sections instead of by page
- Split around paragraph and subsection boundaries when possible
- Keep chunk sizes in the 400 to 600 token range
- Preserve page-span metadata for every chunk
- Retrieve small chunks but optionally expand to surrounding context for generation

### 4. Better grounding

Generation should be constrained so the model answers only from retrieved evidence.

Improvements:

- Require citations for each substantive claim
- Instruct the model to say when evidence is insufficient
- Avoid unsupported summarization beyond the retrieved context
- Add a verification pass to check whether claims are actually supported by cited chunks

### 5. Better evaluation

This is the most important improvement for interviews because it shows engineering rigor.

Improvements:

- Create a labeled question set over NVIDIA filings
- Include gold answers and gold citations
- Measure retrieval recall@k
- Measure citation accuracy
- Measure answer faithfulness and completeness
- Use evaluation results to compare chunking, embedding models, and retrieval strategies

## Best concise explanation in an interview

"The main lesson from this project is that RAG accuracy depends much more on document quality, chunking strategy, and retrieval design than on prompt tuning alone. I improved the pipeline by making retrieval section-aware and preserving page metadata, and the next step would be to add evaluation, hybrid retrieval, and reranking."

## Resume-style bullets

- Built a Python RAG system for NVIDIA 10-K filings using PyMuPDF, Chroma, embeddings, and an LLM to answer natural-language questions with page-level citations.
- Improved retrieval quality by introducing section-aware ingestion and chunking, preserving filing metadata such as section title and page spans through indexing and answer generation.
- Designed a modular ingestion and retrieval pipeline that supports extension to hybrid search, reranking, and evaluation-driven accuracy improvements.

## Strong answers to common follow-up questions

### What was the hardest part?

"The hardest part was making retrieval accurate enough for long financial documents. Filing content spans many pages, section boundaries matter, and naive page-based chunking leads to weak recall. I addressed that by moving to section-aware chunking and carrying page metadata through the pipeline."

### How would you improve it next?

"I would add a labeled evaluation set, hybrid retrieval with keyword plus dense search, and a reranking stage. That would make it easier to measure which changes actually improve grounded answer quality."

### Why is this more than a demo?

"Because the system is designed around source grounding and measurable retrieval quality. It is not just generating plausible answers; it is retrieving evidence from filings and tying responses back to specific pages."
