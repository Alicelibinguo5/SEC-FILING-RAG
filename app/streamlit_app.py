from __future__ import annotations

import streamlit as st

from app.service import FilingQAService


st.set_page_config(page_title="NVIDIA 10-K QA", page_icon=":page_facing_up:", layout="wide")


@st.cache_resource
def get_qa_service() -> FilingQAService:
    return FilingQAService()


def main() -> None:
    st.title("NVIDIA 10-K Filing Q&A")
    st.caption("Ask questions about NVIDIA filings and get grounded answers with page citations.")

    with st.sidebar:
        st.subheader("Example questions")
        st.write("- What risks did NVIDIA mention?")
        st.write("- What drove revenue growth?")
        st.write("- What does management say about the AI market?")

    question = st.text_input(
        "Question",
        placeholder="What risks did NVIDIA highlight in its latest 10-K filing?",
    )

    if not question:
        return

    try:
        service = get_qa_service()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    try:
        with st.spinner("Retrieving relevant filing passages..."):
            answer, chunks = service.answer_question(question)
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    st.subheader("Answer")
    st.write(answer)

    with st.expander("Retrieved sources"):
        for chunk in chunks:
            page_label = f"p.{chunk.start_page}" if chunk.start_page == chunk.end_page else f"pp.{chunk.start_page}-{chunk.end_page}"
            st.markdown(f"**{chunk.filename} | {chunk.section_title} | {page_label}**")
            st.write(chunk.text)


if __name__ == "__main__":
    main()
