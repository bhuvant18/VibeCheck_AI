"""
VibeCheck Agent - Core verification logic using Google Gen AI SDK
Implements the "Single-Shot Structured Grounding" architecture with dual tools:
1. Google Search - for verifying general facts
2. Semantic Scholar - for verifying academic citations
3. URL Validator - for checking if URLs are valid or broken
"""

import os
import re
import json
import requests
from typing import List, Optional
from pydantic import BaseModel, Field
from urllib.parse import urlparse
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path

# --- Load Environment Variables ---
# Try to load from parent directory (root of project)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- Configuration ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
# Handle default placeholder from .env.example
if PROJECT_ID == "your-project-id":
    PROJECT_ID = None

LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
MODEL_ID = "gemini-2.5-flash"


# --- Data Models (Pydantic) ---
class ClaimAnalysis(BaseModel):
    """Structure for each analyzed claim"""
    original_text: str = Field(..., description="The exact sentence being analyzed")
    type: str = Field(..., description="FACT, CITATION, or URL")
    status: str = Field(..., description="VERIFIED, HALLUCINATION, SUSPICIOUS, OPINION, or BROKEN_URL")
    reasoning: str = Field(..., description="Brief explanation of the finding")
    correction: Optional[str] = Field(None, description="Corrected factual statement if false")
    source_url: Optional[str] = Field(None, description="URL supporting the verification")
    confidence_score: int = Field(default=50, description="0-100 confidence level")


class VerificationReport(BaseModel):
    """Full verification report containing all claims"""
    claims: List[ClaimAnalysis]


# --- Custom Tool: Semantic Scholar Citation Verifier ---
def verify_paper_tool(query: str) -> str:
    """
    Verifies if a research paper exists using the Semantic Scholar API.
    Use this when the text mentions a specific paper, author, or study year.
    
    Args:
        query: The title, author name, or citation to search for
        
    Returns:
        A string indicating if the paper was found with details, or NOT FOUND
    """
    try:
        # Clean query to improve academic search match
        clean_query = query.replace("et al.", "").replace("(", "").replace(")", "").strip()
        
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": clean_query,
            "fields": "title,authors,year,url,abstract,citationCount",
            "limit": 1
        }
        
        # 5 second timeout to keep the agent fast
        response = requests.get(base_url, params=params, timeout=5)
        
        if not response.ok:
            return "API Error: Semantic Scholar unreachable."
            
        data = response.json()
        if not data.get('data'):
            return f"NOT FOUND: No matching paper found for '{clean_query}' in the academic database. This citation is likely hallucinated."
            
        paper = data['data'][0]
        authors = ", ".join([a['name'] for a in paper.get('authors', [])[:3]])
        citation_count = paper.get('citationCount', 0)
        
        return (
            f"FOUND: '{paper['title']}' ({paper.get('year', 'N/A')}) by {authors}. "
            f"Citations: {citation_count}. URL: {paper.get('url', 'N/A')}"
        )
        
    except requests.Timeout:
        return "API Timeout: Semantic Scholar took too long to respond."
    except Exception as e:
        return f"Error verifying paper: {str(e)}"


def verify_paper(title: str, author_last_name: str = None) -> dict:
    """
    Alternative function with structured output for direct use.
    
    Args:
        title: The title of the paper to verify
        author_last_name: Optional last name of an author
        
    Returns:
        Dictionary with verification results
    """
    try:
        clean_query = title.replace("et al.", "").strip()
        if author_last_name:
            clean_query = f"{author_last_name} {clean_query}"
            
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": clean_query,
            "fields": "title,authors,year,url,abstract,citationCount",
            "limit": 1
        }
        
        response = requests.get(base_url, params=params, timeout=5)
        
        if not response.ok:
            return {"found": False, "error": "API unreachable"}
            
        data = response.json()
        
        if not data.get('data'):
            return {"found": False, "error": "Paper not found"}
            
        paper = data['data'][0]
        authors = [a['name'] for a in paper.get('authors', [])]
        
        # Soft check on author if provided
        author_match = True
        if author_last_name:
            author_match = any(author_last_name.lower() in a.lower() for a in authors)
            
        return {
            "found": True,
            "title": paper['title'],
            "year": paper.get('year'),
            "url": paper.get('url'),
            "authors": authors[:3],
            "author_match": author_match,
            "citation_count": paper.get('citationCount', 0)
        }
        
    except Exception as e:
        return {"found": False, "error": str(e)}


