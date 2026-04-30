import json
import re
from html import escape
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLES_DIR = BASE_DIR / "data" / "bundles"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = BASE_DIR / "templates"
BASE_URL = "https://store.hobbyetc.com"


THEME_COPY = {
    "crawler": {
        "value_prop": "Built to improve balance, control, and confidence on the crawl.",
        "video_intro": "Real setup. Real crawl feel. Real feedback.",
        "why_intro": (
            "Crawling is about control. This bundle adds weight and stiffness where it "
            "matters so the rig feels more planted and predictable."
        ),
        "benefits": [
            "Adds low-down weight for a more planted crawl feel",
            "Improves front-end bite and steering precision",
            "Helps the rig stay settled on technical lines",
            "Built for controlled crawling, not random upgrades",
        ],
    },
    "basher": {
        "value_prop": "Built to fix the stuff that actually breaks first.",
        "video_intro": "Real install. Real test. Real feedback.",
        "why_intro": (
            "A good bash bundle should toughen up weak points and keep the rig running hard."
        ),
        "benefits": [
            "Toughens up common weak points",
            "Helps handle hard hits and bad landings",
            "Keeps the rig tighter run after run",
            "Built for bashing and going back for more",
        ],
    },
}


def load_bundle(bundle_path: Path) -> dict:
    with bundle_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_template(template_path: Path) -> str:
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


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


def html_link(text: str, url: str) -> str:
    return f'<a href="{escape(url, quote=True)}">{escape(text)}</a>'


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


def build_parts_list_markdown(parts: list[dict]) -> str:
    lines = []

    for part in parts:
        name = part.get("name", "Unnamed Part")
        role = part.get("role", "").strip()
        url = part.get("url", "").strip()

        display_name = markdown_link(name, url) if url else name

        if role:
            lines.append(f"- **{display_name}** — {role.capitalize()}")
        else:
            lines.append(f"- **{display_name}**")

    return "\n".join(lines)


def build_parts_list_html(parts: list[dict]) -> str:
    has_images = any(part.get("image_urls") for part in parts)

    if has_images:
        cards = []

        for part in parts:
            name = part.get("name", "Unnamed Part")
            role = part.get("role", "").strip()
            url = part.get("url", "").strip() or "#"
            image_urls = part.get("image_urls", [])
            image = ""

            if isinstance(image_urls, list):
                image = next(
                    (img.strip() for img in image_urls if isinstance(img, str) and img.strip()),
                    ""
                )

            safe_name = escape(name)
            safe_role = escape(role.capitalize()) if role else ""
            safe_url = escape(url, quote=True)
            safe_image = escape(image, quote=True)

            if safe_image:
                image_html = (
                    f'<img class="part-card-image" src="{safe_image}" alt="{safe_name}">'
                )
            else:
                image_html = '<div class="part-card-image part-card-image-placeholder">No image</div>'

            card = f"""
<div class="part-card">
  {image_html}
  <div class="part-card-body">
    <h3 class="part-card-title">
      <a href="{safe_url}">{safe_name}</a>
    </h3>
    <p class="part-card-role">{safe_role}</p>
    <a class="part-card-link" href="{safe_url}">View part →</a>
  </div>
</div>
"""
            cards.append(card.strip())

        return '<div class="parts-card-grid">\n' + "\n".join(cards) + "\n</div>"

    lines = ["<ul>"]

    for part in parts:
        name = part.get("name", "Unnamed Part")
        role = part.get("role", "").strip()
        url = part.get("url", "").strip()

        display_name = html_link(name, url) if url else escape(name)

        if role:
            lines.append(f"  <li><strong>{display_name}</strong> — {escape(role.capitalize())}</li>")
        else:
            lines.append(f"  <li><strong>{display_name}</strong></li>")

    lines.append("</ul>")
    return "\n".join(lines)


def build_video_block(video: dict) -> str:
    embed_url = video.get("embed_url", "").strip()
    youtube_url = video.get("youtube_url", "").strip()
    thumbnail_url = video.get("thumbnail_url", "").strip()
    title = video.get("title", "Video")

    if embed_url:
        safe_embed = escape(embed_url, quote=True)
        safe_title = escape(title, quote=True)
        return (
            '<div class="video-embed-wrapper">'
            f'<iframe src="{safe_embed}" title="{safe_title}" '
            'loading="lazy" allow="accelerometer; autoplay; clipboard-write; '
            'encrypted-media; gyroscope; picture-in-picture; web-share" '
            'allowfullscreen></iframe>'
            '</div>'
        )

    if youtube_url and thumbnail_url:
        safe_video = escape(youtube_url, quote=True)
        safe_thumb = escape(thumbnail_url, quote=True)
        safe_title = escape(title)
        return (
            f'<a class="video-thumb-link" href="{safe_video}" target="_blank" rel="noopener noreferrer">'
            f'<img src="{safe_thumb}" alt="{safe_title}">'
            f'<span class="video-thumb-play">Watch Video</span>'
            '</a>'
        )

    if youtube_url:
        safe_video = escape(youtube_url, quote=True)
        return (
            f'<div class="video-placeholder"><a href="{safe_video}" target="_blank" '
            'rel="noopener noreferrer">Open creator video</a></div>'
        )

    return '<div class="video-placeholder">Video embed goes here</div>'


