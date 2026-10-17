import streamlit as st
import psycopg2
import ollama

# Configuration
MODEL_NAME = "nomic-embed-text"
DB_CONFIG = {
    "dbname": "products",
    "user": "pgvector",
    "password": "pgvectorpasswd",
    "host": "0.0.0.0",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

st.set_page_config(page_title="PostgreSQL Vector Search with Ollama", layout="wide")
st.title("📚 Electronics Product Vector Search & Processing with Ollama & Postgres")

# Sidebar - Settings & Statistics
st.sidebar.header("⚙️ Configuration & Status")
st.sidebar.write(f"**Embedding Model:** `{MODEL_NAME}`")

# Check DB connection & un-embedded stats
try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM electronics WHERE embedding IS NULL;")
    missing_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM electronics WHERE embedding IS NOT NULL;")
    embedded_count = cur.fetchone()[0]
    cur.close()
    conn.close()

    st.sidebar.metric(label="Embedded Description", value=embedded_count)
    st.sidebar.metric(label="Description Pending Embedding", value=missing_count)

except Exception as e:
    st.sidebar.error(f"Database Connection Error: {e}")
    missing_count = 0

# --- TAB 1: SEARCH QUOTES ---
tab1, tab2 = st.tabs(["🔍 Semantic Search", "⚙️ Generate Embeddings"])

with tab1:
    st.header("Search Description by Meaning")
    search_query = st.text_input("Enter a query, sentiment, or topic:", placeholder="e.g., enterprise laptop")
    top_k = st.slider("Number of results", min_value=1, max_value=10, value=3)

    if st.button("Search", type="primary"):
        if not search_query.strip():
            st.warning("Please enter a text query to search.")
        else:
            with st.spinner("Generating embedding and searching PostgreSQL..."):
                try:
                    # 1. Embed query via Ollama
                    response = ollama.embed(model=MODEL_NAME, input=search_query)
                    query_vector = response['embeddings'][0]

                    # 2. Query Postgres
                    conn = get_db_connection()
                    cur = conn.cursor()
                    sql_query = """
                        SELECT id, product, description, 1 - (embedding <=> %s::vector) AS similarity
                        FROM electronics
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s;
                    """
                    cur.execute(sql_query, (query_vector, query_vector, top_k))
                    results = cur.fetchall()
                    cur.close()
                    conn.close()

                    # 3. Display Results
                    if not results:
                        st.info("No matching description found.")
                    else:
                        st.subheader(f"Top {len(results)} Matches:")
                        for row_id, product, description, similarity in results:
                            with st.container():
                                st.markdown(f"**Features:** *\"{description}\"*")
                                st.markdown(f"**Product:** {product} | **Similarity Score:** `{similarity:.4f}`")
                                st.divider()

                except Exception as e:
                    st.error(f"Search failed: {e}")

# --- TAB 2: GENERATE EMBEDDINGS ---
with tab2:
    st.header("Batch Embedding Processing")
    st.write("Generate embeddings for database rows where the `embedding` column is `NULL`.")

    if missing_count == 0:
        st.success("All description in the database already have embeddings!")
    else:
        batch_size = st.number_input("Batch Size", min_value=1, max_value=200, value=50)
        
        if st.button("Start Generating Embeddings"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                conn = get_db_connection()
                cur = conn.cursor()

                cur.execute("""
                    SELECT id, description 
                    FROM electronics 
                    WHERE embedding IS NULL 
                    LIMIT %s;
                """, (batch_size,))
                rows = cur.fetchall()

                if not rows:
                    st.info("No missing embeddings found.")
                else:
                    total_rows = len(rows)
                    for i, (row_id, quote_text) in enumerate(rows):
                        if quote_text:
                            # Embed with Ollama
                            response = ollama.embed(model=MODEL_NAME, input=quote_text)
                            embedding_vector = response['embeddings'][0]

                            # Update Postgres
                            cur.execute("""
                                UPDATE electronics
                                SET embedding = %s::vector 
                                WHERE id = %s;
                            """, (embedding_vector, row_id))

                        # Update progress UI
                        progress = (i + 1) / total_rows
                        progress_bar.progress(progress)
                        status_text.text(f"Processed {i + 1} of {total_rows} description ...")

                    conn.commit()
                    cur.close()
                    conn.close()

                    st.success(f"Successfully updated embeddings for {total_rows} description!")
                    st.rerun()

            except Exception as e:
                st.error(f"An error occurred during embedding processing: {e}")
