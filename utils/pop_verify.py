import anthropic
import base64
import json
import re

def verify_pop_with_ai(image_data: bytes, mimetype: str, expected_amount: float,
                        expected_ref: str = "", beneficiary_hint: str = "Sugar Trade") -> dict:
    """
    Use Claude vision to analyse a proof of payment image.
    Returns a dict with: confidence, findings, recommendation, extracted_data
    """
    client = anthropic.Anthropic()

    b64 = base64.standard_b64encode(image_data).decode("utf-8")

    prompt = f"""You are a financial document verification specialist for a commodity trading company.

Analyse this proof of payment (PoP) document carefully.

EXPECTED PAYMENT DETAILS:
- Amount: R {expected_amount:,.2f}
- Reference (if any): {expected_ref}
- Expected beneficiary contains: {beneficiary_hint}

Please verify and extract the following:
1. Is this a legitimate bank-issued proof of payment or transaction receipt?
2. What is the transaction amount shown?
3. What is the transaction date?
4. What is the sender/account name?
5. What is the beneficiary/recipient name?
6. What is the transaction reference number?
7. What bank/institution issued this?
8. Does the amount match the expected R {expected_amount:,.2f}?
9. Are there any signs this document may be altered, fraudulent, or suspicious?

Respond ONLY in valid JSON with this exact structure:
{{
  "is_legitimate_pop": true/false,
  "confidence_pct": 0-100,
  "extracted": {{
    "amount": "extracted amount as string or null",
    "date": "extracted date as string or null",
    "sender_name": "name or null",
    "beneficiary_name": "name or null",
    "reference": "reference or null",
    "bank": "bank name or null"
  }},
  "amount_matches": true/false/null,
  "findings": ["finding 1", "finding 2"],
  "red_flags": ["flag 1"] or [],
  "recommendation": "APPROVE / QUERY / REJECT",
  "summary": "2-3 sentence human-readable summary"
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mimetype,
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": prompt}
                    ],
                }
            ],
        )

        text = response.content[0].text.strip()
        # Strip markdown fences if present
        text = re.sub(r"```json|```", "", text).strip()
        result = json.loads(text)
        result["error"] = None
        return result

    except json.JSONDecodeError as e:
        return {
            "error": f"Could not parse AI response: {e}",
            "confidence_pct": 0,
            "recommendation": "QUERY",
            "summary": "AI analysis could not be completed. Please review manually.",
            "findings": [],
            "red_flags": [],
            "extracted": {},
            "is_legitimate_pop": None,
            "amount_matches": None,
        }
    except Exception as e:
        return {
            "error": str(e),
            "confidence_pct": 0,
            "recommendation": "QUERY",
            "summary": "AI analysis failed. Please review the document manually.",
            "findings": [],
            "red_flags": [],
            "extracted": {},
            "is_legitimate_pop": None,
            "amount_matches": None,
        }
