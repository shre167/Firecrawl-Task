import pandas as pd
import time
from urllib.parse import urljoin
from firecrawl import FirecrawlApp

# ==================================================
# CONFIG
# ==================================================

API_KEY = "api_key"

app = FirecrawlApp(api_key=API_KEY)

INPUT_FILE = r"C:\Users\shrey\Desktop\Firecrawl-Task\saas-companies.xlsx"
OUTPUT_FILE = r"C:\Users\shrey\Desktop\Firecrawl-Task\classified_companies.xlsx"

WEBSITE_COLUMN = "website"

# ==================================================
# READ EXCEL
# ==================================================

df = pd.read_excel(INPUT_FILE)

new_columns = [
    "is_b2b",
    "is_saas",
    "has_login_page",
    "login_url",
    "evidence_notes",
    "confidence"
]

for col in new_columns:
    if col not in df.columns:
        df[col] = ""

# ==================================================
# KEYWORDS
# ==================================================

b2b_keywords = [
    "enterprise",
    "enterprises",
    "business",
    "businesses",
    "organization",
    "organizations",
    "company",
    "companies",
    "teams",
    "workflow",
    "contact sales",
    "book a demo",
    "request demo",
    "for enterprises",
    "for businesses",
]

saas_keywords = [
    "software",
    "platform",
    "cloud",
    "dashboard",
    "subscription",
    "pricing",
    "free trial",
    "get started",
    "web app",
    "sign up",
    "monthly",
    "annual",
]

login_keywords = [
    "login",
    "log in",
    "signin",
    "sign in",
    "portal",
    "dashboard",
    "app."
]

# ==================================================
# PROCESS
# ==================================================

for idx, row in df.iterrows():

    website = str(row[WEBSITE_COLUMN]).strip()

    if website == "" or website.lower() == "nan":
        continue

    if not website.startswith("http"):
        website = "https://" + website

    print("=" * 60)
    print(f"Processing {idx+1}/{len(df)}")
    print(website)

    try:

        result = app.scrape_url(
            website,
            formats=["markdown"]
        )

        # Firecrawl v4 returns a Document object
        text = result.markdown

        if text is None:
            raise Exception("No markdown returned")

        lower = text.lower()

        # ----------------------------
        # B2B
        # ----------------------------

        b2b_score = sum(keyword in lower for keyword in b2b_keywords)

        if b2b_score >= 2:
            is_b2b = "Yes"
        elif b2b_score == 1:
            is_b2b = "Unknown"
        else:
            is_b2b = "No"

        # ----------------------------
        # SaaS
        # ----------------------------

        saas_score = sum(keyword in lower for keyword in saas_keywords)

        if saas_score >= 2:
            is_saas = "Yes"
        elif saas_score == 1:
            is_saas = "Unknown"
        else:
            is_saas = "No"

        # ----------------------------
        # Login Detection
        # ----------------------------

        has_login = "No"
        login_url = ""

        if any(keyword in lower for keyword in login_keywords):

            has_login = "Yes"

            if "signin" in lower or "sign in" in lower:
                login_url = urljoin(website, "/signin")

            elif "login" in lower or "log in" in lower:
                login_url = urljoin(website, "/login")

            elif "portal" in lower:
                login_url = urljoin(website, "/portal")

            elif "dashboard" in lower:
                login_url = urljoin(website, "/dashboard")

            else:
                login_url = urljoin(website, "/app")

        # ----------------------------
        # Confidence
        # ----------------------------

        confidence = "High"

        if is_b2b == "Unknown" or is_saas == "Unknown":
            confidence = "Medium"

        if len(lower) < 400:
            confidence = "Low"

        evidence = text.replace("\n", " ")[:250]

        print(
            f"B2B={is_b2b}, SaaS={is_saas}, Login={has_login}, Confidence={confidence}"
        )

        # ----------------------------
        # WRITE TO DATAFRAME
        # ----------------------------

        df.loc[idx, "is_b2b"] = is_b2b
        df.loc[idx, "is_saas"] = is_saas
        df.loc[idx, "has_login_page"] = has_login
        df.loc[idx, "login_url"] = login_url
        df.loc[idx, "evidence_notes"] = evidence
        df.loc[idx, "confidence"] = confidence

    except Exception as e:

        print("ERROR:", e)

        df.loc[idx, "is_b2b"] = "Unknown"
        df.loc[idx, "is_saas"] = "Unknown"
        df.loc[idx, "has_login_page"] = "Unknown"
        df.loc[idx, "login_url"] = ""
        df.loc[idx, "evidence_notes"] = str(e)
        df.loc[idx, "confidence"] = "Low"

    # SAVE AFTER EVERY COMPANY
    df.to_excel(OUTPUT_FILE, index=False)

    time.sleep(1)

print("\nFinished!")

print(f"Saved to:\n{OUTPUT_FILE}")