# Workspace Overview — Web Scrapping Collection

This repository contains multiple small-to-medium Python projects and notebooks focused on web scraping, data extraction, and report generation. The following is a concise summary of each top-level folder so you can quickly find and run the project you need.

- **16_webscrapping:** Notebook exercises and examples for learning web scraping (Jupyter notebooks).
- **Amazon product:** Amazon search scraper and supporting files. Key file: [Amazon product/amazon_search_scraper.py](Amazon%20product/amazon_search_scraper.py). See [Amazon product/requirements.txt](Amazon%20product/requirements.txt).
- **Amazone:** Amazon price tracking utilities. Subproject: [Amazone/amazon_price_tracker](Amazone/amazon_price_tracker) (contains `product_urls.json`).
- **Compare Html:** Tools to compare two HTML pages and match tags. Key file: [Compare Html/CompareSitesCode.py](Compare%20Html/CompareSitesCode.py) and [Compare Html/matching_tags.json](Compare%20Html/matching_tags.json).
- **google-sheet-web-scraper:** Full Google Sheets integration + scraping and combined report generation. See [google-sheet-web-scraper/README.md](google-sheet-web-scraper/README.md) for setup and usage (credentials, `requirements.txt`, and `run_*` helpers).
- **house of dragon:** HBO scraping project focused on “House of the Dragon” metadata and episodes. Two variants available (proxy and no-proxy). See [house of dragon/README.md](house%20of%20dragon/README.md) and [house of dragon/README_no_proxy.md](house%20of%20dragon/README_no_proxy.md). Main entry: [house of dragon/main.py](house%20of%20dragon/main.py).
- **instagram-scraper:** Feature-rich Instagram scraping tool (detailed README with CLI flags and output format). See [instagram-scraper/README.md](instagram-scraper/README.md) and runner `run.py`.
- **job-market-analysis:** Job scraping and recommendation tooling. Entry: [job-market-analysis/main.py](job-market-analysis/main.py). See `requirements.txt` for deps.
- **News scrapping:** Collection of notebooks for scraping news sources (Jupyter notebooks, e.g., `01_bbc.ipynb`).
- **news_aggregator:** BBC news aggregator and utilities. Main script: [news_aggregator/main.py](news_aggregator/main.py) — fetches articles and saves JSON outputs.
- **project 2:** Small app and utilities (includes `app.py`, `captcha_handler.py`, and `url_checker_fixed.py`). Entry: [project 2/app.py](project%202/app.py).
- **Project1:** Larger scraping pipeline that extracts public notices, enriches them and uploads to Google Sheets. Key entry: [Project1/main.py](Project1/main.py). Contains modules for `location`, `information_extractor`, and Google Sheets upload.
- **scraping-project:** Structured scraper + integration with OpenAI/GROQ for notice extraction and post-processing. See `scraper` and `openai_integration` modules (entry examples in [scraping-project/main.py](scraping-project/main.py)).
- **scrapping sites:** Reusable scraping helpers and address extraction utilities. Entry example: [scrapping sites/main.py](scrapping%20sites/main.py).
- **Twiiter_Scrapping:** Twitter scraping scripts and utilities (note folder name contains a small typo). Entry: [Twiiter_Scrapping/main.py](Twiiter_Scrapping/main.py). See `requirements.txt`.
- **web scrapping:** Simple example scripts (`Day_1.py`) and a `requirements.txt` for quick experiments.

Other root files:
- `extracted_notices.json` — example output data present at repo root.
- `Webshare 10 proxies.txt` — proxy list used by some projects.

How I summarized each project:
- I read available `README.md` files where present and inspected top-level `main.py` / `app.py` scripts to infer purpose and entry points.

Next steps you might want me to do:
- Expand any project summary into a full run-guide (dependencies, example commands).
- Add `requirements.txt` if missing or consolidate per-project dependency lists.
- Create minimal run scripts or CI tasks to validate each project.

If you want, I can now open and update any specific project's README with a runnable example and exact dependency list — tell me which one to start with.
