def compose_verdict(claim: str, matches: dict) -> str:
    """Compose a sourced verdict reply from match results."""
    seed = matches.get("seed_match")
    fc = matches.get("factcheck_match")

    parts = [f'Claim: "{claim}"\n']

    if seed:
        parts.append("PUBLIC RECORD FOUND:")
        parts.append(f"  Source: {seed['source']}")
        if seed["constituency"]:
            parts.append(f"  Constituency: {seed['constituency']}")
        if seed["project"]:
            parts.append(f"  Project: {seed['project']}")
        if seed["details"]:
            parts.append(f"  Details: {seed['details']}")
        if seed["url"]:
            parts.append(f"  Reference: {seed['url']}")
        parts.append("")

    if fc:
        parts.append("FACT-CHECK MATCH:")
        parts.append(f"  Rating: {fc['rating']}")
        parts.append(f"  By: {fc['publisher']}")
        if fc["url"]:
            parts.append(f"  Source: {fc['url']}")
        parts.append("")

    if not seed and not fc:
        parts.append(
            "UNVERIFIED: No matching public record or fact-check found. "
            "This claim could not be confirmed or denied from available sources."
        )

    parts.append("-- Hakiki Bot (automated, not legal advice)")
    return "\n".join(parts)
