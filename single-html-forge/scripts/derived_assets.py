"""Static slide states and derived-asset identity. No browser dependency."""

from dataclasses import dataclass, field
import hashlib
import html
import json
import re


@dataclass
class Element:
    name: str
    attrs: dict
    start: int
    opening_end: int
    end: int
    self_closing: bool = False
    children: list = field(default_factory=list)


def elements(text):
    import verify_html as verifier
    roots, stack = [], []
    for token in verifier.lex(text):
        kind = token[0]
        if kind == "raw":
            raw = token[1]
            if raw.name == "title" and any(parent.name == "svg" for parent in stack):
                opening_end = verifier.lex_start_tag(text, raw.pos)[1]
                node = Element(raw.name, raw.attrs, raw.pos, opening_end,
                               opening_end + len(raw.content) + len("</title>"))
                stack[-1].children.append(node)
            continue
        if kind == "end":
            node = stack.pop()
            node.end = token[2] + len(token[1]) + 3
            continue
        tag = token[1]
        opening_end = verifier.lex_start_tag(text, tag.pos)[1]
        node = Element(tag.name, tag.attrs, tag.pos, opening_end, opening_end, tag.self_closing)
        (stack[-1].children if stack else roots).append(node)
        if not tag.self_closing and tag.name not in verifier.VOID:
            stack.append(node)
    return roots


def flatten(nodes):
    for node in nodes:
        yield node
        yield from flatten(node.children)


def slides(text):
    return [node for node in flatten(elements(text)) if "data-slide-id" in node.attrs]


def step_count(slide):
    values = [0]
    for node in flatten(slide.children):
        if "data-shf-step" in node.attrs:
            value = node.attrs["data-shf-step"]
            if not re.fullmatch(r"[0-9]{1,2}", value):
                raise ValueError("Steps must be integers from 0 through 99")
            values.append(int(value))
    if set(values) != set(range(max(values) + 1)):
        raise ValueError("Steps must be contiguous from 0")
    return max(values) + 1


def states(text):
    return [(slide.attrs["data-slide-id"], step) for slide in slides(text) for step in range(step_count(slide))]


def validate_steps(text):
    for slide in slides(text):
        count = step_count(slide)
        if slide.attrs.get("data-shf-print", "final") not in {"final", "all"}:
            raise ValueError("data-shf-print must be final or all")
        for node in flatten(slide.children):
            start = int(node.attrs.get("data-shf-step", "0"))
            if "data-shf-until" in node.attrs:
                until = node.attrs["data-shf-until"]
                if not re.fullmatch(r"[0-9]{1,2}", until) or not start <= int(until) < count:
                    raise ValueError("Invalid data-shf-until range")
                if "data-shf-step" not in node.attrs or slide.attrs.get("data-shf-print") != "all":
                    raise ValueError("Replacement steps require data-shf-print=all")
            if node.attrs.get("data-shf-effect", "fade") not in {"fade", "rise", "emphasis", "route"}:
                raise ValueError("Unknown step effect")
            if "data-shf-step" in node.attrs:
                for child in flatten(node.children):
                    if "data-shf-step" in child.attrs:
                        raise ValueError("Step groups must not be nested")


