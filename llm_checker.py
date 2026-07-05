from openai import AzureOpenAI

AZURE_OAI_ENDPOINT = ""
AZURE_OAI_KEY = ""
DEPLOYMENT_NAME = "gpt-5.4-nano"

client = AzureOpenAI(
    azure_endpoint=AZURE_OAI_ENDPOINT,
    api_key=AZURE_OAI_KEY,
    api_version="2024-02-01"
)

def check_near_duplicate(current_invoice, previous_invoices):
    if not previous_invoices:
        return True, "OK"
    
    prompt = f"""
You are a fraud detection expert reviewing invoices.

Current invoice:
{current_invoice}

Previously processed invoices:
{previous_invoices}

Check if the current invoice is a near-duplicate of any previous invoice.
Near-duplicate means: same vendor, same or very similar amount, but different invoice number.

Reply in this exact format:
VERDICT: SUSPICIOUS or CLEAN
REASON: one sentence explanation
"""
    
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a fraud detection expert."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=150
    )
    
    reply = response.choices[0].message.content.strip()
    
    if "SUSPICIOUS" in reply:
        return False, reply
    return True, "OK"


if __name__ == "__main__":
    print("LLM Checker ready!")