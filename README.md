# 🚀 PLAN AI CITY
### Pan-India RAG-Powered City Intelligence & Personalized Constraint-Aware Planning Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4-F7931E.svg?logo=scikit-learn)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Project Overview

**Plan AI City** is an enterprise-grade, full-stack city intelligence and personalized itinerary planning platform designed for **all of India**. It brings together **Retrieval-Augmented Generation (RAG)**, **Multi-Agent Swarm Orchestration**, **Unsupervised K-Means Persona Clustering**, **Geospatial Distance Optimization (Haversine)**, and **Dynamic Pan-India Locality Discovery (OpenStreetMap)**.

> *"Tell the AI what you want to do, and it researches any Indian city, town, or village, understands your budget and preferences, analyzes verified local information, and generates an optimized, time-blocked plan for you."*

For example:
> *“I have ₹2,000, 8 hours, I like cafés and historical places, and I'm starting from the railway station.”*

**The platform dynamically produces:**
- 🗺️ **Optimized Itinerary**: Geographically sequenced stops minimizing travel fatigue.
- 📍 **Verified Attractions**: Detailed opening hours, ticket costs, and child-friendliness flags.
- 🍴 **Gastronomy & Café Stops**: Authentic regional food and scenic café breaks.
- 💰 **Budget Breakdown**: Complete cost attribution per traveler.
- 🚌 **Travel Suggestions**: Estimated walking and transit times between stops.
- 🌦️ **Weather & Crowd Guidance**: Seasonality, best visiting hours, and peak avoidance.
- 📚 **Grounded RAG Citations**: Direct reference extracts from official tourism knowledge.
- 🤖 **Transparent AI Reasoning**: Step-by-step logs from the multi-agent swarm.

---

## 🇮🇳 Pan-India Places, Cities & Villages Coverage

Plan AI City covers destinations across **all 28 States & Union Territories of India**:
- **Metros & Smart Cities**: Delhi NCR, Mumbai, Bengaluru, Chandigarh, Pune, Hyderabad.
- **Heritage & Cultural Capitals**: Jaipur (Pink City), Varanasi (Ghats & Kashi Vishwanath), Agra (Taj Mahal), Udaipur, Kolkata, Amritsar (Golden Temple), Lucknow.
- **Mountain & Hill Stations**: Shimla, Manali, Rishikesh, Srinagar, Leh-Ladakh.
- **Coastal Escapes**: Goa (Fontainhas & Beaches), Kochi (Kerala Spice Hub).
- **Rural Wonders & Border Villages**:
  - **Chitkul** *(Himachal Pradesh)* – India's last inhabited border village in Kinnaur.
  - **Mawlynnong** *(Meghalaya)* – Asia's Cleanest Village with living root bridges.
  - **Kasol & Kangra** *(Himachal Pradesh)* – Scenic Himalayan valleys and temples.

### 🔍 Dynamic On-Demand Locality Resolver (`POST /api/v1/cities/resolve`)
If a user searches for *any* Indian town, tehsil, or village not yet pre-seeded, the platform automatically:
1. Queries **OpenStreetMap India** to verify exact coordinates, state, and district.
2. Auto-provisions authentic local points of interest (heritage spots, bazaars, regional eateries, scenic viewpoints).
3. Generates verified RAG vector embeddings on the fly, making any Indian locality instantly plannable!

---

## 🏛️ System Architecture

