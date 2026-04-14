import json
import re
from html import escape
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLES_DIR = BASE_DIR / "data" / "bundles"
OUTPUT_DIR = BASE_DIR / "output"
BASE_URL = "https://store.hobbyetc.com"


def load_bundle(bundle_path: Path) -> dict:
    with bundle_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("&", "and")
    text = text.replace("/", "-")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def markdown_link(text: str, url: str) -> str:
    return f"[{text}]({url})"


def build_product_links(parts: list[dict]) -> list[dict]:
    product_links = []

    for part in parts:
        name = part.get("name", "Part")
        url = part.get("url", "").strip()

        product_links.append({
            "anchor_text": name,
            "url": url
        })

    return product_links


def build_link_map(parts: list[dict]) -> dict:
    return {
        item["anchor_text"]: item["url"]
        for item in build_product_links(parts)
        if item["url"]
    }


def build_parts_list_markdown(parts: list[dict], link_parts: bool = True) -> str:
    link_map = build_link_map(parts)
    lines = []

    for part in parts:
        name = part.get("name", "Unnamed Part")
        role = part.get("role", "").strip()

        if link_parts and name in link_map:
            display_name = markdown_link(name, link_map[name])
        else:
            display_name = name

        if role:
            lines.append(f"- **{display_name}** — {role.capitalize()}")
        else:
            lines.append(f"- **{display_name}**")

    return "\n".join(lines)


def build_landing_page(bundle: dict) -> str:
    bundle_name = bundle.get("bundle_name", "HR Upgrade Bundle")
    vehicle_name = bundle.get("vehicle_name", "Your Vehicle")
    headline = bundle.get("headline", bundle_name)
    subheadline = bundle.get("subheadline", "")
    bundle_slug = bundle.get("bundle_slug") or slugify(bundle_name)

    bundle_url = f"{BASE_URL}/bundles/{bundle_slug}"
    parts_finder_url = f"{BASE_URL}/vehicles"
    parts_page_url = f"{BASE_URL}/parts"

    offer = bundle.get("offer", {})
    offer_label = offer.get("label", "Pit Pass Cash eligible")
    offer_note = offer.get(
        "note",
        "Earn loyalty rewards on your build without discounting the bundle."
    )

    influencer = bundle.get("influencer", {})
    influencer_name = influencer.get("name", "our creator partner")
    influencer_angle = influencer.get("content_angle", "install, test, real-world use")

    parts_markdown = build_parts_list_markdown(bundle.get("parts", []), link_parts=True)

    return f"""# {headline}

{subheadline}

**Built to fix the stuff that actually breaks first.**

## What’s Included

{parts_markdown}

## Why This Bundle

This {bundle_name} was put together for {vehicle_name} owners who want a smart mix of durability, strength, and upgrade value without guessing their way through a pile of parts.

These are the kinds of upgrades that make sense when you actually drive, bash, wrench, and go back for more.

## Built for Real-World Use

This isn’t a random collection of parts. It’s a hand-picked setup built around real upgrade intent:
- strengthen common weak points
- improve confidence behind the wheel
- make the platform more fun to run

## Creator Content Angle

We’re pairing this bundle with content from **{influencer_name}** with a focus on:

**{influencer_angle}**

That means real installs, real testing, and real feedback.

## Loyalty Bonus

**{offer_label}**

{offer_note}

## Call to Action

Ready to build your Mini Kraton your way?

- {markdown_link("Shop the bundle", bundle_url)}
- {markdown_link("Check the individual parts", parts_page_url)}
- {markdown_link("Use the parts finder to keep the build going", parts_finder_url)}
"""


def build_blog_post(bundle: dict) -> str:
    bundle_name = bundle.get("bundle_name", "HR Upgrade Bundle")
    vehicle_name = bundle.get("vehicle_name", "Your Vehicle")
    headline = bundle.get("headline", bundle_name)
    bundle_slug = bundle.get("bundle_slug") or slugify(bundle_name)

    bundle_url = f"{BASE_URL}/bundles/{bundle_slug}"
    parts_finder_url = f"{BASE_URL}/vehicles"
    parts_page_url = f"{BASE_URL}/parts"

    parts = bundle.get("parts", [])
    parts_markdown = build_parts_list_markdown(parts, link_parts=True)

    influencer = bundle.get("influencer", {})
    influencer_name = influencer.get("name", "our creator partner")

    return f"""# {headline} Upgrades That Actually Make Sense

If you run an {vehicle_name}, you already know how quickly a fun platform can turn into a list of parts you probably ought to upgrade next.

That’s where {markdown_link("this bundle", bundle_url)} comes in.

Instead of tossing together random upgrades, this setup focuses on parts that help support real-world driving, durability, and repeat use. The goal is simple: make the vehicle stronger, more capable, and more satisfying to run.

## What’s in the Bundle

{parts_markdown}

## Why We Built It This Way

A good upgrade bundle should do more than look nice on a product page. It should answer a real question:

**If I’m going to upgrade this rig, where should I start?**

This bundle gives a solid answer by combining parts that help it:
- take hits better
- stay tighter
- keep power where it belongs
- hold up run after run

## Real Content, Not Just Catalog Copy

We’re also putting this bundle in the hands of **{influencer_name}** so people can see what it looks like in actual use.

That means installs, testing, and honest impressions instead of polished nonsense.

## The Bigger Idea

This isn’t just about one bundle. It’s about helping hobbyists make smarter upgrade decisions without digging through endless listings and second-guessing every part.

If this build style fits what you’re after, start with {markdown_link("the full bundle", bundle_url)}, dig through {markdown_link("the individual parts", parts_page_url)}, and use {markdown_link("the parts finder", parts_finder_url)} to keep the build going.

## Next Steps

- {markdown_link("Shop the full bundle", bundle_url)}
- {markdown_link("Explore the individual parts", parts_page_url)}
- {markdown_link("Use the parts finder to see what fits your vehicle", parts_finder_url)}
"""


