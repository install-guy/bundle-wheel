import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html import unescape


BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLES_DIR = BASE_DIR / "data" / "bundles"


class DescriptionCleaner(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.allowed_tags = {"br", "strong", "b", "div"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t not in self.allowed_tags:
            return
        if t == "br":
            self.parts.append("<br>")
            return
        if t == "div":
            class_name = ""
            for key, value in attrs:
                if key == "class" and value:
                    class_name = value.strip()
            if class_name == "ldh":
                self.parts.append('<div class="ldh">')
            else:
                self.parts.append("<div>")
            return
        self.parts.append(f"<{t}>")

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in {"strong", "b", "div"}:
            self.parts.append(f"</{t}>")

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(unescape(text))

    def get_html(self) -> str:
        cleaned = "".join(self.parts)
        cleaned = re.sub(r"(?:<br>\s*){3,}", "<br><br>", cleaned)
        cleaned = re.sub(r"\s+</", "</", cleaned)
        return cleaned.strip()


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    with urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_image_urls(html: str) -> list[str]:
    html = unescape(html)
    candidates = []

    # First, try the product photo gallery specifically.
    gallery_match = re.search(
        r'<div class="component-photo-gallery".*?</div><h1',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    search_area = gallery_match.group(0) if gallery_match else html

    # Grab Cloudinary image URLs from the gallery/source.
    cloudinary_matches = re.findall(
        r'https://res\.cloudinary\.com/hobbyshop/image/upload/[^"\']+\.(?:jpg|jpeg|png|webp)(?:\?[^"\']*)?',
        search_area,
        flags=re.IGNORECASE,
    )

    candidates.extend(cloudinary_matches)

    # Fallback: grab img src attributes.
    img_matches = re.findall(
        r'<img[^>]+src=["\']([^"\']+)["\']',
        search_area,
        flags=re.IGNORECASE,
    )

    candidates.extend(img_matches)

    cleaned = []
    seen = set()

    for url in candidates:
        url = unescape(url.strip())

        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = "https://store.hobbyetc.com" + url

        lower = url.lower()

        if "res.cloudinary.com/hobbyshop" not in lower:
            continue

        if not any(ext in lower for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            continue

        if any(skip in lower for skip in ["logo", "icon", "favicon", "sprite"]):
            continue

        if url not in seen:
            seen.add(url)
            cleaned.append(url)

    return cleaned


def extract_div_by_class(html: str, class_name: str) -> str:
    start_match = re.search(
        rf'<div[^>]*class=["\'][^"\']*\b{re.escape(class_name)}\b[^"\']*["\'][^>]*>',
        html,
        flags=re.IGNORECASE,
    )
    if not start_match:
        return ""

    start = start_match.start()
    idx = start_match.end()
    depth = 1

    while depth > 0 and idx < len(html):
        next_open = re.search(r"<div\b[^>]*>", html[idx:], flags=re.IGNORECASE)
        next_close = re.search(r"</div>", html[idx:], flags=re.IGNORECASE)

        if not next_close:
            return ""

        open_pos = idx + next_open.start() if next_open else None
        close_pos = idx + next_close.start()

        if open_pos is not None and open_pos < close_pos:
            depth += 1
            idx = idx + next_open.end()
        else:
            depth -= 1
            idx = idx + next_close.end()

    return html[start:idx] if depth == 0 else ""


def extract_description_html(html: str) -> str:
    raw_block = extract_div_by_class(html, "component-part-description")
    if not raw_block:
        return ""

    raw_block = re.sub(r"<script\b.*?</script>", "", raw_block, flags=re.IGNORECASE | re.DOTALL)
    raw_block = re.sub(r"<style\b.*?</style>", "", raw_block, flags=re.IGNORECASE | re.DOTALL)
    raw_block = re.sub(r"<button\b.*?</button>", "", raw_block, flags=re.IGNORECASE | re.DOTALL)

    cleaner = DescriptionCleaner()
    cleaner.feed(raw_block)
    return cleaner.get_html()


def update_bundle_file(bundle_path: Path) -> None:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    changed = False

    for part in bundle.get("parts", []):
        part_name = part.get("name", "Unnamed Part")
        part_url = part.get("url", "").strip()

        if not part_url or "REPLACE" in part_url:
            print(f"Skipping {part_name} — missing real product URL")
            continue

        existing_images = part.get("image_urls", [])
        existing_description = str(part.get("description_html", "")).strip()
        needs_images = not existing_images
        needs_description = not existing_description

        if not needs_images and not needs_description:
            print(f"Skipping {part_name} — image_urls and description_html already populated")
            continue

        try:
            print(f"Fetching missing data for {part_name}: {part_url}")
            html = fetch_html(part_url)

            if needs_images:
                image_urls = extract_image_urls(html)
                if image_urls:
                    part["image_urls"] = image_urls[:6]
                    changed = True
                    print(f"  Found {len(image_urls[:6])} image(s)")
                else:
                    print("  No images found")
            else:
                print("  image_urls already populated")

            if needs_description:
                description_html = extract_description_html(html)
                if description_html:
                    part["description_html"] = description_html
                    changed = True
                    print("  Found description_html")
                else:
                    print("  No description found")
            else:
                print("  description_html already populated")

        except (HTTPError, URLError, TimeoutError) as e:
            print(f"  Error fetching {part_url}: {e}")

    if changed:
        bundle_path.write_text(
            json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        print(f"Updated {bundle_path.name}")
    else:
        print(f"No changes for {bundle_path.name}")


def main() -> None:
    bundle_files = sorted(BUNDLES_DIR.glob("*.json"))

    if not bundle_files:
        print("No bundle JSON files found.")
        return

    for bundle_path in bundle_files:
        print(f"\nProcessing {bundle_path.name}")
        update_bundle_file(bundle_path)


if __name__ == "__main__":
    main()
