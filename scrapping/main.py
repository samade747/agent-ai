from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str
    prompt: str
    license_key: str | None = None

@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    try:
        # Setup headless Chrome with Selenium
        options = Options()
        options.headless = True
        driver = uc.Chrome(options=options)
        driver.get(request.url)

        # Let JS render
        driver.implicitly_wait(5)
        html = driver.page_source
        driver.quit()

        # Extract visible text
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=" ")

        # LLM call
        messages = [
            {"role": "system", "content": "You're a web scraping expert."},
            {"role": "user", "content": f"{request.prompt}\n\nText:\n{text[:4000]}"},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        return {"result": response["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"detail": f"Fetch error: {e}"}





# import os, re, json
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, HttpUrl
# from bs4 import BeautifulSoup
# import openai
# from selenium.webdriver.chrome.options import Options
# import undetected_chromedriver as uc

# # Load environment variables
# load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# PAID_LICENSE_KEY = os.getenv("PAID_LICENSE_KEY")
# openai.api_key = OPENAI_API_KEY

# app = FastAPI()

# class ScrapeRequest(BaseModel):
#     url: HttpUrl
#     prompt: str
#     license_key: str | None = None

# class ScrapeResponse(BaseModel):
#     result: dict | str

# def fetch_page(url: str, timeout: int = 15) -> str:
#     options = Options()
#     options.headless = True
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     driver = uc.Chrome(options=options)
#     try:
#         driver.get(url)
#         html = driver.page_source
#     finally:
#         driver.quit()
#     return html

# def html_to_text(html: str) -> str:
#     soup = BeautifulSoup(html, "html.parser")
#     for tag in soup(["script", "style", "noscript"]):
#         tag.decompose()
#     text = soup.get_text(separator="\n")
#     return re.sub(r"\n\s*\n+", "\n\n", text).strip()

# def ai_extract(text: str, prompt: str) -> str:
#     messages = [
#         {"role": "system", "content": "You extract structured data from website text."},
#         {"role": "user", "content": f"{prompt}\n\n---\n{text[:2000]}..."}
#     ]
#     resp = openai.ChatCompletion.create(
#         model="gpt-4o",
#         messages=messages,
#         temperature=0,
#         max_tokens=512,
#     )
#     return resp.choices[0].message.content.strip()

# @app.post("/scrape", response_model=ScrapeResponse)
# def scrape(req: ScrapeRequest):
#     if not OPENAI_API_KEY:
#         raise HTTPException(status_code=500, detail="OpenAI key not set")
    
#     is_paid = req.license_key == PAID_LICENSE_KEY
#     try:
#         html = fetch_page(str(req.url))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Fetch error: {e}")

#     text = html_to_text(html)

#     try:
#         raw = ai_extract(text, req.prompt)
#         return {"result": json.loads(raw)}
#     except json.JSONDecodeError:
#         return {"result": raw}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"AI error: {e}")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



# # import os, re, json
# # from dotenv import load_dotenv
# # from fastapi import FastAPI, HTTPException
# # from pydantic import BaseModel, HttpUrl
# # from bs4 import BeautifulSoup
# # import openai
# # from selenium.webdriver.chrome.options import Options
# # import undetected_chromedriver as uc

# # # Load environment variables
# # load_dotenv()
# # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # PAID_LICENSE_KEY = os.getenv("PAID_LICENSE_KEY")
# # openai.api_key = OPENAI_API_KEY

# # app = FastAPI()

# # class ScrapeRequest(BaseModel):
# #     url: HttpUrl
# #     prompt: str
# #     license_key: str | None = None

# # class ScrapeResponse(BaseModel):
# #     result: dict | str

# # def fetch_page(url: str, timeout: int = 15) -> str:
# #     options = Options()
# #     options.headless = True
# #     options.add_argument("--no-sandbox")
# #     options.add_argument("--disable-dev-shm-usage")
# #     driver = uc.Chrome(options=options)
# #     try:
# #         driver.get(url)
# #         html = driver.page_source
# #     finally:
# #         driver.quit()
# #     return html

# # def html_to_text(html: str) -> str:
# #     soup = BeautifulSoup(html, "html.parser")
# #     for tag in soup(["script", "style", "noscript"]):
# #         tag.decompose()
# #     text = soup.get_text(separator="\n")
# #     return re.sub(r"\n\s*\n+", "\n\n", text).strip()

# # def ai_extract(text: str, prompt: str) -> str:
# #     messages = [
# #         {"role": "system", "content": "You extract structured data from website text."},
# #         {"role": "user", "content": f"{prompt}\n\n---\n{text[:2000]}..."}
# #     ]
# #     resp = openai.ChatCompletion.create(
# #         model="gpt-4o",
# #         messages=messages,
# #         temperature=0,
# #         max_tokens=512,
# #     )
# #     return resp.choices[0].message.content.strip()

# # @app.post("/scrape", response_model=ScrapeResponse)
# # def scrape(req: ScrapeRequest):
# #     if not OPENAI_API_KEY:
# #         raise HTTPException(status_code=500, detail="OpenAI key not set")
    
# #     is_paid = req.license_key == PAID_LICENSE_KEY
# #     try:
# #         html = fetch_page(str(req.url))
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Fetch error: {e}")

# #     text = html_to_text(html)

# #     try:
# #         raw = ai_extract(text, req.prompt)
# #         return {"result": json.loads(raw)}
# #     except json.JSONDecodeError:
# #         return {"result": raw}
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"AI error: {e}")


# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)




# # # import os, re, json
# # # from dotenv import load_dotenv
# # # from fastapi import FastAPI, HTTPException
# # # from pydantic import BaseModel, HttpUrl
# # # from bs4 import BeautifulSoup
# # # import openai
# # # from selenium.webdriver.chrome.options import Options
# # # import undetected_chromedriver as uc

# # # # Load environment variables
# # # load_dotenv()
# # # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # # PAID_LICENSE_KEY = os.getenv("PAID_LICENSE_KEY")
# # # openai.api_key = OPENAI_API_KEY

# # # app = FastAPI()

# # # class ScrapeRequest(BaseModel):
# # #     url: HttpUrl
# # #     prompt: str
# # #     license_key: str | None = None

# # # class ScrapeResponse(BaseModel):
# # #     result: dict | str

# # # def fetch_page(url: str, timeout: int = 15) -> str:
# # #     options = Options()
# # #     options.headless = True
# # #     options.add_argument("--no-sandbox")
# # #     options.add_argument("--disable-dev-shm-usage")
# # #     driver = uc.Chrome(options=options)
# # #     try:
# # #         driver.get(url)
# # #         html = driver.page_source
# # #     finally:
# # #         driver.quit()
# # #     return html

# # # def html_to_text(html: str) -> str:
# # #     soup = BeautifulSoup(html, "html.parser")
# # #     for tag in soup(["script", "style", "noscript"]):
# # #         tag.decompose()
# # #     text = soup.get_text(separator="\n")
# # #     return re.sub(r"\n\s*\n+", "\n\n", text).strip()

# # # def ai_extract(text: str, prompt: str) -> str:
# # #     messages = [
# # #         {"role": "system", "content": "You extract structured data from website text."},
# # #         {"role": "user", "content": f"{prompt}\n\n---\n{text[:2000]}..."}
# # #     ]
# # #     resp = openai.ChatCompletion.create(
# # #         model="gpt-4o",
# # #         messages=messages,
# # #         temperature=0,
# # #         max_tokens=512,
# # #     )
# # #     return resp.choices[0].message.content.strip()

# # # @app.post("/scrape", response_model=ScrapeResponse)
# # # def scrape(req: ScrapeRequest):
# # #     if not OPENAI_API_KEY:
# # #         raise HTTPException(status_code=500, detail="OpenAI key not set")
    
# # #     is_paid = req.license_key == PAID_LICENSE_KEY
# # #     try:
# # #         html = fetch_page(str(req.url))
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Fetch error: {e}")

# # #     text = html_to_text(html)

# # #     try:
# # #         raw = ai_extract(text, req.prompt)
# # #         return {"result": json.loads(raw)}
# # #     except json.JSONDecodeError:
# # #         return {"result": raw}
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"AI error: {e}")

# # # if __name__ == "__main__":
# # #     import uvicorn
# # #     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



# # # # #  main.py
# # # # from dotenv import load_dotenv
# # # # import os
# # # # import re
# # # # import json
# # # # from fastapi import FastAPI, HTTPException
# # # # from pydantic import BaseModel, HttpUrl
# # # # from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
# # # # from bs4 import BeautifulSoup
# # # # import openai
# # # # import uvicorn  # moved here so it's available

# # # # # ─── CONFIG ───────────────────────────────────────────────
# # # # load_dotenv()  # loads .env
# # # # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # # # PAID_LICENSE_KEY = os.getenv("PAID_LICENSE_KEY")
# # # # if not OPENAI_API_KEY:
# # # #     raise RuntimeError("Missing OPENAI_API_KEY in .env")
# # # # openai.api_key = OPENAI_API_KEY

# # # # # ─── APP & MODELS ──────────────────────────────────────────
# # # # app = FastAPI(title="AI Web-Scraper API")

# # # # class ScrapeRequest(BaseModel):
# # # #     url: HttpUrl
# # # #     prompt: str
# # # #     license_key: str | None = None

# # # # class ScrapeResponse(BaseModel):
# # # #     result: dict | str

# # # # # ─── HELPERS ──────────────────────────────────────────────
# # # # def fetch_page(url: str, timeout: int = 15000) -> str:
# # # #     print("Launching browser...")
# # # #     try:
# # # #         with sync_playwright() as p:
# # # #             browser = p.chromium.launch(headless=True)
# # # #             print("Browser launched.")
# # # #             page = browser.new_page()
# # # #             page.goto(url, timeout=timeout)
# # # #             page.wait_for_load_state("networkidle", timeout=timeout)
# # # #             html = page.content()
# # # #             browser.close()
# # # #             return html
# # # #     except Exception as e:
# # # #         raise RuntimeError(f"Playwright launch error: {str(e)}")


# # # # def html_to_text(html: str) -> str:
# # # #     soup = BeautifulSoup(html, "html.parser")
# # # #     for tag in soup(["script", "style", "noscript"]):
# # # #         tag.decompose()
# # # #     text = soup.get_text(separator="\n")
# # # #     return re.sub(r"\n\s*\n+", "\n\n", text).strip()

# # # # def ai_extract(text: str, prompt: str) -> str:
# # # #     messages = [
# # # #         {"role": "system", "content": "You extract structured data from website text."},
# # # #         {"role": "user",   "content": f"{prompt}\n\n---\n{text[:2000]}...\n"}
# # # #     ]
# # # #     resp = openai.ChatCompletion.create(
# # # #         model="gpt-4o-mini",
# # # #         messages=messages,
# # # #         temperature=0.0,
# # # #         max_tokens=512,
# # # #     )
# # # #     return resp.choices[0].message.content.strip()

# # # # # ─── ROUTES ───────────────────────────────────────────────
# # # # # @app.post("/scrape", response_model=ScrapeResponse)
# # # # # def scrape(req: ScrapeRequest):


# # # #     is_paid = (req.license_key == PAID_LICENSE_KEY)

# # # #     # 1. fetch
# # # #     try:
# # # #         html = fetch_page(req.url)
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=f"Fetch error: {e}")

