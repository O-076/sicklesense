# SickleSense Requirements

## Frontend Laptop Setup

- Windows, macOS, or Linux
- Node.js 20 or newer
- npm 10 or newer
- 4 GB RAM minimum, 8 GB recommended
- Internet access for installing npm packages and loading Google Fonts
- A modern browser: Chrome, Edge, Firefox, or Safari

## Install And Run

```bash
npm install
npm run dev
```

Open the local URL printed by Vite, normally `http://127.0.0.1:5173/`.

## Production Build

```bash
npm run build
npm run preview
```

## Frontend Stack

- React
- Vite
- Lucide React icons
- CSS custom properties and responsive CSS

## RAG Backend Requirements

The notebook currently uses Python and these services/packages:

- Python 3.10 or newer
- Azure AI Search
- Groq API access
- The three source PDFs used by the notebook
- Python packages listed in the notebook setup cell, including LangChain, Azure Search, Chroma, FastEmbed, PyPDF, Groq, and jsonschema

The backend should expose an HTTP endpoint such as:

```text
POST /api/ask
Content-Type: application/json

{"question":"When should hydroxyurea be started?"}
```

Expected response shape:

```json
{
  "recommendation": "...",
  "evidence": "...",
  "confidence": "high",
  "citations": [
    {
      "document": "NHLBI Expert Panel Report, 2014",
      "section": "Hydroxyurea Therapy",
      "page": 56,
      "chunk_id": "nhlbi-scd-2014-p56-c03"
    }
  ]
}
```

## Environment Variables

Do not commit secrets. The backend should load these from a local `.env` file:

```text
AZURE_SEARCH_ENDPOINT=...
AZURE_SEARCH_KEY=...
AZURE_SEARCH_INDEX=...
GROQ_API_KEY=...
```

## Connecting The Frontend

Replace the demo submit handler in `src/main.jsx` with a `fetch('/api/ask')` request. Store loading, answer, error, and citation data in React state. Keep the patient-specific safety check and insufficient-evidence refusal in the backend as well as the frontend.

## Important Safety Boundary

SickleSense is for clinical education and evidence review. It must not present population-level guidance as personalized diagnosis, dosage, or treatment advice.
