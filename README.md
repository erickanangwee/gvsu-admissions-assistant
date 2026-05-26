# GVSU Admissions Chatbot

## Motivation

Having worked in admissions, one of the most time-consuming aspects of the job is answering students' questions. These questions span a wide range of topics, and getting accurate answers typically requires a web search — which often returns many results, some unrelated, forcing you to read through multiple pages before finding what you need. This process is slow and sometimes yields no clear answer at all.

The GVSU Admissions Chatbot was created to address this problem. Rather than manually searching the web, the chatbot searches gvsu.edu live, reads the most relevant pages, and returns a concise, grounded answer — cutting search time significantly. Future versions will expand coverage to include the web pages most frequently consulted by students during the admissions process.

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose (only for Docker setup)

---

## Required API Keys

### 1. Anthropic API Key
Used to power the chatbot's responses via Claude.

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **API Keys** and click **Create Key**
4. Copy the key — you will only see it once

### 2. Serper API Key
Used to search gvsu.edu via Google Search.

1. Go to [serper.dev](https://serper.dev)
2. Sign up for a free account (includes 2,500 free searches)
3. From the dashboard, copy your API key

---

## Clone the Repository

```bash
git clone https://github.com/your-username/gvsu-admissions-chatbot.git
cd gvsu-admissions-chatbot
```

---

## Setup Without Docker

### 1. Configure environment variables

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SERPER_API_KEY=your_serper_api_key_here
DATABASE_URL=sqlite:///./gvsu_chatbot.db
```

### 2. Set up the backend

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Set up the frontend

```bash
cd frontend
npm install
cd ..
```

### 4. Run the chatbot

Open two terminal windows from the project root.

**Terminal 1 — API server:**
```bash
# Activate venv first (see step 2)
uvicorn api.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## Setup With Docker

### 1. Install Docker Desktop

1. Go to [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) and download the installer for your operating system (Windows, macOS, or Linux)
2. Run the installer and follow the on-screen instructions
3. Once installed, open **Docker Desktop**

### 2. Create a Docker account

1. Go to [hub.docker.com](https://hub.docker.com) and sign up for a free account
2. In Docker Desktop, click **Sign in** (top right) and log in with your Docker account
3. Docker Desktop will show a green status indicator at the bottom left confirming the Docker daemon is running — you must see this before proceeding

### 3. Configure environment variables

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

> The Docker setup uses PostgreSQL automatically — no `DATABASE_URL` needed in `.env`.

### 4. Build and run

Open a terminal in the project root and run:

```bash
docker compose up --build
```

This will build the API and frontend images and start all three containers (API, frontend, and database). The first build may take a few minutes. Once complete, open your browser at `http://localhost`.

On subsequent runs, the images are already built so you can start faster with:

```bash
docker compose up
```

To stop the containers:
```bash
docker compose down
```

---

## Usage

- Type any GVSU admissions-related question in the chat input and press **Send** or hit **Enter**
- Use the topic chips (**Freshman**, **Transfer**, **Graduate**, **International**, **Financial Aid**, **Housing**) to tailor responses to your context
- Each answer includes source links back to the gvsu.edu pages used to generate it
