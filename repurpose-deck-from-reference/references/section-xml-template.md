# Section XML Template

`python-pptx` は PowerPoint セクション（左ペインで章分けされるアレ）をサポートしないので、`presentation.xml` に `p14:sectionLst` を直接挿入する。

## 構造

```xml
<p:extLst>
  <p:ext uri="{521415D9-36F7-43E2-AB2F-B90AF26B5E84}">
    <p14:sectionLst xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">
      <p14:section name="A. Overview" id="{NEW-GUID}">
        <p14:sldIdLst>
          <p14:sldId id="2076138485"/>
          <p14:sldId id="2076138486"/>
        </p14:sldIdLst>
      </p14:section>
      <p14:section name="B. Next" id="{NEW-GUID}">
        ...
      </p14:section>
    </p14:sectionLst>
  </p:ext>
</p:extLst>
```

`</p:presentation>` の直前に挿入する。

## 注意

- セクション名に `&` `<` `>` を含むなら **XML escape** (`&amp;` / `&lt;` / `&gt;`)
- `id` は GUID（`uuid.uuid4()` で生成）、波括弧 `{...}` で囲む、**大文字**
- `p14:sldId id=` には `presentation.xml` の `p:sldIdLst` で使われている `sldId` の `id` 属性値（数値）を使う

## 実装例

```python
import zipfile, shutil, re, uuid
from pathlib import Path

PATH = Path("...pptx")
TMP = PATH.with_suffix(".tmp.pptx")
P14_NS = "http://schemas.microsoft.com/office/powerpoint/2010/main"
SECTION_EXT_URI = "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}"

SECTIONS = [
    ("A. Overview",                [1, 2, 3, 4]),
    ("B. Sessions の動かし方",      [5, 6, 7, 8]),
    ("C. GitHub 連携",              [9, 10]),
    ("D. Customize &amp; Collaborate", [11, 12]),  # MUST escape
    ("E. 継続実行と Sandboxes",     [13, 14, 15]),
    ("F. 導入と統制",                [16, 17, 18, 19]),
]


def build_section_xml(sld_ids_by_position):
    parts = [f'<p:extLst><p:ext uri="{SECTION_EXT_URI}">'
             f'<p14:sectionLst xmlns:p14="{P14_NS}">']
    for sec_name, positions in SECTIONS:
        sec_id = "{" + str(uuid.uuid4()).upper() + "}"
        parts.append(f'<p14:section name="{sec_name}" id="{sec_id}">'
                     f'<p14:sldIdLst>')
        for pos in positions:
            parts.append(f'<p14:sldId id="{sld_ids_by_position[pos - 1]}"/>')
        parts.append("</p14:sldIdLst></p14:section>")
    parts.append("</p14:sectionLst></p:ext></p:extLst>")
    return "".join(parts)


with zipfile.ZipFile(PATH, "r") as z:
    pres_xml = z.read("ppt/presentation.xml").decode("utf-8")
sld_lst = re.search(r"<p:sldIdLst>(.*?)</p:sldIdLst>", pres_xml, re.S)
sld_ids = re.findall(r'<p:sldId id="(\d+)"', sld_lst.group(1))
section_xml = build_section_xml(sld_ids)
pres_xml = re.sub(r"<p:extLst>.*?</p:extLst>", "", pres_xml, flags=re.S)
pres_xml = pres_xml.replace("</p:presentation>", f"{section_xml}</p:presentation>")
with zipfile.ZipFile(PATH, "r") as zin, zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "ppt/presentation.xml":
            data = pres_xml.encode("utf-8")
        zout.writestr(item, data)
shutil.move(str(TMP), str(PATH))
```

## Done Criteria

- 全 section 名の `&` が `&amp;` に escape されている
- 全 GUID が大文字、`{...}` で囲まれている
- `p14:sldId id=` に渡す数値が `presentation.xml` の sldIdLst に実在する
- 挿入後、`python com_test.py` で COM Open が通る
- PowerPoint で開いてサイドペインに章が表示される
