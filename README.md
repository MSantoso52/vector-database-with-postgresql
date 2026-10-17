# vector-database-with-postgresql
Integrated pgvector into PostgreSQL to enable efficient vector storage and similarity search capabilities.


https://github.com/user-attachments/assets/84d6429a-2d5c-44b3-b346-3b5dd8d15e97

---

### 1. What is a Vector Database?

A vector database is a database optimized to store, manage, and query **vector embeddings**—high-dimensional numerical arrays (often numbering from hundreds to thousands of dimensions) that represent the semantic meaning of unstructured data like text, images, audio, or video.

* **How it works:** Instead of searching by exact keywords (like traditional SQL or NoSQL databases), vector databases use **approximate nearest neighbor (ANN)** search algorithms (e.g., HNSW, IVFFlat) to find vectors that are close to each other in a multi-dimensional space, reflecting conceptual or semantic similarity.

---

### 2. Problems Solved by Vector Databases

Traditional databases struggle with unstructured data and semantic nuance. Vector databases solve several key engineering challenges:

* **Semantic Search:** Traditional text search relies on exact keyword matching (BM25/TF-IDF). If a user searches for *"inexpensive laptop,"* standard search might miss an article titled *"budget notebook."* Vector search understands that these concepts are semantically related.
* **Long-Term Memory for AI (RAG):** Large Language Models (LLMs) have static training data and token limits. Vector databases act as an external knowledge base for Retrieval-Augmented Generation (RAG), allowing LLMs to fetch relevant context dynamically.
* **Multimodal Similarity Search:** Enabling "reverse image search," audio fingerprinting, or recommendation systems where items are recommended based on user behavior patterns encoded as vectors.
* **Handling Scale:** Standard databases perform full table scans ($O(N)$ time complexity) to compare high-dimensional vectors, which becomes computationally impossible at scale. Vector databases use indexing to perform sub-linear searches efficiently.

---

### 3. Why `pgvector` Matters

`pgvector` is an open-source vector similarity search extension for PostgreSQL. It has become a game-changer for data engineers and developers for several reasons:

* **No New Database to Manage:** Instead of introducing a specialized, standalone vector database (like Pinecone, Milvus, or Qdrant) that adds operational overhead, network latency, and synchronization issues, `pgvector` lets you keep your vectors right inside your existing PostgreSQL instance.
* **Transactional Consistency (ACID):** You can store your application's relational data (users, metadata, transactional records) and vector embeddings in the **same database**, ensuring atomic transactions and simplified backups.
* **Powerful Ecosystem Integration:** Because it lives in Postgres, it integrates seamlessly with existing tools, ORMs (like SQLAlchemy, Prisma), and data frameworks (like LangChain, LlamaIndex, and dbt).
* **Cost-Efficient for Moderate to High Scale:** For many production workloads, you don't need a massive distributed vector cluster. A well-tuned Postgres instance with `pgvector` handles millions of vectors efficiently while leveraging Postgres's robust indexing (HNSW and IVFFlat) and query optimizer.

## Prerequisites
* **PostgreSQL with `pgvector` extension on podman by creating `podman-compose.yml`**
  ```nvim
  services:
    postgres:
      image: docker.io/pgvector/pgvector:17
    ---
  volumes:
    pgdata:
  
  ```
* **Create database to be used for semantic search with description as embedding**
  ```psql
  CREATE DATABASE products;

  \c products

  CREATE EXTENSION IF NOT EXISTS vector;

  CREATE TABLE electronics(
    id SERIAL PRIMARY KEY,
    product TEXT,
    description TEXT,
    embedding VECTOR(768) -- refer to nomic-embed-text
  );
  ```
* **Install ollama, psycopg2 to communicate between postgresql with local AI ollama**
  ```zsh
  python3 -m install ollama, psycopg2 --break-system-packages
  ```
* **Using `nomic-embed-text` as local model to generate embedding**
  ```zsh
  ollama pull nomic-embed-text
  ```

## Project Flow
* **Insert Data into PostgreSQL database***
* **Write vector into embedding using Ollama with `nomic-embed-text` model**
* **Using user input as interactive prompt to PostgreSQL query by find the vector with `nomic-embed-text` model**
* **Wrap it all as WEB app using Streamlit**