# # # #     # 2. clean
# # # #     text = html_to_text(html)

# # # #     # 3. extract
# # # #     try:
# # # #         raw = ai_extract(text, req.prompt)
# # # #         parsed = json.loads(raw)
# # # #         return {"result": parsed}
# # # #     except json.JSONDecodeError:
# # # #         return {"result": raw}
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=f"AI error: {e}")

# # # # @app.post("/scrape", response_model=ScrapeResponse)
# # # # def scrape(req: ScrapeRequest):
# # # #     is_paid = (req.license_key == PAID_LICENSE_KEY)

# # # #     # 1. fetch
# # # #     try:
# # # #         html = fetch_page(str(req.url))  # <-- FIXED HERE
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=f"Fetch error: {e}")

# # # #     # 2. clean
# # # #     text = html_to_text(html)

# # # #     # 3. extract
# # # #     try:
# # # #         raw = ai_extract(text, req.prompt)
# # # #         parsed = json.loads(raw)
# # # #         return {"result": parsed}
# # # #     except json.JSONDecodeError:
# # # #         return {"result": raw}
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=f"AI error: {e}")

# # # # # ─── UVICORN ENTRYPOINT ────────────────────────────────────
# # # # if __name__ == "__main__":
# # # #     uvicorn.run(
# # # #         "main:app",
# # # #         host="0.0.0.0",
# # # #         port=int(os.getenv("PORT", 8000)),
# # # #         reload=True,
# # # #     )





