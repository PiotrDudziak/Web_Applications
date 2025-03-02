import os
import re
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# Set up output directories
OUTPUT_DIR = "WWW1"
CHARACTERS_DIR = os.path.join(OUTPUT_DIR, "characters")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CHARACTERS_DIR, exist_ok=True)

# ------------------------------
# Part 1: Main Website (star_wars.md file creation)
# ------------------------------
def get_wikipedia_info(query):
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {"action": "query", "list": "search", "srsearch": query, "format": "json"}
    response = requests.get(search_url, params=params)
    data = response.json()
    if data.get("query", {}).get("search", []):
        title = data["query"]["search"][0]["title"]
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
        summary_response = requests.get(summary_url)
        summary_data = summary_response.json()
        if "extract" in summary_data:
            info = summary_data["extract"]
            link = summary_data.get("content_urls", {}).get("desktop", {}).get("page", "")
            return info, link
    return "No information found.", ""

# Retrieve background picture URL using DuckDuckGo
with DDGS() as ddgs:
    image_results = ddgs.images("star wars picture", max_results=1)
bg_image_url = (
    image_results[0].get("image", "")
    if image_results and len(image_results) > 0
    else "assets/default_star_wars_bg.jpg"
)

# Retrieve Wikipedia information for main content
wiki_intro, wiki_source = get_wikipedia_info("Star Wars")
movies_info, movie_source = get_wikipedia_info("Star Wars movies")
games_info, games_source = get_wikipedia_info("Star Wars games")
books_info, books_source = get_wikipedia_info("Star Wars books")

# Build main Markdown file wrapped in HTML for background styling
main_md_content = f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Star Wars Introduction</title>
    <style>
      html, body {{
        height: 100%;
        margin: 0;
      }}
      body {{
        background: url({bg_image_url}) no-repeat center center fixed;
        background-size: cover;
        font-family: Arial, sans-serif;
        color: #FFFFFF;
      }}
      .content {{
        position: relative;
        padding: 20px;
        min-height: 100vh;
        text-shadow: 4px 4px 8px rgba(0, 0, 0, 1);
        background-color: rgba(0, 0, 0, 0.5);
      }}
      a {{
        color: #ADD8E6;
      }}
    </style>
  </head>
  <body>
    <div class="content">
      <h1>Star Wars Introduction</h1>
      <p>{wiki_intro}</p>
      <p><em>Source: <a href="{wiki_source}" target="_blank">{wiki_source}</a></em></p>
      <h2>Star Wars Movies</h2>
      <p>{movies_info}</p>
      <p><em>Source: <a href="{movie_source}" target="_blank">{movie_source}</a></em></p>
      <h2>Star Wars Games</h2>
      <p>{games_info}</p>
      <p><em>Source: <a href="{games_source}" target="_blank">{games_source}</a></em></p>
      <h2>Star Wars Books</h2>
      <p>{books_info}</p>
      <p><em>Source: <a href="{books_source}" target="_blank">{books_source}</a></em></p>
      <h3>List of some of the characters from franchise: <a href="star_wars_list.md">Visit the Star Wars Characters Catalog</a></h3>
    </div>
  </body>
</html>
""".strip()

with open(os.path.join(OUTPUT_DIR, "star_wars.md"), "w", encoding="utf-8") as f:
    f.write(main_md_content)
print("Main website Markdown file (star_wars.md) generated.")

# ------------------------------
# Part 2: Character List File (star_wars_list.md creation)
# ------------------------------
url = "https://kenjosabers.com/blogs/news/top-15-most-popular-star-wars-characters-icons-from-a-galaxy-far-far-away"
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
elements = soup.find_all("strong", string=re.compile(r"#\d+:"))
if not elements:
    print("No characters found.")
    exit()

characters = []
for element in elements:
    char_text = element.get_text(strip=True)
    character_name = char_text.replace(":", "").strip()
    search_name = re.sub(r"^\#\d+\s*", "", character_name).strip()
    additional_info = "No additional info found."
    additional_info_source = ""
    image_url = ""
    image_source = ""

    with DDGS() as ddgs:
        text_results = ddgs.text("fandom information " + search_name, max_results=1)
        image_results = ddgs.images(search_name, max_results=1)

    if text_results and len(text_results) > 0:
        full_text = ""
        for result in text_results:
            full_text += result.get("body", result.get("title")) + "\n\n"
        sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", full_text)
        if sentences:
            additional_info = sentences[0]
            for i in range(1, len(sentences)):
                if len(additional_info) + len(sentences[i]) < 300:
                    additional_info += " " + sentences[i]
                else:
                    break
        additional_info_source = text_results[0].get("href") if text_results else ""

    if image_results and len(image_results) > 0:
        image_url = image_results[0].get("image", "")
        image_source = image_results[0].get("image") if image_results else ""

    characters.append({
        "name": character_name,
        "info": additional_info,
        "info_src": additional_info_source,
        "img": image_url,
        "img_src": image_source
    })

# Create character list file (star_wars_list.md) in OUTPUT_DIR.
# Links point to individual detail pages in the characters directory.
character_list_md = "## Star Wars Characters\n\n"
for char in characters:
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", re.sub(r"^\#\d+\s*", "", char["name"])) + ".md"
    character_list_md += f"- [{char['name']}](characters/{safe_name})\n"

with open(os.path.join(OUTPUT_DIR, "star_wars_list.md"), "w", encoding="utf-8") as f:
    f.write(character_list_md)
print("Character list Markdown file (star_wars_list.md) generated.")

# ------------------------------
# Part 3: Details Subpages (individual character details in the characters directory)
# ------------------------------
for char in characters:
    file_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", re.sub(r"^\#\d+\s*", "", char["name"])) + ".md"
    detail_md_content = f"# {char['name']}\n\n"
    img_section = ""
    if char["img"]:
        img_section = (
            f'<img src="{char["img"]}" alt="{char["name"]}" '
            f'style="max-height: 275px; max-width: 100%; min-height: 175px;"/>'
            f'<br><br>Source: <a href="{char["img_src"]}" style="word-break: break-all;">{char["img_src"]}</a>'
        )
    detail_md_content += (
        '<div style="display: flex;">\n'
        '  <div style="flex: 1; padding-right: 10px;">\n'
        '    <strong>Short Introduction:</strong>\n'
        f'    <p>{char["info"]}</p>\n'
        f'    Additional info source: <a href="{char["info_src"]}">{char["info_src"]}</a>\n'
        '  </div>\n'
        '  <div style="flex: 1; text-align: right;">\n'
        f'    {img_section}\n'
        '  </div>\n'
        '</div>\n'
    )
    with open(os.path.join(CHARACTERS_DIR, file_name), "w", encoding="utf-8") as f:
        f.write(detail_md_content)

print("Detail subpages generated.")