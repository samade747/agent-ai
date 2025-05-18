import os, json
from dotenv import load_dotenv
import streamlit as st
import httpx

# ─── CONFIG ───────────────────────────────────────────────
load_dotenv()
BACKEND_URL    = os.getenv("BACKEND_URL", "http://localhost:8000")
PAID_LICENSE   = os.getenv("PAID_LICENSE_KEY", "")

st.set_page_config(page_title="AI Web-Scraper UI", layout="wide")
st.title("🤖 AI Web-Scraper – Free vs. Paid Tier")

# ─── STATE ─────────────────────────────────────────────────
if "scrapes" not in st.session_state:
    st.session_state.scrapes = 0
if "is_paid" not in st.session_state:
    st.session_state.is_paid = False

# ─── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.header("🚪 Access Control")
    key = st.text_input("License Key (Paid)", type="password")
    if st.button("🔑 Unlock Paid Tier"):
        if key == PAID_LICENSE:
            st.session_state.is_paid = True
            st.success("Paid Tier unlocked!")
        else:
            st.error("Invalid key.")
    tier = "Paid" if st.session_state.is_paid else "Free"
    st.write(f"**Current Tier:** {tier}")
    if tier == "Free":
        st.write("Free Tier limit: 3 scrapes/session")

# ─── MAIN UI ───────────────────────────────────────────────
st.header("🔗 Step 1: URL & Prompt")
url = st.text_input("Website URL", placeholder="https://example.com")
default_prompt = (
    "Extract contact details: company name, email(s), phone(s), address(es), and purpose. "
    "Return JSON with keys: company_name, emails, phones, addresses, purpose."
)
prompt = st.text_area("Extraction Prompt", value=default_prompt, height=120)

if st.button("🚀 Scrape & Analyze"):
    if not url:
        st.error("Enter a URL.")
    elif not st.session_state.is_paid and st.session_state.scrapes >= 5:
        st.error("Free Tier limit reached. Enter key for Paid Tier.")
    else:
        st.session_state.scrapes += 1
        payload = {
            "url": url,
            "prompt": prompt,
            "license_key": PAID_LICENSE if st.session_state.is_paid else None
        }
        with st.spinner("Calling scraping service…"):
            resp = httpx.post(f"{BACKEND_URL}/scrape", json=payload, timeout=60)
        if resp.status_code != 200:
            st.error(f"Error {resp.status_code}: {resp.text}")
        else:
            data = resp.json()["result"]
            if isinstance(data, dict):
                st.json(data)
            else:
                st.text_area("Raw Output", data, height=300)

        if not st.session_state.is_paid:
            st.info(f"Free uses: {st.session_state.scrapes}/3")
