# UI components for Streamlit app
import streamlit as st

def render_sidebar(unique_values, schema_docs, example_queries):
    st.header("📈 Data Overview")
    st.write(f"**Companies:** {len(unique_values['companies'])}")
    st.write(f"**Countries:** {len(unique_values['countries'])}")
    st.write(f"**Date Range:** {unique_values['date_range']}")
    st.write(f"**Total Records:** {unique_values.get('total_records', 'N/A')}")

    st.subheader("🏢 Companies")
    st.write(", ".join(unique_values["companies"][:10]) + ("..." if len(unique_values["companies"]) > 10 else ""))
    with st.expander("Show All Companies"):
        st.markdown("<br>".join(unique_values["companies"]), unsafe_allow_html=True)

    st.subheader("🌍 Countries")
    st.write(", ".join(unique_values["countries"]))

    st.subheader("📋 Accounts")
    st.write(", ".join(unique_values["accounts"][:10]) + ("..." if len(unique_values["accounts"]) > 10 else ""))
    with st.expander("Show All Accounts"):
        st.markdown("<br>".join(unique_values["accounts"]), unsafe_allow_html=True)

    st.subheader("📚 Schema")
    with st.expander("View Schema"):
        st.markdown(schema_docs)

    st.subheader("💡 Example Queries")
    for i, query in enumerate(example_queries):
        if st.button(query, key=f"example_{i}"):
            st.session_state.example_prompt = query
            st.rerun()

def render_chat(messages):
    st.subheader("💬 Chat")
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
