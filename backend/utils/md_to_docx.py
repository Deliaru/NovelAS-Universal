"""
Markdown to DOCX converter utility.
Converts Markdown files to Word documents with proper formatting.
"""

import re
from pathlib import Path
from typing import Optional
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def convert_md_to_docx(
    md_path: str,
    docx_path: Optional[str] = None,
    title: Optional[str] = None,
    font_name: str = "微软雅黑",
    font_size: int = 12,
) -> str:
    """
    Convert a Markdown file to DOCX format.

    Args:
        md_path: Path to the input Markdown file
        docx_path: Path to the output DOCX file (optional, defaults to same name with .docx extension)
        title: Document title (optional, extracted from first # heading if not provided)
        font_name: Font name for the document (default: 宋体)
        font_size: Font size in points (default: 12)

    Returns:
        Path to the created DOCX file
    """
    md_path = Path(md_path)

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    # Determine output path
    if docx_path is None:
        docx_path = md_path.with_suffix('.docx')
    else:
        docx_path = Path(docx_path)

    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Create document
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = font_name
    font.size = Pt(font_size)

    # Parse and convert markdown
    lines = md_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        # Skip YAML frontmatter
        if i == 0 and line == '---':
            i += 1
            while i < len(lines) and lines[i].strip() != '---':
                i += 1
            i += 1
            continue

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Heading 1 (# )
        if line.startswith('# '):
            text = line[2:].strip()
            if title is None:
                title = text
            p = doc.add_heading(text, level=1)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Heading 2 (## )
        elif line.startswith('## '):
            text = line[3:].strip()
            doc.add_heading(text, level=2)

        # Heading 3 (### )
        elif line.startswith('### '):
            text = line[4:].strip()
            doc.add_heading(text, level=3)

        # Horizontal rule (---)
        elif line.startswith('---') and len(line.strip()) >= 3:
            p = doc.add_paragraph()
            p.add_run('─' * 50)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Comment (<!-- -->)
        elif line.startswith('<!--'):
            # Skip comments
            while i < len(lines) and '-->' not in lines[i]:
                i += 1

        # Regular paragraph
        else:
            # Collect multi-line paragraph
            para_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('---'):
                para_lines.append(lines[i].rstrip())
                i += 1

            para_text = ' '.join(para_lines)

            # Add paragraph with inline formatting
            p = doc.add_paragraph()
            _add_formatted_text(p, para_text, font_name)

            continue  # Skip the i += 1 at the end

        i += 1

    # Save document
    doc.save(str(docx_path))

    return str(docx_path)


def _add_formatted_text(paragraph, text: str, font_name: str = "微软雅黑"):
    """
    Add text to paragraph with inline formatting (bold, italic, etc.).
    """
    # Simple regex-based inline formatting
    # This is a basic implementation - can be enhanced

    # Split by bold (**text**)
    parts = re.split(r'(\*\*.*?\*\*)', text)

    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            # Bold text
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            run.font.name = font_name
        else:
            # Regular text (may contain italic)
            italic_parts = re.split(r'(\*.*?\*)', part)
            for ipart in italic_parts:
                if ipart.startswith('*') and ipart.endswith('*') and not ipart.startswith('**'):
                    # Italic text
                    run = paragraph.add_run(ipart[1:-1])
                    run.italic = True
                    run.font.name = font_name
                else:
                    # Plain text
                    run = paragraph.add_run(ipart)
                    run.font.name = font_name


def batch_convert_md_to_docx(
    input_dir: str,
    output_dir: Optional[str] = None,
    pattern: str = "*.md",
    **kwargs
) -> list[str]:
    """
    Batch convert all Markdown files in a directory to DOCX.

    Args:
        input_dir: Directory containing Markdown files
        output_dir: Output directory (optional, defaults to input_dir)
        pattern: Glob pattern for matching files (default: *.md)
        **kwargs: Additional arguments passed to convert_md_to_docx

    Returns:
        List of created DOCX file paths
    """
    input_dir = Path(input_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    if output_dir is None:
        output_dir = input_dir
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    created_files = []

    for md_file in input_dir.glob(pattern):
        if md_file.is_file():
            docx_path = output_dir / md_file.with_suffix('.docx').name
            result = convert_md_to_docx(str(md_file), str(docx_path), **kwargs)
            created_files.append(result)

    return created_files
