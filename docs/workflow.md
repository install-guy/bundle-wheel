# Bundle-Wheel Workflow

## 1. Project purpose

This repo generates bundle marketing content for Hobby Etc and Hot Racing upgrade bundles. Bundle details live in JSON files, and Python scripts combine that data with reusable templates to produce reviewable content in `output/`.

## 2. Source files vs generated files

Source files live in:

- `scripts/*`
- `templates/blog/*`
- `data/bundles/*`
- `assets/*`

Generated files live in:

- `output/*`

Do not commit generated output files unless intentionally requested.

## 3. Recommended workflow

Use this sequence for normal bundle work:

1. Update or add bundle JSON in `data/bundles/`.
2. Run `scripts/fetch_part_images.py` when product images or descriptions need to be pulled from product pages.
3. Run `scripts/generate_bundle_content.py` to generate previews.
4. Review output previews locally.
5. Commit only source files and intentional assets.
6. Leave `output/` uncommitted.

## 4. Local commands

Windows PowerShell examples:

```powershell
cd "C:\Users\Jeff W\Documents\GitHub\bundle-wheel"
py scripts/fetch_part_images.py
py scripts/generate_bundle_content.py
start .\output\scx30-brass-crawl-bundle\blog-post.preview.html
```

## 5. Codex / AI agent rules

- Do not commit `output/`.
- Edit source files only.
- Use generated outputs for verification only.
- Report if output files changed during testing.
- Do not invent product URLs or image URLs.
- Do not overwrite existing `image_urls` or `description_html` unless asked.

## 6. Current bundle themes

- `crawler`: focuses on control, low-down weight, steering precision, planted feel, and technical lines.
- `basher`: focuses on durability, impacts, hard landings, drivetrain strength, and getting back to the next run.

## 7. Notes

- Mini Kraton currently has placeholder product URLs.
- SCX30 currently has real product URLs and fetched image/description assets.
- Hero images are optional via `hero_image_url`.
