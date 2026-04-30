import json
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html import unescape


BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLES_DIR = BASE_DIR / "data" / "bundles"


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

        if existing_images:
            print(f"Skipping {part_name} — image_urls already populated")
            continue

        try:
            print(f"Fetching images for {part_name}: {part_url}")
            html = fetch_html(part_url)
            image_urls = extract_image_urls(html)

            if image_urls:
                part["image_urls"] = image_urls[:6]
                changed = True
                print(f"  Found {len(image_urls[:6])} image(s)")
            else:
                print("  No images found")

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