# --- URL Validation Functions ---
def extract_urls(text: str) -> List[str]:
    """
    Extract all URLs from the given text.
    
    Args:
        text: The text to search for URLs
        
    Returns:
        List of URLs found in the text
    """
    # Regex pattern to match URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\-.~:/?#\[\]@!$&\'()*+,;=%]*'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # Remove duplicates


def check_url_validity(url: str) -> dict:
    """
    Check if a URL is valid and accessible.
    
    Args:
        url: The URL to check
        
    Returns:
        Dictionary with validation results including status code and accessibility
    """
    result = {
        "url": url,
        "is_valid": False,
        "is_accessible": False,
        "status_code": None,
        "error": None,
        "redirect_url": None
    }
    
    # First, validate URL format
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            result["error"] = "Invalid URL format"
            return result
        result["is_valid"] = True
    except Exception as e:
        result["error"] = f"URL parsing error: {str(e)}"
        return result
    
    # Then, check if URL is accessible
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        
        # Some servers don't support HEAD, try GET
        if response.status_code >= 400:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True, stream=True)
            response.close()
        
        result["status_code"] = response.status_code
        result["is_accessible"] = response.status_code < 400
        
        # Check if there was a redirect
        if response.url != url:
            result["redirect_url"] = response.url
            
    except requests.Timeout:
        result["error"] = "Request timed out"
    except requests.ConnectionError:
        result["error"] = "Connection failed - URL may not exist"
    except requests.TooManyRedirects:
        result["error"] = "Too many redirects"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def verify_url_tool(url: str) -> str:
    """
    Verifies if a URL is valid and accessible.
    Use this when the text contains a URL that needs to be validated.
    
    Args:
        url: The URL to verify
        
    Returns:
        A string indicating if the URL is valid and accessible
    """
    result = check_url_validity(url)
    
    if not result["is_valid"]:
        return f"INVALID URL: '{url}' - {result['error']}"
    
    if result["is_accessible"]:
        redirect_info = ""
        if result["redirect_url"]:
            redirect_info = f" (redirects to: {result['redirect_url']})"
        return f"VALID URL: '{url}' is accessible (HTTP {result['status_code']}){redirect_info}"
    else:
        error_msg = result["error"] or f"HTTP {result['status_code']}"
        return f"BROKEN URL: '{url}' is not accessible - {error_msg}"


def validate_all_urls(text: str) -> List[dict]:
    """
    Extract and validate all URLs in the given text.
    
    Args:
        text: The text containing URLs to validate
        
    Returns:
        List of dictionaries with URL validation results
    """
    urls = extract_urls(text)
    results = []
    
    for url in urls:
        validation = check_url_validity(url)
        results.append(validation)
    
    return results


def fetch_url_content(url: str, max_chars: int = 5000) -> dict:
    """
    Fetch and extract the main text content from a URL.
    
    Args:
        url: The URL to fetch content from
        max_chars: Maximum characters to extract (default 5000)
        
    Returns:
        Dictionary with extracted content and metadata
    """
    result = {
        "url": url,
        "success": False,
        "title": None,
        "content": None,
        "error": None
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        if response.status_code >= 400:
            result["error"] = f"HTTP {response.status_code}"
            return result
        
        # Try to extract text content
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'text/html' in content_type or 'application/xhtml' in content_type:
            # Parse HTML and extract text
            html = response.text
            
            # Remove script and style elements
            import re
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)
            
            # Extract title
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if title_match:
                result["title"] = title_match.group(1).strip()
            
            # Remove all HTML tags
            text = re.sub(r'<[^>]+>', ' ', html)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Decode HTML entities
            import html as html_module
            text = html_module.unescape(text)
            
            # Truncate if too long
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            result["content"] = text
            result["success"] = True
            
        elif 'application/json' in content_type:
            # Handle JSON responses
            result["content"] = str(response.json())[:max_chars]
            result["success"] = True
            
        elif 'text/plain' in content_type:
            result["content"] = response.text[:max_chars]
            result["success"] = True
            
        else:
            result["error"] = f"Unsupported content type: {content_type}"
            
    except requests.Timeout:
        result["error"] = "Request timed out"
    except requests.ConnectionError:
        result["error"] = "Connection failed"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def fetch_all_url_contents(text: str) -> List[dict]:
    """
    Extract all URLs from text and fetch their contents.
    
    Args:
        text: The text containing URLs
        
    Returns:
        List of dictionaries with URL contents
    """
    urls = extract_urls(text)
    results = []
    
    for url in urls:
        content_result = fetch_url_content(url)
        results.append(content_result)
    
    return results