def digest(text):
    import verify_html as verifier
    material = [text[node.start:node.end] for node in slides(text)]
    for kind, *parts in verifier.lex(text):
        if kind == "raw" and parts[0].attrs.get("id") in {"shf-theme", "shf-css", "shf-runtime"}:
            material.append(parts[0].content)
    return hashlib.sha256(json.dumps(material, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def splice(text, replacements):
    for start, end, replacement in sorted(replacements, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def serialize_open(node, attrs):
    suffix = " /" if node.self_closing else ""
    return "<" + node.name + "".join(' ' + key + '="' + str(value) + '"' for key, value in attrs.items()) + suffix + ">"


def print_markup(text):
    output = []
    assets = []
    pages = []
    destinations = {}
    source_ids = {}
    for ordinal, slide in enumerate(slides(text), 1):
        for node in flatten([slide]):
            if "id" in node.attrs:
                identity = html.unescape(node.attrs["id"])
                if identity in source_ids:
                    raise ValueError(f"Duplicate slide content id: {identity}")
                source_ids[identity] = node.start
        count = step_count(slide)
        selected = range(count) if slide.attrs.get("data-shf-print") == "all" else [count - 1]
        for step in selected:
            prefix = f"shf-print-{ordinal}-{step}-"
            included = []
            excluded = []
            local_ids = {}
            for node in flatten([slide]):
                if any(start <= node.start < end for start, end in excluded):
                    continue
                start = int(node.attrs.get("data-shf-step", "0"))
                until = int(node.attrs.get("data-shf-until", "99"))
                if "data-shf-notes" in node.attrs or ("hidden" in node.attrs and node is not slide and "data-shf-step" not in node.attrs) or not start <= step <= until:
                    excluded.append((node.start, node.end))
                    continue
                included.append(node)
                if "id" in node.attrs:
                    identity = html.unescape(node.attrs["id"])
                    local_ids[identity] = prefix + identity
                    destinations.setdefault(identity, prefix + identity)
            pages.append((slide, step, prefix, included, excluded, local_ids))

    id_references = {"for", "aria-labelledby", "aria-describedby", "aria-details", "aria-errormessage", "aria-controls", "aria-owns", "aria-activedescendant", "aria-flowto"}
    for slide, step, prefix, included, excluded, local_ids in pages:
        replacements = [(start - slide.start, end - slide.start, "") for start, end in excluded]
        for node in included:
            attrs = {key: value for key, value in node.attrs.items() if key not in {"hidden", "data-shf-step", "data-shf-until", "data-shf-effect", "data-slide-id", "tabindex"}}
            if node is slide:
                attrs.pop("aria-hidden", None)
                attrs["data-shf-print-slide"] = slide.attrs["data-slide-id"]
                attrs["data-shf-print-step"] = str(step)
            if "id" in attrs:
                attrs["id"] = prefix + attrs["id"]
            for attribute in id_references | {"href"}:
                if attribute not in attrs:
                    continue
                value = html.unescape(attrs[attribute]).strip()
                if attribute == "href" and not value.startswith("#"):
                    continue
                references = [value[1:]] if attribute == "href" else value.split()
                mapped = []
                for identity in references:
                    target = local_ids.get(identity, destinations.get(identity))
                    if target is None:
                        raise ValueError(f"Print reference has no visible target: {attribute}={identity}")
                    mapped.append(target)
                rewritten = "#" + mapped[0] if attribute == "href" else " ".join(mapped)
                attrs[attribute] = html.escape(rewritten, quote=True)
            if "data-asset-ref" in attrs:
                attrs["data-asset-ref"] = prefix + attrs["data-asset-ref"]
                import verify_html as verifier
                mime, payload = verifier.decode_data_uri(attrs["src"])
                assets.append({"id": attrs["data-asset-ref"], "mime": mime, "sha256": hashlib.sha256(payload).hexdigest(), "alt": attrs.get("alt", "")})
            replacements.append((node.start - slide.start, node.opening_end - slide.start, serialize_open(node, attrs)))
        output.append(splice(text[slide.start:slide.end], replacements))
    return '<div id="shf-print">' + "\n".join(output) + '</div>', assets


def check_derived(text, model):
    if model.get("schemaVersion") != 2:
        return
    if model.get("sourceDigest") != digest(text):
        raise ValueError("Derived assets are stale; finalize the deck again")
    roots = list(flatten(elements(text)))
    print_nodes = [node for node in roots if node.attrs.get("id") == "shf-print"]
    expected_print, _ = print_markup(text)
    if len(print_nodes) != 1 or text[print_nodes[0].start:print_nodes[0].end] != expected_print:
        raise ValueError("Print representation does not match slide states")
    thumbnails = model.get("thumbnails")
    if not isinstance(thumbnails, list):
        raise ValueError("schema 2 requires a thumbnails list")
    images = [node for node in roots if "data-shf-thumbnail" in node.attrs]
    if thumbnails:
        expected_ids = [slide.attrs["data-slide-id"] for slide in slides(text)]
        if [item.get("slideId") for item in thumbnails if isinstance(item, dict)] != expected_ids:
            raise ValueError("Thumbnail coverage or order differs from slides")
    if len(images) != len(thumbnails):
        raise ValueError("Thumbnail model/image count mismatch")
    for image, item in zip(images, thumbnails):
        slide = next(slide for slide in slides(text) if slide.attrs["data-slide-id"] == item["slideId"])
        if item.get("step") != step_count(slide) - 1 or item.get("width") != 320 or item.get("height") != 180:
            raise ValueError("Unsupported thumbnail rendering conditions")
        if image.attrs.get("data-shf-thumbnail") != item["slideId"] or image.attrs.get("data-asset-ref") != item.get("assetId"):
            raise ValueError("Thumbnail is associated with the wrong slide")
        import verify_html as verifier
        from embed_assets import png_size
        mime, payload = verifier.decode_data_uri(image.attrs["src"])
        if mime != "image/png" or len(payload) < 24 or png_size(payload) != (320, 180):
            raise ValueError("Thumbnail PNG dimensions must be exactly 320x180")
        if image.attrs.get("width") != "320" or image.attrs.get("height") != "180":
            raise ValueError("Thumbnail dimensions disagree with HTML attributes")
        owner = next((node for node in roots if node.opening_end <= image.start < node.end and "data-shf-goto" in node.attrs), None)
        if owner is None or owner.attrs["data-shf-goto"] != item["slideId"]:
            raise ValueError("Thumbnail is not inside its slide navigation button")


def finalize(text, thumbnails):
    import verify_html as verifier
    tokens = verifier.lex(text)
    model_raw = next((parts[0] for kind, *parts in tokens if kind == "raw" and parts[0].attrs.get("id") == "shf-model"), None)
    if model_raw is None:
        raise ValueError("Finalization requires a shf-model JSON block; start from a current deck skeleton")
    model = json.loads(model_raw.content)
    replacements = []
    nodes = list(flatten(elements(text)))
    old_refs = set()
    for node in nodes:
        if node.attrs.get("id") == "shf-print" or "data-shf-thumbnail" in node.attrs:
            replacements.append((node.start, node.end, ""))
            old_refs.update(child.attrs["data-asset-ref"] for child in flatten([node]) if "data-asset-ref" in child.attrs)
    clean = splice(text, replacements)
    model["assets"] = [asset for asset in model.get("assets", []) if asset["id"] not in old_refs]
    print_content, print_assets = print_markup(clean)
    model.update(schemaVersion=2, sourceDigest=digest(clean), thumbnails=[])
    model["assets"].extend(print_assets)
    additions = []
    links = [node for node in flatten(elements(clean)) if "data-shf-goto" in node.attrs]
    for slide_id, step, uri, asset in thumbnails:
        link = next(node for node in links if node.attrs["data-shf-goto"] == slide_id)
        image = '<img data-shf-thumbnail="' + html.escape(slide_id, quote=True) + '" data-asset-ref="' + asset["id"] + '" src="' + uri + '" alt="" width="320" height="180">'
        additions.append((link.opening_end, link.opening_end, image))
        model["assets"].append(asset)
        model["thumbnails"].append({"slideId": slide_id, "step": step, "assetId": asset["id"], "width": 320, "height": 180})
    clean = splice(clean, additions)
    model_raw = next(parts[0] for kind, *parts in verifier.lex(clean) if kind == "raw" and parts[0].attrs.get("id") == "shf-model")
    start = verifier.lex_start_tag(clean, model_raw.pos)[1]
    encoded = json.dumps(model, ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c")
    clean = clean[:start] + encoded + clean[start + len(model_raw.content):]
    return clean.replace('<script id="shf-model"', print_content + '\n<script id="shf-model"', 1)