from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-3e7202e1c82a4f20a08613b88f735f0f")

result = app.scrape_url(
    "https://www.worldlabs.ai",
    formats=["markdown"]
)

print(type(result))
print(result)
print(dir(result))