# --- Main Verification Engine ---
def verify_content(text_input: str, api_key: str = None) -> VerificationReport:
    """
    Main verification function that uses Gemini with dual tools.
    
    Args:
        text_input: The text to verify for hallucinations
        api_key: Optional API key (uses environment variable if not provided)
        
    Returns:
        VerificationReport with all analyzed claims
    """
    # Pre-check: Validate all URLs in the text
    url_validations = validate_all_urls(text_input)
    
    # Fetch content from all URLs to verify claims against actual page content
    url_contents = fetch_all_url_contents(text_input)
    
    # Initialize Client (Supports both Vertex AI and API Key modes)
    use_vertex = bool(PROJECT_ID) and not api_key  # Only use Vertex if no API key provided
    
    if use_vertex:
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION
        )
    else:
        # Use provided API key or fall back to environment variable
        key = api_key
        if not key:
            key = os.getenv("GEMINI_API_KEY")
        if not key:
            key = os.getenv("GOOGLE_API_KEY")
        
        if not key:
            raise ValueError("No API key provided. Please provide an API key or set GEMINI_API_KEY environment variable.")
            
        client = genai.Client(api_key=key)

    # 1. Define Tools
    google_search_tool = types.Tool(google_search=types.GoogleSearch())
    
    # Wrap the Python function as a tool for Gemini
    scholar_tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration.from_callable(
                client=client,
                callable=verify_paper_tool
            )
        ]
    )

    # Build URL validation context for the prompt
    url_context = ""
    if url_validations:
        url_context = "\n\nURL VALIDATION RESULTS (pre-checked):\n"
        for uv in url_validations:
            status = "✅ ACCESSIBLE" if uv["is_accessible"] else "❌ BROKEN/INACCESSIBLE"
            error_info = f" - {uv['error']}" if uv.get("error") else ""
            status_code = f" (HTTP {uv['status_code']})" if uv.get("status_code") else ""
            url_context += f"- {uv['url']}: {status}{status_code}{error_info}\n"
    
    # Build URL content context for the prompt
    url_content_context = ""
    if url_contents:
        url_content_context = "\n\nURL CONTENT EXTRACTED (for verification against claims):\n"
        for uc in url_contents:
            if uc["success"] and uc["content"]:
                title_info = f" - Title: {uc['title']}" if uc.get("title") else ""
                # Truncate content for prompt to avoid token limits
                content_preview = uc["content"][:2000] + "..." if len(uc["content"]) > 2000 else uc["content"]
                url_content_context += f"\n--- URL: {uc['url']}{title_info} ---\n{content_preview}\n"
            else:
                error_info = uc.get("error", "Unknown error")
                url_content_context += f"\n--- URL: {uc['url']} ---\nCould not fetch content: {error_info}\n"

    # 2. Construct the System Prompt
    prompt = f"""
    You are VibeCheck, an elite Fact-Verification Engine designed to detect AI hallucinations.
    
    MISSION: Analyze the following text for factual accuracy, fake citations, broken URLs, and URL content mismatches.
    
    INSTRUCTIONS:
    1. Break the text into distinct factual claims or sentences.
    2. For GENERAL FACTS (news, history, science, current events):
       - Use Google Search to verify the facts
    3. For ACADEMIC CITATIONS (papers, studies, research):
       - Use the 'verify_paper_tool' function
    4. For URLs in the text:
       - Check the URL VALIDATION RESULTS to see if URLs are accessible
       - **CRITICAL**: Read the URL CONTENT EXTRACTED section carefully
       - Compare the actual content from the URL against what the text claims about it
       - If the URL content does NOT match or support the claim, this is a HALLUCINATION
    5. CLASSIFICATION:
       - VERIFIED: Claim is factually accurate AND URL content (if any) supports the claim
       - HALLUCINATION: Claim is false, citation doesn't exist, OR URL content contradicts/doesn't support the claim
       - SUSPICIOUS: Cannot fully verify, needs review
       - OPINION: Subjective statement, skip verification
       - BROKEN_URL: URL is not accessible or returns an error
    
    6. **CORRECTION RULES (VERY IMPORTANT)**:
       For HALLUCINATIONS, you MUST provide a correction:
       
       a) If the TEXT is wrong but URL is correct:
          - Correction should contain the CORRECT TEXT based on what the URL actually says
          - Keep the same URL in source_url
       
       b) If the URL is wrong but TEXT claim might be true:
          - Use Google Search to find the CORRECT URL that actually supports the claim
          - Correction should include the correct URL
          - Put the correct URL in source_url field
       
       c) If BOTH text and URL are wrong:
          - Use Google Search to find what's actually true
          - Provide corrected text with the correct source URL
       
       d) If it's a fake citation:
          - Use: "[CITATION REMOVED: Reference could not be verified]"
       
       - NEVER leave 'correction' null for HALLUCINATION status.
    
    7. For BROKEN_URL:
       - Use Google Search to find a working alternative URL with similar content
       - Set correction to include the working URL if found
    
    8. Always put the CORRECT/VERIFIED URL in source_url field
    9. Rate confidence from 0-100 based on source reliability
    
    {url_context}
    {url_content_context}
    
    OUTPUT FORMAT:
    Return a valid JSON object with the following structure:
    {{
      "claims": [
        {{
          "original_text": "The exact sentence from the input",
          "type": "FACT" | "CITATION" | "URL",
          "status": "VERIFIED" | "HALLUCINATION" | "SUSPICIOUS" | "OPINION" | "BROKEN_URL",
          "reasoning": "Detailed explanation of why this status was assigned, including what the URL actually contains if relevant",
          "correction": "The corrected statement with correct URL if applicable, or null if VERIFIED",
          "source_url": "The CORRECT URL that supports the verified/corrected information",
          "confidence_score": 0-100
        }}
      ]
    }}

    EXAMPLE:
    If input says "According to https://example.com, Python was created in 2020" but the URL actually says Python was created in 1991:
    {{
      "original_text": "According to https://example.com, Python was created in 2020",
      "type": "URL",
      "status": "HALLUCINATION",
      "reasoning": "The URL https://example.com actually states Python was created in 1991 by Guido van Rossum, not 2020 as claimed.",
      "correction": "According to https://example.com, Python was created in 1991 by Guido van Rossum.",
      "source_url": "https://example.com",
      "confidence_score": 95
    }}

    TEXT TO ANALYZE:
    {text_input}
    """

    # 3. Execute the Agent
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )
        
        # Manual Parsing
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        data = json.loads(text.strip())
        return VerificationReport(**data)
        
    except Exception as e:
        print(f"Agent Error: {e}")
        # Return empty report on failure
        return VerificationReport(claims=[])
    return response.parsed


