"""
build.py — Static Site Generator for FlaskrTutorials
=====================================================
Replaces Flask's request-time rendering with a one-time build step.
Outputs a complete static site to the _site/ folder, ready for
GitHub Pages or Netlify deployment.

Usage:
    python build.py

Output:
    _site/                   ← deploy this folder
      index.html
      static/                ← copied from flaskr/static/
      <topic>/<creator>/<course>/<chapter>/<section>/index.html

Requirements:
    pip install jinja2

Run from the project root (same folder that contains the flaskr/ directory).
"""

import os
import re
import json
import shutil
from jinja2 import Environment, FileSystemLoader
from json import JSONDecodeError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_PATH       = 'flaskr/static/json'
TEMPLATES_PATH  = 'flaskr/templates'
STATIC_SRC      = 'flaskr/static'
OUTPUT_DIR      = '_site'
STATIC_DST      = os.path.join(OUTPUT_DIR, 'static')


# ---------------------------------------------------------------------------
# Library loader  (mirrors flaskr/__init__.py exactly)
# ---------------------------------------------------------------------------

def get_topics(path):
    library = []
    basedir = os.path.abspath(path)
    for entry in sorted(os.listdir(basedir)):
        full_path = os.path.join(basedir, entry)
        if os.path.isdir(full_path):
            topic = {"topic": entry, "creators": []}
            library.append(topic)
            get_creators(topic, full_path)
    return library


def get_creators(container, path):
    basedir = os.path.abspath(path)
    for entry in sorted(os.listdir(basedir)):
        full_path = os.path.join(basedir, entry)
        if os.path.isdir(full_path):
            creator = {"creator": entry, "courses": []}
            container["creators"].append(creator)
            get_courses(creator, full_path)


def get_courses(container, path):
    basedir = os.path.abspath(path)
    for entry in sorted(os.listdir(basedir)):
        full_path = os.path.join(basedir, entry)
        if os.path.isdir(full_path):
            course = {"course": entry, "chapters": []}
            container["courses"].append(course)
            get_chapters(course, full_path)


def get_chapters(container, path):
    basedir = os.path.abspath(path)
    for entry in sorted(os.listdir(basedir)):
        full_path = os.path.join(basedir, entry)
        if os.path.isdir(full_path):
            get_chapter(container["chapters"], full_path)
        else:
            with open(full_path, "r", encoding="utf-8") as f:
                json_data = json.loads(f.read())
            for key, value in json_data.items():
                container[key] = value


def get_chapter(container, path):
    basedir = os.path.abspath(path)
    for entry in sorted(os.listdir(basedir)):
        full_path = os.path.join(basedir, entry)
        with open(full_path, "r", encoding="utf-8") as f:
            try:
                json_data = json.loads(f.read())
                container.append(json_data)
            except JSONDecodeError as e:
                print(f"  WARNING: JSON error in {full_path} — {e}")


def load_library():
    return get_topics(DATA_PATH)


# ---------------------------------------------------------------------------
# Content item parser  (mirrors flaskr/routes.py exactly)
# ---------------------------------------------------------------------------