def build_meta(bundle: dict) -> dict:
    bundle_name = bundle.get("bundle_name", "HR Upgrade Bundle")
    vehicle_name = bundle.get("vehicle_name", "Mini Kraton")
    title = f"{vehicle_name} HR Upgrade Bundle | Hobby Etc"
    description = (
        f"Shop the {bundle_name} at Hobby Etc. "
        f"A hand-picked upgrade setup built for real-world use, smarter installs, and repeat runs."
    )
    return {
        "title": title,
        "description": description
    }


def build_internal_links(bundle: dict) -> dict:
    bundle_slug = bundle.get("bundle_slug", "bundle")
    product_links = build_product_links(bundle.get("parts", []))

    return {
        "bundle_page": f"{BASE_URL}/bundles/{bundle_slug}",
        "parts_finder": f"{BASE_URL}/vehicles",
        "related_category": f"{BASE_URL}/parts",
        "product_links": product_links
    }


def markdown_to_html(markdown_text: str, meta: dict | None = None) -> str:
    meta = meta or {}
    title = escape(meta.get("title", "Generated Content"))
    description = escape(meta.get("description", ""))

    lines = markdown_text.splitlines()
    html_parts = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    def convert_inline(text: str) -> str:
        text = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda m: f'@@LINK_START@@{m.group(1)}||{m.group(2)}@@LINK_END@@',
            text
        )

        text = escape(text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

        text = re.sub(
            r"@@LINK_START@@(.*?)\|\|(.*?)@@LINK_END@@",
            lambda m: f'<a href="{escape(m.group(2), quote=True)}">{m.group(1)}</a>',
            text
        )

        return text

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            close_list()
            continue

        if line.startswith("# "):
            close_list()
            html_parts.append(f"<h1>{convert_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            close_list()
            html_parts.append(f"<h2>{convert_inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{convert_inline(line[2:])}</li>")
        else:
            close_list()
            html_parts.append(f"<p>{convert_inline(line)}</p>")

    close_list()

    body = "\n".join(html_parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
</head>
<body>
{body}
</body>
</html>
"""


def write_output(bundle: dict) -> None:
    bundle_slug = bundle.get("bundle_slug") or slugify(bundle.get("bundle_name", "bundle"))
    bundle_output_dir = OUTPUT_DIR / bundle_slug
    bundle_output_dir.mkdir(parents=True, exist_ok=True)

    landing_page = build_landing_page(bundle)
    blog_post = build_blog_post(bundle)
    meta = build_meta(bundle)
    internal_links = build_internal_links(bundle)

    landing_page_html = markdown_to_html(landing_page, meta)
    blog_post_html = markdown_to_html(blog_post, meta)

    (bundle_output_dir / "landing-page.md").write_text(landing_page, encoding="utf-8")
    (bundle_output_dir / "blog-post.md").write_text(blog_post, encoding="utf-8")
    (bundle_output_dir / "landing-page.html").write_text(landing_page_html, encoding="utf-8")
    (bundle_output_dir / "blog-post.html").write_text(blog_post_html, encoding="utf-8")
    (bundle_output_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (bundle_output_dir / "internal-links.json").write_text(
        json.dumps(internal_links, indent=2),
        encoding="utf-8"
    )

    print(f"Generated content for: {bundle_slug}")
    print(f"Output folder: {bundle_output_dir}")


def main() -> None:
    if not BUNDLES_DIR.exists():
        raise FileNotFoundError(f"Bundles directory not found: {BUNDLES_DIR}")

    bundle_files = sorted(BUNDLES_DIR.glob("*.json"))

    if not bundle_files:
        print("No bundle JSON files found in /data/bundles")
        return

    for bundle_file in bundle_files:
        try:
            bundle = load_bundle(bundle_file)
            write_output(bundle)
        except Exception as e:
            print(f"Error processing {bundle_file.name}: {e}")


if __name__ == "__main__":
    main()