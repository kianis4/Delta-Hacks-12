# Juris - The AI Legal Defender

> **"Access to Justice, Simplified."**

## 📖 Introduction
**Juris** is an Agentic Retrieval-Augmented Generation (RAG) system designed to level the playing field for tenants and low-income individuals facing legal challenges. It is **not** a lawyer. It is a highly sophisticated, autonomous research and drafting aide that empowers users to understand their rights and generate valid legal documents for review.

In 2026, the legal gap is widening. Juris bridges this gap by using state-of-the-art **Agentic AI** to turn complex legal jargon into actionable defense.

---

## 🏗️ Architecture: The "Agentic" Difference
Traditional RAG just retrieves text and summarizes it. **Juris** uses an **Agentic Workflow** that mirrors how a human paralegal works:

1.  **Orchestrator (The Brain)**: A master agent that breaks down the user's problem.
2.  **Triage Agent**: Determines the domain (e.g., "Eviction" vs "Harassment").
3.  **Research Agent**: Autonomously searches our **MongoDB Atlas Vector Store** for specific laws (e.g., *Residential Tenancies Act 2006*).
    *   *Self-Correction*: If the first search fails, it rephrases the query and tries again.
4.  **Drafter Agent**: Uses the research to fill out official government forms (e.g., N12, T6).
5.  **Critic Agent**: A "Devil's Advocate" agent that reviews the draft for factual hallucinations before showing it to the user.

---

## 🛠️ The 2026 Tech Stack (Winner's Configuration)

We have selected this stack based on **State-of-the-Art (SOTA) 2026 Benchmarks**:

| Component | Choice | Rationale |
| :--- | :--- | :--- |
| **Embeddings** | **Voyage AI (`voyage-law-2`)** | Benchmarks show it outperforms OpenAI/Gemini by ~10% on legal retrieval. It handles the nuance of "legalese" better than general models. |
| **LLM Reasoning** | **Google Gemini 1.5 Pro** | Huge context window (2M tokens) allows us to dump entire case files into context for "reasoning". |
| **Vector DB** | **MongoDB Atlas** | **Hybrid Search**: We need keyword search (for exact legal clause numbers) AND vector search (for concepts). Atlas does both natively. |
| **Orchestration** | **LangGraph** | Legal logic is cyclical and strict ("If A then B"). LangGraph offers better control than CrewAI's open-ended roleplay. |
| **Privacy** | **Tailscale** | Allows us to demo a distributed "Local Mesh" where sensitive legal docs never leave the user's devices (optional advanced feature). |

---

## ⚖️ Ethics & Liability (Crucial)

**We are "Aiding", not "Replacing".**

To ensure we are ethical and safe, Juris enforces the following:

1.  **The "Red Box" Disclaimer**:
    > *WARNING: Juris is an AI research tool, not a law firm. This system produces drafts for informational purposes only. You must verify all citations with a qualified legal professional.*
2.  **Human-in-the-Loop**: The system never "auto-sends" an email or files a form. It *drafts*, and the user must manually review and hit "Send".
3.  **Citation Transparency**: Every sentence in a drafted letter includes a footnote linking back to the exact source text in the *Tenancies Act*.

---

## 🚀 Pros & Cons

### Pros
*   **Massive Cost Savings**: A paralegal costs $150/hr. Juris costs $0.05 per run.
*   **Empowerment**: Users walk into court knowing exactly which section of the law protects them.
*   **Availability**: 24/7 assistance for emergencies (e.g., "Landlord just locked me out").

### Cons
*   **Hallucination Risk**: AI can invent precedents. *Mitigation: The "Critic Agent" layer.*
*   **Complexity bias**: Users might trust the "smart machine" too much. *Mitigation: Strongly worded UI warnings.*
*   **No "Strategy"**: Juris can execute tasks, but it cannot devise a complex multi-year litigation strategy like a human can.

---
### Troubleshooting
*   **Ingestion is Slow**: Voyage AI's free tier has a **3 RPM (Request Per Minute)** limit. The ingestion script sleeps for 25s between batches to respect this. This is normal.
*   **API Errors**: Ensure `VOYAGE_API_KEY` and `MONGODB_URI` are correct in `.env`.

## 🗺️ Roadmap

### Phase 1: The Core (Hackathon MVP)
- [ ] Ingest *Ontario Residential Tenancies Act* into MongoDB.
- [ ] Build the **Triage -> Research -> Draft** LangGraph loop.
- [ ] Create a simple Next.js frontend to upload a "Notice to Quit" and get a "Response Letter".

### Phase 2: The Network (Post-MVP)
- [ ] Add **Tailscale** for secure document sharing with a real pro-bono lawyer.
- [ ] Add **Voice Mode** (ElevenLabs) for accessibility.

---

## 💻 Getting Started

```bash
# Clone the monorepo
git clone https://github.com/your-team/juris.git

# Install dependencies
cd juris
npm install

# Set up secrets
cp .env.example .env
# (Add GEMINI_API_KEY, MONGODB_URI, VOYAGE_API_KEY)

# Run the Agent
cd agent
python agent_graph.py

# Run the UI
cd web
npm run dev
```