def get_content_item(content):
    content_item = {}
    if isinstance(content, str):
        if any(tag in content for tag in ("[kbd]", "[k]", "[url]", "[i]", "[u]", "[b]")):
            content_item["type"] = "compound_text"
            content_item["content"] = []
            if "[kbd]" in content:
                regex_list = re.findall(r"\[kbd\][^[]+\[\/kbd\]", content)
                for i in regex_list:
                    content = content.replace(i, "|")
                content = content.split("|")
                for i, v in enumerate(content):
                    content_item["content"].append(get_content_item(v))
                    if i < len(regex_list):
                        o = {"kbd": regex_list[i].replace("[kbd]", "").replace("[/kbd]", "")}
                        content_item["content"].append(get_content_item(o))
            if "[k]" in content:
                regex_list = re.findall(r"\[k\][^[]+\[\/k\]", content)
                for i in regex_list:
                    content = content.replace(i, "|")
                content = content.split("|")
                for i, v in enumerate(content):
                    content_item["content"].append(get_content_item(v))
                    if i < len(regex_list):
                        o = {"kbd": regex_list[i].replace("[k]", "").replace("[/k]", "")}
                        content_item["content"].append(get_content_item(o))
            if "[i]" in content:
                regex_list = re.findall(r"\[i\][^[]+\[\/i\]", content)
                for i in regex_list:
                    content = content.replace(i, "|")
                content = content.split("|")
                for i, v in enumerate(content):
                    content_item["content"].append(get_content_item(v))
                    if i < len(regex_list):
                        o = {"italic": regex_list[i].replace("[i]", "").replace("[/i]", "")}
                        content_item["content"].append(get_content_item(o))
            if "[u]" in content:
                regex_list = re.findall(r"\[u\][^[]+\[\/u\]", content)
                for i in regex_list:
                    content = content.replace(i, "|")
                content = content.split("|")
                for i, v in enumerate(content):
                    content_item["content"].append(get_content_item(v))
                    if i < len(regex_list):
                        o = {"underline": regex_list[i].replace("[u]", "").replace("[/u]", "")}
                        content_item["content"].append(get_content_item(o))
            if "[b]" in content:
                regex_list = re.findall(r"\[b\][^[]+\[\/b\]", content)
                for i in regex_list:
                    content = content.replace(i, "|")
                content = content.split("|")
                for i, v in enumerate(content):
                    content_item["content"].append(get_content_item(v))
                    if i < len(regex_list):
                        o = {"strong": regex_list[i].replace("[b]", "").replace("[/b]", "")}
                        content_item["content"].append(get_content_item(o))
            if "[url]" in content:
                regex_list = re.findall(r"\[url\][^[]+\[\/url\]", content)
                for i in regex_list:
                    content = content.replace(i, "|")
                content = content.split("|")
                for i, v in enumerate(content):
                    content_item["content"].append(get_content_item(v))
                    if i < len(regex_list):
                        parts = regex_list[i].replace("[url]", "").replace("[/url]", "").split("^^")
                        href = parts[1] if len(parts) > 1 else "#"
                        html = parts[0]
                        o = {"url": {"href": href, "html": html}}
                        content_item["content"].append(get_content_item(o))
        else:
            content_item["type"] = "text"
            content_item["content"] = content

    elif isinstance(content, list):
        content_item["type"] = "list"
        content_item["content"] = [get_content_item(item) for item in content]

    elif isinstance(content, dict):
        for element_type, concept_element in content.items():
            if element_type == "code":
                content_item["type"] = "code"
                content_item["content"] = concept_element
            elif element_type == "compound_text":
                content_item["type"] = "compound_text"
                content_item["content"] = [get_content_item(i) for i in concept_element]
            elif element_type == "d_list":
                content_item["type"] = "d_list"
                content_item["content"] = concept_element
            elif element_type == "kbd":
                content_item["type"] = "kbd"
                content_item["content"] = concept_element
            elif element_type == "italic":
                content_item["type"] = "italic"
                content_item["content"] = concept_element
            elif element_type == "image":
                content_item["type"] = "image"
                content_item["content"] = [concept_element] if isinstance(concept_element, dict) else concept_element
            elif element_type == "image-dlist":
                content_item["type"] = "image-dlist"
                content_item["content"] = concept_element
            elif element_type == "list":
                content_item["type"] = "list"
                content_item["content"] = [get_content_item(i) for i in concept_element]
            elif element_type == "menu_selection":
                content_item["type"] = "menu_selection"
                content_item["content"] = concept_element
            elif element_type == "model":
                content_item["type"] = "model"
                content_item["content"] = concept_element
            elif element_type == "section":
                content_item["type"] = "section"
                content_item["header"] = concept_element["header"]
                content_item["content"] = [get_content_item(i) for i in concept_element["content"]]
            elif element_type == "strong":
                content_item["type"] = "strong"
                content_item["content"] = concept_element
            elif element_type == "ref-table":
                content_item["type"] = "ref-table"
                content_item["content"] = []
                for row in concept_element:
                    row_obj = []
                    content_item["content"].append(row_obj)
                    for cell in row:
                        o = {}
                        row_obj.append(o)
                        if "th" in cell:
                            o["th"] = get_content_item(cell["th"])
                        else:
                            o["td"] = get_content_item(cell["td"])
            elif element_type == "table":
                content_item["type"] = "table"
                content_item["content"] = []
                for row in concept_element:
                    row_obj = []
                    content_item["content"].append(row_obj)
                    for cell in row:
                        o = {}
                        row_obj.append(o)
                        if "th" in cell:
                            o["th"] = get_content_item(cell["th"])
                        else:
                            o["td"] = get_content_item(cell["td"])
            elif element_type == "underline":
                content_item["type"] = "underline"
                content_item["content"] = concept_element
            elif element_type == "url":
                content_item["type"] = "anchor"
                content_item["href"] = concept_element["href"]
                content_item["content"] = concept_element["html"]
            break  # dict entries are single-key by design in your schema
    return content_item


# ---------------------------------------------------------------------------
# Flatten library into an ordered list of all pages
# This makes prev/next trivial: just index ± 1
# ---------------------------------------------------------------------------

def flatten_library(library):
    """
    Returns a flat list of dicts, one per section, in nav order.
    Each dict contains all the context needed to build the page.
    """
    pages = []
    for topic in library:
        for creator in topic["creators"]:
            for course in creator["courses"]:
                if "chapters" not in course:
                    continue
                for chapter in course["chapters"]:
                    if "sections" not in chapter:
                        continue
                    for section_item in chapter["sections"]:
                        section_title = list(section_item.keys())[0]
                        pages.append({
                            "topic":    topic["topic"],
                            "creator":  creator["creator"],
                            "course":   course["course"],
                            "chapter":  chapter["title"],
                            "section":  section_title,
                            "data":     section_item[section_title],
                        })
    return pages


def make_href(page):
    """Build the URL path for a page dict."""
    return "/{}/{}/{}/{}/{}".format(
        page["topic"], page["creator"], page["course"],
        page["chapter"], page["section"]
    )