# # # # # import os, re, json
# # # # # from dotenv import load_dotenv
# # # # # from fastapi import FastAPI, HTTPException
# # # # # from pydantic import BaseModel, HttpUrl
# # # # # from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
# # # # # from bs4 import BeautifulSoup
# # # # # import openai

# # # # # # ─── CONFIG ───────────────────────────────────────────────
# # # # # load_dotenv()
# # # # # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# # # # # if not OPENAI_API_KEY:
# # # # #     raise RuntimeError("Missing OPENAI_API_KEY in .env")
# # # # # openai.api_key = OPENAI_API_KEY

# # # # # # ─── APP & MODELS ──────────────────────────────────────────
# # # # # app = FastAPI(title="AI Web-Scraper API")

# # # # # class ScrapeRequest(BaseModel):
# # # # #     url: HttpUrl
# # # # #     prompt: str
# # # # #     license_key: str | None = None

# # # # # class ScrapeResponse(BaseModel):
# # # # #     result: dict | str

# # # # # # ─── HELPERS ──────────────────────────────────────────────
# # # # # def fetch_page(url: str, timeout: int = 15000) -> str:
# # # # #     with sync_playwright() as p:
# # # # #         browser = p.chromium.launch(headless=True)
# # # # #         page = browser.new_page()
# # # # #         try:
# # # # #             page.goto(url, timeout=timeout)
# # # # #             page.wait_for_load_state("networkidle", timeout=timeout)
# # # # #         except PlaywrightTimeout:
# # # # #             pass
# # # # #         html = page.content()
# # # # #         browser.close()
# # # # #     return html

