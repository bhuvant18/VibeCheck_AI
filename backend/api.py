"""
VibeCheck API - FastAPI backend server
Provides REST endpoints for text verification using Gemini and Semantic Scholar
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import verify_content, verify_paper, ClaimAnalysis, VerificationReport

# --- FastAPI App Setup ---
app = FastAPI(
    title="VibeCheck API",
    description="AI Hallucination Detection API powered by Gemini 2.0 & Semantic Scholar",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---
class VerifyRequest(BaseModel):
    """Request body for text verification"""
    text: str = Field(..., description="The text to verify for hallucinations", min_length=1)
    api_key: Optional[str] = Field(None, description="Google Gemini API key (optional, uses server key if not provided)")


class CitationCheckRequest(BaseModel):
    """Request body for direct citation verification"""
    title: str = Field(..., description="Paper title to search for")
    author: Optional[str] = Field(None, description="Author last name (optional)")


class CitationCheckResponse(BaseModel):
    """Response for citation verification"""
    found: bool
    title: Optional[str] = None
    year: Optional[int] = None
    url: Optional[str] = None
    authors: Optional[List[str]] = None
    author_match: Optional[bool] = None
    citation_count: Optional[int] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    model: str


# --- API Endpoints ---
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model="gemini-2.0-flash-exp"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model="gemini-2.0-flash-exp"
    )


@app.post("/api/verify", response_model=VerificationReport)
async def verify_text(request: VerifyRequest):
    """
    Main verification endpoint.
    
    Takes text input and returns a detailed verification report with:
    - Claims broken down into individual statements
    - Status for each claim (VERIFIED, HALLUCINATION, SUSPICIOUS, OPINION)
    - Corrections for false claims
    - Source URLs for verified claims
    """
    try:
        report = verify_content(request.text, api_key=request.api_key)
        
        if not report:
            raise HTTPException(
                status_code=500, 
                detail="Model failed to generate structured report."
            )
        
        return report
        
    except Exception as e:
        print(f"Verification Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Verification failed: {str(e)}"
        )


@app.post("/api/check-citation", response_model=CitationCheckResponse)
async def check_citation(request: CitationCheckRequest):
    """
    Direct citation verification endpoint.
    
    Checks if a specific paper exists in Semantic Scholar database.
    Useful for quick citation validation without full text analysis.
    """
    try:
        result = verify_paper(request.title, request.author)
        return CitationCheckResponse(**result)
        
    except Exception as e:
        print(f"Citation Check Error: {str(e)}")
        return CitationCheckResponse(found=False, error=str(e))


@app.post("/api/batch-verify")
async def batch_verify(requests: List[VerifyRequest]):
    """
    Batch verification endpoint.
    
    Verifies multiple texts in parallel.
    Limited to 5 texts per request to prevent timeout.
    """
    if len(requests) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 texts per batch request"
        )
    
    results = []
    for req in requests:
        try:
            report = verify_content(req.text)
            results.append({"success": True, "report": report})
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    
    return {"results": results}


# --- Run Server ---
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting VibeCheck API on http://{host}:{port}")
    print(f"📚 API Docs available at http://{host}:{port}/docs")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