# ---------------------------------------------------------------------------
# Jinja2 setup — replicates url_for('static', filename=...) as a filter
# ---------------------------------------------------------------------------

def setup_jinja_env():
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_PATH),
        autoescape=True,
    )

    # Replace Flask's url_for('static', filename=X) with /static/X
    # Used as: url_for('static', filename='img/foo.jpg')
    # In templates this appears as: url_for('static', filename=...)
    # We expose a simple global function with the same signature.
    def url_for(endpoint, **kwargs):
        if endpoint == "static":
            return "/tutorials/static/" + kwargs.get("filename", "")
        return "/"

    env.globals["url_for"] = url_for
    return env


# ---------------------------------------------------------------------------
# Page builder
# ---------------------------------------------------------------------------

def build_content(section_data):
    """Parse a section's key_concepts and exercises into content items."""
    content = []
    content.append({"type": "header", "content": section_data.get("title", "")})

    for key_concept in section_data.get("key_concepts", []):
        content.append(get_content_item(key_concept))

    if "exercises" in section_data:
        o = {"type": "exercises", "content": []}
        for exercise in section_data["exercises"]:
            o["content"].append(get_content_item(exercise))
        content.append(o)

    return content


def write_page(env, template, output_path, **context):
    """Render a template and write it to disk."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    html = template.render(**context)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build():
    print("=" * 60)
    print("FlaskrTutorials Static Site Builder")
    print("=" * 60)

    # 1. Clean and recreate output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    print(f"\n[1/4] Output directory '{OUTPUT_DIR}/' created")

    # 2. Copy static assets
    if os.path.exists(STATIC_SRC):
        shutil.copytree(STATIC_SRC, STATIC_DST)
        print(f"[2/4] Static assets copied  ({STATIC_SRC} → {STATIC_DST})")
    else:
        print(f"[2/4] WARNING: Static source '{STATIC_SRC}' not found, skipping")

    # 3. Load data
    print("[3/4] Loading library from JSON...")
    library = load_library()
    all_pages = flatten_library(library)
    print(f"      Found {len(all_pages)} pages across all courses")

    # 4. Build pages
    print("[4/4] Rendering pages...")
    env = setup_jinja_env()

    # Load content template (extends base.html, contains all macros)
    try:
        content_template = env.get_template("content.html")
    except Exception as e:
        print(f"  ERROR: Could not load content.html template: {e}")
        return

    # Load index template
    try:
        index_template = env.get_template("true_index.html")
    except Exception as e:
        print(f"  WARNING: Could not load true_index.html template: {e}")
        index_template = None

    # Build index page
    if index_template:
        index_path = os.path.join(OUTPUT_DIR, "index.html")
        write_page(env, index_template,
                   index_path,
                   title="Blender Courses",
                   library=library)
        print(f"  index.html")

    # Build all content pages
    error_count = 0
    for i, page in enumerate(all_pages):
        prev_page = all_pages[i - 1] if i > 0 else None
        next_page = all_pages[i + 1] if i < len(all_pages) - 1 else None

        footer_data = {}
        if prev_page:
            footer_data["prev"] = {
                "href": make_href(prev_page),
                "html": prev_page["section"],
            }
        if next_page:
            footer_data["next"] = {
                "href": make_href(next_page),
                "html": next_page["section"],
            }

        try:
            content = build_content(page["data"])
        except Exception as e:
            print(f"  WARNING: Content parse error for {make_href(page)}: {e}")
            content = [{"type": "text", "content": f"[Build error: {e}]"}]
            error_count += 1

        # Output path: _site/topic/creator/course/chapter/section/index.html
        out_path = os.path.join(
            OUTPUT_DIR,
            page["topic"],
            page["creator"],
            page["course"],
            page["chapter"],
            page["section"],
            "index.html"
        )

        try:
            write_page(
                env,
                content_template,
                out_path,
                title="Blender Courses",
                nav=[],
                library=library,
                content=content,
                footer_data=footer_data,
                _topic=page["topic"],
                _creator=page["creator"],
                _course=page["course"],
                _chapter=page["chapter"],
                _section=page["section"],
            )
        except Exception as e:
            print(f"  ERROR rendering {make_href(page)}: {e}")
            error_count += 1
            continue

        # Progress indicator every 25 pages
        if (i + 1) % 25 == 0 or i == len(all_pages) - 1:
            print(f"  {i + 1}/{len(all_pages)} pages rendered...")

    # Summary
    print()
    print("=" * 60)
    print(f"Build complete.")
    print(f"  Pages generated : {len(all_pages)}")
    print(f"  Errors          : {error_count}")
    print(f"  Output folder   : {os.path.abspath(OUTPUT_DIR)}/")
    print()
    print("To test locally:")
    print("  cd _site && python -m http.server 8080")
    print()
    print("To deploy to GitHub Pages, push _site/ contents to your")
    print("gh-pages branch, or configure GitHub Actions (see README).")
    print("=" * 60)


if __name__ == "__main__":
    build()
