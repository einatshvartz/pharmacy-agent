# Pharmacy Agent (Wonderful - Home Assignment)

Real-time, stateless conversational AI pharmacy agent built with FastAPI + OpenAI GPT-5.
The agent supports Hebrew and English, streams responses, and uses internal tools for pharmacy workflows.

---

## What this project includes

- **Stateless** agent (no server-side conversation memory)
- **Real-time streaming** responses (`/chat`)
- **Tool-based workflows** (internal DB only)
- **Safety guardrails** (no medical advice, no diagnosis, no purchase encouragement)
- **Observability** (server logs for tool usage + flow trace)

---

## Repository structure

- `app/main.py` — FastAPI server (health + chat endpoints)
- `app/agent.py` — GPT-5 streaming agent + tool-calling orchestration
- `app/tools.py` — Internal tools over the in-memory DB 
- `app/db.py` — In-memory DB (users, medications)
- `test_tools.py` — Basic unit tests for tools

---

## Requirements

- Python 3.10+
- An OpenAI API key with access to GPT-5

---

## Setup - for a local python environment

1. Create and activate a virtual environment
2. Install dependencies
3. Set environment variables
4. Run the server

Example (PowerShell):

- powershell
- python -m venv venv
- .\venv\Scripts\Activate.ps1
- pip install -r requirements.txt

- $Env:OPENAI_API_KEY="valid OPENAI_API_KEY"
- uvicorn app.main:app --port 8002

---

## Docker

The project is fully containerized and can be run using Docker, without requiring
a local Python environment.

### Prerequisites
- Docker Desktop (Windows / macOS / Linux)
- An OpenAI API key with access to GPT-5

### Build the Docker image

From the project root directory:

1) Build Docker:
    docker build -t pharmacy-agent:latest 
2) Run the container:
    docker run --rm -p 8002:8002 -e OPENAI_API_KEY=YOUR_KEY_HERE pharmacy-agent:latest

**The API will be available at:**
Health check: http://localhost:8002/health
Swagger UI: http://localhost:8002/docs

---

## Multi-Step Agent Flows

The agent is designed to execute professional, deterministic multi-step workflows, similar to how a real pharmacy staff member would assist a customer.
- *Note:* A multi-step flow may involve one or multiple tools.
  The “multi-step” nature refers to validation, intent detection, tool orchestration, and response composition — not necessarily multiple tool calls
- Each flow starts with a mandatory User Gate, followed by intent-driven tool usage and a structured response.

---

### Multi-Step Flow 1 — Medication Facts

#### Purpose:
Provide factual information about a medication: active ingredient, dosage, usage instructions, and safety information.

#### Use case examples:
- “What is the active ingredient in Paracetamol?”  
- “What are the usage instructions for Ibuprofen?”

#### Expected sequence & Tool usage:

0) **Tool call #0 : User Gate (deterministic):**
- Run `get_user(user_id)`.
- If the user is not found → return an appropriate deterministic message in the user’s language and stop.

1) **Intent detection (LLM):**
- Identify that the user is requesting factual medication information (active ingredient / dosage / usage / safety).
- If the medication name is missing or ambiguous → ask a short clarifying question (without using any tool).

2) **Tool call #1:**
- Call `get_medication_by_name(name=<drug>)`.

3) **Error handling:**  
- If a NOT_FOUND error is returned → respond with a deterministic “medication not found in the internal database” message and stop.

4) **Response composition:**
- Answer strictly using only the fields returned from the internal database, such as:
    - active_ingredient
    - dosage_instruction (dose_amount, frequency, max_daily)
    - usage_instructions
    - safety_instructions
- Enforce policy constraints:
    - No medical advice, diagnosis, treatment recommendations, or purchase encouragement. 
    - Respond in the user's language (Hebrew or English).

---

### Multi-Step Flow 2 — Prescription Eligibility

#### Purpose:
Professionally verify both:
 - Whether the medication requires a prescription
 - Whether the user has a prescription for this medication

#### Use case examples:
- “Do I have a prescription for Metformin?”  
- “Does Amoxicillin require a prescription?”

#### Expected sequence & Tool usage:

0) **Tool call #0 : User Gate (deterministic):**
- Run `get_user(user_id).`
- If the user is not found → return an appropriate deterministic message in the user’s language and stop.

1) **Intent detection (LLM):**
- Identify that the user is asking about a prescription-related query (required / do I have one). 
- If the medication name is missing or ambiguous → ask a short clarifying question (without using any tool).

2) **Tool call #1:**
- Call `check_prescription(user_id=<user_id>, name=<drug>)`.

3) **Response composition:**
- Return a factual response including:
   - Whether the medication requires a prescription.
   - Whether the specific user has a prescription on file.
- Enforce policy constraints:
    - Do not advise how to obtain a prescription and refer to a pharmacist or doctor if asked.
    - No medical advice, diagnosis, treatment recommendations, or purchase encouragement. 
    - Respond in the user's language (Hebrew or English).

---

### Multi-Step Flow 3 — Inventory + Prescription  
*Note: This flow demonstrates the agent's use of multiple (non-detemenistic) tools.*

#### Purpose:
The user wants to know both medication availability in stock and prescription status (including user-specific eligibility).

#### Use case examples:
- “Do you have Amoxicillin in stock, and can I get it?”  
- “Is Metformin available, and do I have a prescription?”

#### Expected sequence & Tool usage:

0) **Tool call #0 : User Gate (deterministic):**
- Run `get_user(user_id).`
- If the user is not found → return an appropriate deterministic message in the user’s language and stop.

1) **Intent detection (LLM):**
- Identify that this is a combined request (inventory + prescription).
- If the medication name is missing or ambiguous → ask a short clarifying question (without using any tool).

2) **Tool call #1 — Inventory:**
- Call `check_stock(name=<drug>)`.

3) **Tool call #2 — Prescription eligibility:**
- Call check_prescription(user_id=<user_id>, name=<drug>).

4) **Response composition (merge results):**
- Merge both results into a single, clear answer:
   - Stock availability.
   - Prescription requirement.
   - User’s prescription status.
- Enforce policy constraints:
    - Do not advise how to obtain a prescription and refer to a pharmacist or doctor if asked.
    - No medical advice, diagnosis, treatment recommendations, or purchase encouragement. 
    - Respond in the user's language (Hebrew or English).

---

### Why These Qualify as Multi-Step Flows

- Each flow mirrors a real pharmacy interaction.
- Each flow includes validation, decision-making, tool execution, and controlled termination.
- The agent demonstrates tool orchestration rather than single-shot answers.
- All flows are stateless, deterministic, and observable via logs.

---

### Evidence – Multi-Step Flow Demonstrations

The following screenshots demonstrate real conversations with the agent,
executed via Swagger UI, and show the corresponding tool usage in server logs.

- Flow 1 – Medication Facts  
- Flow 2 – Prescription Eligibility  
- Flow 3 – Inventory + Prescription  

See the `/screenshots` directory for visual evidence.


