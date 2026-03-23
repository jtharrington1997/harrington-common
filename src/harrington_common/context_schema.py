from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Any


ContextKind = Literal["text", "status", "number", "date", "list"]


@dataclass(frozen=True)
class ContextItem:
    key: str
    label: str
    value: Any
    kind: ContextKind = "text"
    notes: str | None = None
    source: str | None = None


@dataclass(frozen=True)
class ContextSection:
    title: str
    items: tuple[ContextItem, ...]
    summary: str | None = None


@dataclass(frozen=True)
class AppContext:
    app_name: str
    sections: tuple[ContextSection, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


def context_to_markdown(context: AppContext) -> str:
    """Render structured context as markdown for reports or debugging."""
    lines: list[str] = [f"# {context.app_name} Context", ""]

    for section in context.sections:
        lines.append(f"## {section.title}")
        if section.summary:
            lines.append(section.summary)
            lines.append("")

        for item in section.items:
            if item.kind == "list" and isinstance(item.value, (list, tuple)):
                lines.append(f"- **{item.label}:**")
                for entry in item.value:
                    lines.append(f"  - {entry}")
            else:
                lines.append(f"- **{item.label}:** {item.value}")

            if item.notes:
                lines.append(f"  - Notes: {item.notes}")
            if item.source:
                lines.append(f"  - Source: {item.source}")

        lines.append("")

    if context.metadata:
        lines.append("## Metadata")
        for key, value in context.metadata.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"
