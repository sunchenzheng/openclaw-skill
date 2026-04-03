---
name: "docx-reader"
description: "读取和处理 Word 文档（.docx）。识别文档文字内容、提取图片、生成结构化摘要。触发场景：用户发送或指定 .docx 文件路径，要求读取、总结或分析内容。"
---

# Word 文档读取技能

## 核心能力

1. **读取文档文字** — 提取 .docx 中的段落文本、表格内容
2. **提取图片** — 将文档中的图片导出为独立文件
3. **结构化摘要** — 生成文档内容大纲和关键信息提取
4. **试卷评测** — 结合 math-exam-evaluator，识别数学试卷中的题目和学生答案

## 使用方式

```python
# 基本读取
from docx import Document
doc = Document("C:\\path\\to\\file.docx")
for para in doc.paragraphs:
    if para.text.strip():
        print(para.text)

# 读取表格
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text, end="\t")
        print()

# 提取图片
for rel in doc.part.rels.values():
    if "image" in rel.target_ref:
        img_data = rel.target_part.blob
        img_name = rel.target_ref.split("/")[-1]
        with open(f"output/{img_name}", "wb") as f:
            f.write(img_data)
```

## 文档结构识别

```python
# 识别标题层级
def extract_headings(doc):
    headings = []
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            level = para.style.name.replace("Heading ", "")
            headings.append({"level": level, "text": para.text})
    return headings
```

## 常用属性参考

| 属性 | 说明 |
|------|------|
| `doc.paragraphs` | 所有段落 |
| `doc.tables` | 所有表格 |
| `doc.inline_shapes` | 所有嵌入式图片 |
| `doc.part.rels` | 文档关系（包含图片引用） |

## 图片导出路径

导出目录结构：
```
原文件目录/
├── 原文件名.docx
└── extracted_images/
    ├── image1.png
    ├── image2.jpg
    └── ...
```

## 注意事项

- 只支持 `.docx`（Office Open XML），不支持 `.doc`（旧版格式）
- `.doc` 文件需先转换为 `.docx`（可用 PowerShell + Word COM 自动化）
- 文档中的公式（MathType/OMML）以纯文本形式提取
- 加密保护的文档无法读取（会报错）
