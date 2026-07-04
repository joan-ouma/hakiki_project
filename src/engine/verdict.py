def compose_verdict(claim: str | None, matches: dict | None, media_result: dict | None = None) -> str:
    """Compose a sourced verdict reply from match results and/or media analysis."""
    parts = []

    if claim:
        parts.append(f'Claim: "{claim}"\n')

    # Claim matching results
    if matches:
        seed = matches.get("seed_match")
        fc = matches.get("factcheck_match")

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
                "This claim could not be confirmed or denied from available sources.\n"
            )

    # Media analysis results
    if media_result:
        if media_result.get("error"):
            parts.append(f"MEDIA CHECK: Could not analyze image ({media_result['error']})")
        else:
            label = media_result.get("label", "unknown")
            prob = media_result.get("ai_probability", 0)
            parts.append("MEDIA AUTHENTICITY CHECK:")
            parts.append(f"  Verdict: {label}")
            parts.append(f"  AI-generation probability: {prob:.0%}")
            parts.append("  Model: ViT-based classifier (generic, not dialect-specific)")
            parts.append("")

    parts.append("-- Hakiki Bot (automated, not legal advice)")
    return "\n".join(parts)
