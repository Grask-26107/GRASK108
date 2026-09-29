# GRASK AI — Intelligent Standards & Procurement Engine

**Smart India Hackathon 2026 | Problem Statement ID: SIH26108**  
*AI-Powered Recommendation Engine for Indian Standards (BIS) & GeM Tender Specifications*

---

## 🎯 1. The Core Problem (SIH26108)

Public procurement officers, government buyers (e.g., on **GeM** and **CPPP**), and organizational purchasers frequently struggle when drafting technical specifications for public tenders:

1. **Outdated Standards**: Tenders often reference superseded or withdrawn Indian Standards without active amendments.
2. **Missing Quality Control Orders (QCO)**: Government buyers risk floating tenders without mandating legally compulsory Scheme-I (ISI Mark) certifications, violating statutory compliance.
3. **Omitted Allied Standards**: Procuring complex goods requires not just the main product code, but also related testing methods (NABL), safety codes, installation guidelines, and normative references.
4. **Language & Terminology Barriers**: Local procurement officers often describe requirements using colloquial or vernacular terminology (e.g., *sariya*, *bijli taar*, *neeti pumpu*) rather than statutory catalog names.

---

## 💡 2. The Solution & How We Solved It

**GRASK AI** automates and eliminates ambiguity in standards procurement by providing an intelligent, statutory-grounded recommendation engine:

* **Semantic Product-to-Standard Matching**: Translates plain text, technical descriptions, or vernacular terms directly to official Bureau of Indian Standards (IS) codes.
* **Automated QCO Enforcement**: Instantly flags whether a product is subject to a mandatory Quality Control Order under the BIS Act, protecting officers from compliance breaches.
* **6-Dimensional Allied Standards Graph**: Automatically links each product standard to its **Test Methods**, **Safety Codes**, **Installation Standards**, **Normative References**, and **Terminology**.
* **1-Click GeM Tender Clause Generator**: Automatically compiles legally airtight, audit-ready tender clauses formatted specifically for Government e-Marketplace (GeM) bids.

---

## 🔄 3. End-to-End Flow: From Query to Result

```
[ User Input: Voice (STT) or Text in 11 Indian Languages ]
                           │
                           ▼
     [ Step 1: Semantic Sanitizer & Vernacular Normalizer ]
       • Corrects phonetic terms (e.g., "sariya" ➔ IS 1786)
       • Validates domain scope & prevents query leakage
                           │
                           ▼
     [ Step 2: Hybrid Retrieval & Knowledge Graph ]
       • ChromaDB Dense Vector Search + BM25 Sparse Search
       • Real-time BIS catalog lookup & amendment checks
                           │
                           ▼
     [ Step 3: Statutory QCO & Allied Standards Engine ]
       • Maps Testing (NABL), Safety, Installation & Normative codes
       • Checks mandatory ISI Mark statutory orders
                           │
                           ▼
     [ Step 4: Structured Output Delivery ]
       • Primary IS Code & Reaffirmation Year
       • Interactive Allied Standards Breakdown
       • 1-Click Copyable GeM Tender Specification Clause
```

---

## ⚡ 4. Additional Features (In Short)

* **🥗 FSSAI Nutri-Score & Additive Radar**: Evaluates food nutritional profiles to assign Front-of-Pack grades (A to E) and detects hidden industrial additives/sugars.
* **📋 Ready to Apply (MSME Readiness Dossier)**: Evaluates factory readiness, provides in-house laboratory machinery checklists, and calculates statutory fees with Udyam concessions.
* **🏷️ MANAK-Vision Statutory Mark Verifier**: Verifies BIS ISI (CM/L), FSSAI license numbers, MeitY CRS, Gold HUID, and GS1 Barcodes to catch counterfeit goods.
* **🧪 Compliance Audit Workspace**: Validates observed laboratory test certificate parameters against statutory tolerance limits with instant pass/fail verdicts.

---

## 🚀 5. Quickstart & Execution Guide

### Prerequisites
* **Python 3.10+**
* **Node.js 18+** & **npm**

---

### Step A: Run the Backend

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Gemini API key (optional for offline fallback)

# 5. Start the backend server
python run.py
```
> The FastAPI backend will be available at: `http://localhost:8000`  
> Interactive API Docs: `http://localhost:8000/docs`

---

### Step B: Run the Frontend

```bash
# 1. Open a new terminal and navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the Vite development server
npm run dev
```
> The frontend application will be live at: `http://localhost:5173`

---

## 🔒 6. Privacy & Data Safety Commitment

* **Zero Personal / System Metadata**: All source files and configurations are sanitized. No local machine paths, user data, or active private API keys are contained in this repository.
* **Safe for Immediate GitHub Publication**: The project includes a pre-configured `.gitignore` that prevents accidental commits of virtual environments, `node_modules`, `.env` files, logs, or local database caches.
