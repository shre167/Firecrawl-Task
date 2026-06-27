from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="")

result = app.scrape_url(
    "https://www.worldlabs.ai",
    formats=["markdown"]
)

print(type(result))
print(result)
print(dir(result))
