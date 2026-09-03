from __future__ import annotations

from typing import Optional

from cli.ui.icons import ANALYZER_ICONS


ALL_ANALYZERS = list(ANALYZER_ICONS.keys())


def _description_for(name: str) -> str:
    descriptions = {
        "seo": "Meta tags, structured data, sitemap",
        "performance": "Load time, bundle size, caching",
        "accessibility": "WCAG contrast, ARIA, keyboard nav",
        "design": "Design-system/token consistency",
        "nlp": "Reading level, tone, copy clarity",
        "security": "Security headers, HTTPS, vulnerabilities",
    }
    return descriptions.get(name, name.title())


def pick_analyzers(console) -> Optional[list[str]]:
    """Interactive analyzer picker.

    Returns a list of analyzer names if the user makes a selection,
    or ``None`` if the picker is unavailable/canceled and the caller
    should fall back to the default set.
    """
    try:
        import questionary
    except ImportError:
        console.print(
            "[info]INFO: install uibench-cli[interactive] for the analyzer picker — "
            "running all analyzers.[/info]"
        )
        return None

    choices = []
    for name in ALL_ANALYZERS:
        icon, ascii_fallback, _style = ANALYZER_ICONS.get(name, ("", "[???]", "dim"))
        label = f"{icon} {name.title()}" if console.is_terminal else f"{ascii_fallback} {name.title()}"
        choices.append(
            {
                "name": label,
                "value": name,
                "checked": True,
            }
        )

    try:
        selected = questionary.checkbox(
            "Which analyzers would you like to run? (space to toggle, enter to confirm, a to toggle all)",
            choices=choices,
        ).unsafe_ask()
    except KeyboardInterrupt:
        return None

    if selected is None:
        return None

    return [str(item) for item in selected if isinstance(item, str)]