def render_template(template: str, context: dict) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))
    return rendered


def build_blog_context(bundle: dict) -> dict:
    bundle_name = bundle.get("bundle_name", "HR Upgrade Bundle")
    bundle_slug = bundle.get("bundle_slug") or slugify(bundle_name)
    vehicle_name = bundle.get("vehicle_name", "Your Vehicle")
    headline = bundle.get("headline", bundle_name)
    subheadline = bundle.get("subheadline", "")
    parts = bundle.get("parts", [])
    video = bundle.get("video", {})

    theme = str(bundle.get("theme", "basher")).strip().lower() or "basher"
    if theme not in THEME_COPY:
        theme = "basher"

    theme_copy = THEME_COPY[theme]

    offer_label = bundle.get("offer", {}).get("label", "Pit Pass Cash eligible")
    influencer_name = bundle.get("influencer", {}).get("name", "our creator partner")
    influencer_angle = bundle.get(
        "influencer", {}
    ).get("content_angle", "install, test, does it make the cut")

    bundle_url = f"{BASE_URL}/bundles/{bundle_slug}"
    parts_page_url = f"{BASE_URL}/parts"
    parts_finder_url = f"{BASE_URL}/vehicles"

    meta_title = f"{vehicle_name} HR Upgrade Bundle | Hobby Etc"
    meta_description = (
        f"Shop the {bundle_name} at Hobby Etc. "
        f"A hand-picked upgrade setup built for real-world use, smarter installs, and repeat runs."
    )

    hero_image_url = str(bundle.get("hero_image_url", "")).strip()
    hero_image_html = ""

    if hero_image_url:
        safe_url = escape(hero_image_url, quote=True)
        safe_alt = escape(headline)
        hero_image_html = (
            f'<img src="{safe_url}" alt="{safe_alt}" '
            'style="display:block;width:100%;max-width:920px;height:auto;'
            'border-radius:12px;margin-top:14px;">'
        )

    return {
        "headline": headline,
        "subheadline": subheadline,
        "value_prop": theme_copy["value_prop"],
        "vehicle_name": vehicle_name,
        "theme": theme.capitalize(),
        "part_count": str(len(parts)),
        "offer_label": offer_label,
        "influencer_name": influencer_name,
        "influencer_angle": influencer_angle,
        "video_intro": theme_copy["video_intro"],
        "video_embed_or_placeholder": build_video_block(video),
        "parts_list": build_parts_list_markdown(parts),
        "parts_list_html": build_parts_list_html(parts),
        "why_intro": theme_copy["why_intro"],
        "benefit_1": theme_copy["benefits"][0],
        "benefit_2": theme_copy["benefits"][1],
        "benefit_3": theme_copy["benefits"][2],
        "benefit_4": theme_copy["benefits"][3],
        "hero_image_html": hero_image_html,
        "creator_supporting_copy": (
            "That means installs, testing, and honest impressions instead of polished nonsense."
        ),
        "parts_finder_intro": (
            "Start with your vehicle and we’ll help you find what actually fits."
        ),
        "bundle_url": bundle_url,
        "parts_page_url": parts_page_url,
        "parts_finder_url": parts_finder_url,
        "meta_title": meta_title,
        "meta_description": meta_description,
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


def build_meta(context: dict) -> dict:
    return {
        "title": context["meta_title"],
        "description": context["meta_description"]
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
            lambda m: f"@@LINK_START@@{m.group(1)}||{m.group(2)}@@LINK_END@@",
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

    blog_md_template = load_template(TEMPLATES_DIR / "blog" / "bundle-blog-post.md")
    blog_fragment_template = load_template(
        TEMPLATES_DIR / "blog" / "bundle-blog-post.fragment.html"
    )
    blog_preview_template = load_template(
        TEMPLATES_DIR / "blog" / "bundle-blog-post.preview.html"
    )

    context = build_blog_context(bundle)
    blog_post_md = render_template(blog_md_template, context)
    blog_fragment_html = render_template(blog_fragment_template, context)

    preview_context = dict(context)
    preview_context["blog_fragment"] = blog_fragment_html
    blog_preview_html = render_template(blog_preview_template, preview_context)

    meta = build_meta(context)
    internal_links = build_internal_links(bundle)
    blog_post_html = markdown_to_html(blog_post_md, meta)

    (bundle_output_dir / "blog-post.md").write_text(blog_post_md, encoding="utf-8")
    (bundle_output_dir / "blog-post.fragment.html").write_text(
        blog_fragment_html, encoding="utf-8"
    )
    (bundle_output_dir / "blog-post.preview.html").write_text(
        blog_preview_html, encoding="utf-8"
    )
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