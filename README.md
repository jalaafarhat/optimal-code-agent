Based on the repository name and our previous discussions, here's a comprehensive README for your `optimal-code-agent` project. It explains the purpose, setup, and usage of the two agents you've built.

---

# 🧠 Optimal Code Agent

This project contains two intelligent agents built with Google's **Agent Development Kit (ADK)**. They help you discover profitable business ideas and find great deals on online marketplaces.

## ✨ Agents Overview

### 1. **Business Agent**
*   **Purpose**: Evaluates small, realistic, machine-based business opportunities (e.g., paper cup manufacturing, vending machines, repair shops).
*   **How it works**:
    1.  Searches for machine details (price, power, supplier) using a real‑time Google Search.
    2.  Calculates total import costs, taxes, and ROI.
    3.  Checks local market feasibility based on population.
    4.  Verifies voltage compatibility and legal status.
    5.  Provides a structured "Viable / High Risk / Not Viable" verdict.

### 2. **Item Finder Agent**
*   **Purpose**: Finds underpriced items (**deals**) on eBay and Alibaba.
*   **How it works**:
    1.  Takes a user query, desired marketplace, and maximum budget.
    2.  Uses the **SerpAPI** to search eBay (via eBay engine) or Alibaba (via Google Search with `site:alibaba.com`).
    3.  Extracts prices from titles and snippets, handling ranges (e.g., `$500 – $800`).
    4.  Returns a list of items under budget with direct links.

## 🛠️ Technologies Used
*   Python 3.12+
*   Google ADK
*   SerpAPI (for real‑time search)
*   Google Gemini (`gemini-2.0-flash`) as the underlying LLM
*   `python-dotenv` for environment variable management

## 🚀 Setup & Installation

### Prerequisites
*   Python 3.12 or higher
*   A [SerpAPI API Key](https://serpapi.com/) (free tier available)
*   A [Google AI Studio API Key](https://aistudio.google.com/) for Gemini

### Steps

1.  **Clone the repository**
    ```bash
    git clone https://github.com/jalaafarhat/optimal-code-agent.git
    cd optimal-code-agent
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *(If you don't have a `requirements.txt` yet, create one with: `google-adk`, `python-dotenv`, `serpapi`, `requests`, `beautifulsoup4`)*

4.  **Set up environment variables**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Open the new `.env` file and add your actual API keys:
        ```env
        SERPAPI_API_KEY=your_actual_serpapi_key_here
        GOOGLE_API_KEY=your_actual_gemini_key_here
        ```
    *   **Important:** The `.env` file is listed in `.gitignore` and will **never** be committed to GitHub. This keeps your keys safe.

## 🎯 How to Use

### Run the Business Agent
Navigate to the agent's directory and start the ADK web interface:
```bash
cd multi-agent/stateful_multi_agent/manager/sub_agents/business_agent
adk web
```
Then open your browser to the provided local URL. You can ask questions like:
*   *"I live in a village in Israel with 8,000 people. I have $15,000. What's a good passive income machine I can import from China?"*
*   *"Analyze the feasibility of starting a paper cup manufacturing business in my town."*

### Run the Item Finder Agent
```bash
cd multi-agent/stateful_multi_agent/manager/sub_agents/itemfinder
adk web
```
Then try queries such as:
*   *"Find me a used Rolex Submariner on eBay for under $200."*
*   *"Find me a commercial juice pasteurizer on Alibaba for under $10,000."*
*   *"Find me a 1 oz gold coin under $150."* (The agent will ask which marketplace you prefer.)

## 📁 Project Structure (Simplified)
```
optimal-code-agent/
├── .env.example               # Template for environment variables
├── .gitignore                  # Ignores .env, __pycache__, etc.
├── multi-agent/
│   └── stateful_multi_agent/
│       └── manager/
│           └── sub_agents/
│               ├── business_agent/       # Business opportunity agent
│               │   ├── agent.py
│               │   ├── prompt.md
│               │   └── machines.json     # Auto-populated machine DB
│               └── itemfinder/            # eBay/Alibaba deal finder
│                   ├── agent.py
│                   └── prompt.md
└── requirements.txt            # Python dependencies
```

## ⚠️ Important Security Notes
*   Your API keys are stored **only** in your local `.env` file. The repository itself contains **no** secrets.
*   The `.env` file is explicitly ignored by Git (via `.gitignore`).
*   If you ever accidentally commit a secret, **rotate your keys immediately** and use tools like `git filter-branch` to remove them from history.

## 🤝 Contributing
Feel free to fork the project, improve the agents, or add new tools. Pull requests are welcome!

## 📄 License
This project is open-source. Please add your preferred license here (e.g., MIT, Apache 2.0).