# --- Standalone Test ---
if __name__ == "__main__":
    test_text = """
    Recent studies by Johnson et al. (2024) in the Journal of Advanced AI suggest that 
    neural networks consume 50% less energy when trained on quantum hardware. 
    This breakthrough was validated by Google DeepMind in their 2023 annual report. 
    Meanwhile, the moon is made of green cheese, a fact confirmed by NASA in 1969.
    The Transformer architecture was introduced by Vaswani et al. in 2017.
    For more info, visit https://www.google.com and https://this-url-does-not-exist-12345.com/fake-page
    """
    
    print("Testing VibeCheck Agent...")
    print("-" * 50)
    
    # Test URL validation separately
    print("\n🔗 Testing URL Validation:")
    urls = extract_urls(test_text)
    for url in urls:
        result = check_url_validity(url)
        status = "✅ Valid" if result["is_accessible"] else "❌ Broken"
        print(f"  {status}: {url}")
    print("-" * 50)
    
    try:
        report = verify_content(test_text)
        for claim in report.claims:
            status_emoji = "✅" if claim.status == "VERIFIED" else "❌" if claim.status in ["HALLUCINATION", "BROKEN_URL"] else "⚠️"
            print(f"{status_emoji} [{claim.status}] {claim.original_text[:60]}...")
            print(f"   Reasoning: {claim.reasoning}")
            if claim.correction:
                print(f"   Correction: {claim.correction}")
            print()
    except Exception as e:
        print(f"Error: {e}")


