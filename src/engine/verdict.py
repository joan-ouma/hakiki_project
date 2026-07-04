def compose_verdict(claim: str, match_result: dict, media_score: float = None) -> str:
    """
    Combines the claim match and media authenticity score into a final response.
    Implements symmetric confidence gating for deepfakes.
    """
    reply = "Hakiki Fact Check:\n\n"
    
    if claim != "NO CLAIM FOUND" and claim != "ERROR_EXTRACTING_CLAIM":
        reply += f"Claim: '{claim}'\n"
        
        if match_result:
            reply += "Claim Verdict: VERIFIED CONTEXT FOUND 🔍\n"
            reply += f"Source: {match_result['title']}\n"
            reply += f"Context: {match_result['content_snippet']}\n"
            if match_result.get('url'):
                reply += f"Link: {match_result['url']}\n"
        else:
            reply += "Claim Verdict: UNVERIFIED ⚠️\n"
            reply += "Source: No matching records found in our NG-CDF/Audit database or Google Fact Check.\n"
    else:
        reply += "Claim: No clear factual claim detected in the text.\n"
        
    reply += "\n"
    
    # Media checking (Symmetric gating)
    # Let's say our ViT model needs > 0.8 to confidently call it fake, 
    # and < 0.2 to confidently call it real. Everything else is unverified.
    if media_score is not None:
        if media_score >= 0.8:
            reply += "Media Authenticity: LIKELY MANIPULATED/AI-GENERATED ❌\n"
            reply += f"Confidence: High ({int(media_score * 100)}%)\n"
            reply += "Source: Deepfake ViT Image Classifier Analysis\n"
        elif media_score <= 0.2:
            reply += "Media Authenticity: LIKELY AUTHENTIC ✅\n"
            reply += f"Confidence: High ({int((1.0 - media_score) * 100)}%)\n"
            reply += "Source: Deepfake ViT Image Classifier Analysis\n"
        else:
            reply += "Media Authenticity: INCONCLUSIVE ⚠️\n"
            reply += f"Confidence: Low (AI score {int(media_score * 100)}%)\n"
            reply += "Source: Deepfake ViT Image Classifier Analysis\n"
            
    return reply.strip()