```mermaid
graph TD
    subgraph Client ["Frontend Layer (React 18 + TypeScript + Tailwind)"]
        UI_Home["Landing Page & Pan-India Omnibox"]
        UI_Planner["AI Trip Planner (Constraints & Budget)"]
        UI_Chat["RAG Assistant (Chat & Citations)"]
        UI_Dash["City Intelligence & Admin Dashboard"]
        UI_Auth["User Account & Profile Center"]
    end

    subgraph API_Gateway ["Backend API Gateway (FastAPI)"]
        Router["FastAPI App & API v1 Routers"]
        Auth_MW["JWT Auth & Role-Based Access Control"]
        Query_Router["Agent Query Router & Intent Classifier"]
    end

    subgraph Agents ["Multi-Agent Swarm (AI Layer)"]
        Orchestrator["AI Orchestrator"]
        CityAgent["City Knowledge Agent"]
        PlanningAgent["Constraint-Aware Itinerary Agent"]
        SearchAgent["Hybrid Search Agent"]
        RAGAgent["RAG QA & Citation Agent"]
        MapAgent["Geospatial & Route Optimization Agent"]
        RecAgent["ML Recommendation Agent"]
    end

    subgraph RAG_Engine ["RAG & Retrieval Subsystem"]
        DocLoader["Document Loader & Cleaner"]
        Chunker["Semantic Chunking Engine"]
        Embedder["Embedding Engine (384-Dim Normalized Dense Vector)"]
        HybridSearch["Hybrid Retrieval (BM25 + Dense Cosine)"]
        Reranker["Cross-Score Reranking (RRF)"]
        Citations["Evidence Citation Builder"]
    end

    subgraph ML_Analytics ["Machine Learning & Analytics Subsystem"]
        KMeans["User Persona Clustering (K-Means)"]
        ScoringModel["Multi-Factor Recommendation Scorer"]
        Aggregator["City Metrics & Query Analytics"]
    end

    subgraph Data_Layer ["Data & Storage Layer"]
        UserProfiles["user_profiles Table (Dedicated User Profile Storage)"]
        Users["users Table (Authentication)"]
        Cities["cities Table (Pan-India Cities & Villages)"]
        Places["places Table (Verified Attractions)"]
        VectorDB["Cosine Vector Similarity Store"]
    end

    Client --> Router
    Router --> Auth_MW
    Router --> Query_Router
    Query_Router --> Orchestrator
    Orchestrator --> CityAgent
    Orchestrator --> PlanningAgent
    Orchestrator --> SearchAgent
    Orchestrator --> RAGAgent
    Orchestrator --> MapAgent
    Orchestrator --> RecAgent
    RAGAgent --> HybridSearch
    HybridSearch --> VectorDB
    RecAgent --> ScoringModel
    PlanningAgent --> MapAgent
    Router --> Data_Layer
```

---

## 👤 User Account & Profile Storage (`user_profiles` Table)

Plan AI City features a dedicated relational table architecture:
1. **`users` Table**: Encrypted authentication credentials (`email`, `hashed_password` using bcrypt, `role`, `is_active`).
2. **`user_profiles` Table**: Dedicated user profile and contact storage:
   - `full_name`: User's full name
   - `email`: Verified account email
   - `phone_number`: Optional contact number
   - `home_city` & `home_state`: Home region in India
   - `country`: Default `India`
   - `bio`: Travel style and background
   - `account_status`: `active`
   - `created_at` & `last_login_at`: Timestamps
3. **`user_preferences` Table**: K-Means persona cluster, budget tier, and preferred categories.

---

## ⚡ Quickstart: Run on Any Windows Laptop

### 1-Click Automated Setup (No manual setup needed!)

1. **Install Prerequisites (Free, install once)**:
   - [Python 3.10+](https://www.python.org/downloads/) *(check "Add python.exe to PATH")*
   - [Node.js LTS](https://nodejs.org/)

2. **First Time Setup**:
   - Double-click **`INSTALL_ALL.bat`** (installs all Python and React packages).

3. **Start the Application**:
   - Double-click **`START_APP.bat`** (starts backend, frontend, and opens [http://localhost:3000](http://localhost:3000) automatically).

4. **Inspect Database**:
   - Double-click **`view_database.bat`** to view all tables (`user_profiles`, `cities`, `places`) in a formatted table view.

---

## 🧪 Verified Integration Tests

All core subsystems pass 100%:
- ✅ Pan-India multi-state cities & villages verified (Jaipur, Varanasi, Chitkul, Mawlynnong, Kangra, Goa, etc.)
- ✅ OpenStreetMap dynamic locality resolution verified
- ✅ New user registration with dedicated `user_profiles` database storage verified
- ✅ Constraint-aware budget and time optimizer verified

```bash
# Run integration test suite
python backend/test_all_features.py
```

---

## 📄 License
MIT License © 2026 Plan AI City
Developed with pride for Pan-India Travel & Smart Tourism.