# # # # # def html_to_text(html: str) -> str:
# # # # #     soup = BeautifulSoup(html, "html.parser")
# # # # #     for tag in soup(["script", "style", "noscript"]):
# # # # #         tag.decompose()
# # # # #     text = soup.get_text(separator="\n")
# # # # #     return re.sub(r"\n\s*\n+", "\n\n", text).strip()

# # # # # def ai_extract(text: str, prompt: str) -> str:
# # # # #     messages = [
# # # # #         {"role": "system", "content": "You extract structured data from website text."},
# # # # #         {"role": "user",   "content": f"{prompt}\n\n---\n{text[:2000]}...\n"}
# # # # #     ]
# # # # #     resp = openai.ChatCompletion.create(
# # # # #         model="gpt-4o-mini",
# # # # #         messages=messages,
# # # # #         temperature=0.0,
# # # # #         max_tokens=512,
# # # # #     )
# # # # #     return resp.choices[0].message.content.strip()

# # # # # # ─── ROUTES ───────────────────────────────────────────────
# # # # # @app.post("/scrape", response_model=ScrapeResponse)
# # # # # def scrape(req: ScrapeRequest):
# # # # #     # enforce free vs paid
# # # # #     is_paid = (req.license_key == os.getenv("PAID_LICENSE_KEY"))
# # # # #     # NOTE: for simplicity, no per-session counting on backend
# # # # #     # You could add Redis or DB to track free‐tier uses per IP.

# # # # #     # 1. fetch
# # # # #     try:
# # # # #         html = fetch_page(req.url)
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=f"Fetch error: {e}")

# # # # #     # 2. clean
# # # # #     text = html_to_text(html)

# # # # #     # 3. extract
# # # # #     try:
# # # # #         raw = ai_extract(text, req.prompt)
# # # # #         # try parse JSON
# # # # #         parsed = json.loads(raw)
# # # # #         return {"result": parsed}
# # # # #     except json.JSONDecodeError:
# # # # #         return {"result": raw}
# # # # #     except Exception as e:
# # # # #         raise HTTPException(status_code=500, detail=f"AI error: {e}")
