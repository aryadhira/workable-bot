## workable-bot
---

### What is workable-bot?
---
Workable bot is bot that automate process of filling and submit job application form. This bot is created using Python and Playwright as the automation browser. workable-bot also powerred by AI to answering question based on resume data.

---
### Quick Start
---
- install required dependencies `pip install -r requirement.txt`
- install playwright browser and dependencies `playwright install`
- create environment variable file `.env` file and copy value from the `.env-example`
- for LLM we can use [OpenAI](https://platform.openai.com/docs/quickstart) or local LLM like [Ollama](https://ollama.com/) or [llama.cpp](https://github.com/ggml-org/llama.cpp) 
- local LLM
  - no need to fill `OPENAI_KEY` on `.env`
  - fill `OPENAI_BASE_URL` based on your local LLM server URL
- Open AI
  - fill `OPENAI_KEY` on `.env` based on your api-key
  - fill `OPENAI_MODEL` to use your desired model
- run bot `python main.py`

---