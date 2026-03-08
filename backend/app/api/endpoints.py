from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from typing import List
from ..models.schemas import VisionRequest, ChatRequest, RiskAnalysisRequest, CalendarLinkRequest, IcsContentRequest, HistoryResponse, UserUpdate, User
from ..dependencies import get_ai_client, get_logic_engine, get_cache_manager, get_local_processor
from ..core.ai_client import LensAI
from ..core.logic_engine import LogicEngine
from ..core.cache_manager import AsyncCacheManager
from ..core.local_processor import LocalProcessor
from ..db import crud, models, database
from ..core import report_generator
from ..api import auth
from sqlalchemy.orm import Session
import time
import asyncio
import json

router = APIRouter()

# --- Auth Dependencies ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    from jose import jwt, JWTError
    from ..core import security
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# --- User Profile ---

@router.put("/user/profile", response_model=User)
async def update_profile(profile: UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_user = crud.update_user_profile(db, current_user.id, profile)
    return updated_user

@router.get("/user/profile", response_model=User)
async def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- Vision & Core Logic ---

@router.post("/vision/analyze")
async def analyze_vision(
    request: VisionRequest, 
    ai_client: LensAI = Depends(get_ai_client),
    cache_manager: AsyncCacheManager = Depends(get_cache_manager),
    local_processor: LocalProcessor = Depends(get_local_processor),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        start_total = time.time()
        perf_report = {}

        # Construct User Context for AI
        user_context = {
            "medical_history": current_user.medical_history,
            "preferences": current_user.preferences
        }

        # 1. Check Cache (Cache key should ideally include user context if personalization affects result, 
        # but for now we keep image-based cache for raw analysis and might re-process context. 
        # However, to keep it simple, we skip cache if personalization is critical or we rely on AI to include it in response.
        # Let's assume the AI response is personalized, so cache key should include user_id or context hash.
        # For this iteration, we'll bypass cache if we want strictly personalized results, or we assume cache is shared generic analysis.
        # BETTER: Let's fetch cached generic result and augment it? No, AI prompt includes context.
        # So we must include context in cache key OR just cache per image+user combination.
        # Let's simple append user_id to image_base64 for cache key to ensure personalization privacy and correctness.
        cache_key = f"{current_user.id}:{request.image_base64}"
        
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            perf_report['source'] = 'cache'
            perf_report['total_latency'] = time.time() - start_total
            cached_result['perf_report'] = perf_report
            
            # Save to History
            crud.create_user_history(db, models.History(
                category=cached_result.get('category', 'unknown'),
                title=cached_result.get('title', 'Unknown'),
                summary=cached_result.get('description', '')[:100]
            ), current_user.id)
            
            return cached_result

        # 2. Local Preprocessing (Async)
        local_task = asyncio.create_task(local_processor.preprocess_and_analyze(request.image_base64))
        
        # 3. Cloud Analysis (Async) - Pass User Context
        cloud_start = time.time()
        cloud_task = asyncio.create_task(ai_client.get_vision_response(request.image_base64, user_context=user_context))
        
        # Wait for both
        local_result, cloud_result = await asyncio.gather(local_task, cloud_task)
        
        if not cloud_result:
             raise HTTPException(status_code=500, detail="Failed to analyze image")

        # 4. Generate Performance Report
        perf_report['source'] = 'cloud'
        perf_report['local_preprocessing_latency'] = local_result.get('local_latency', 0)
        perf_report['cloud_inference_latency'] = time.time() - cloud_start
        perf_report['total_latency'] = time.time() - start_total
        perf_report['local_metrics'] = {k: v for k, v in local_result.items() if k != 'local_latency'}

        # Attach report to result
        cloud_result['perf_report'] = perf_report

        # 5. Cache Result (Personalized)
        await cache_manager.set(cache_key, cloud_result)

        # 6. Save to DB History
        crud.create_user_history(db, HistoryResponse(
            id=0, # Placeholder
            timestamp=time.time(), # Placeholder
            category=cloud_result.get('category', 'unknown'),
            title=cloud_result.get('title', 'Unknown'),
            summary=cloud_result.get('description', '')[:100],
            owner_id=current_user.id
        ), current_user.id)

        return cloud_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/completions")
async def chat_completions(request: ChatRequest, ai_client: LensAI = Depends(get_ai_client), current_user: models.User = Depends(get_current_user)):
    try:
        messages = [msg.dict() for msg in request.messages]
        result = await ai_client.get_chat_response(messages)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logic/risk")
async def check_risk(request: RiskAnalysisRequest, logic_engine: LogicEngine = Depends(get_logic_engine), current_user: models.User = Depends(get_current_user)):
    try:
        # We could also enhance this with user medical history if we parsed it into structured allergens
        # For now, it uses the standard LogicEngine list
        risks = logic_engine.get_risk_details(request.ingredients)
        return {"risks": risks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logic/calendar/link")
async def calendar_link(request: CalendarLinkRequest, logic_engine: LogicEngine = Depends(get_logic_engine), current_user: models.User = Depends(get_current_user)):
    try:
        link = logic_engine.parse_calendar_data(request.event_name, request.time_str, request.location)
        return {"link": link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logic/calendar/ics")
async def calendar_ics(request: IcsContentRequest, logic_engine: LogicEngine = Depends(get_logic_engine), current_user: models.User = Depends(get_current_user)):
    try:
        ics_content = logic_engine.get_ics_content(request.event_name, request.time_str, request.location)
        if ics_content:
            return {"ics_content": ics_content.decode('utf-8')} 
        return {"ics_content": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- History & Reports ---

@router.get("/history", response_model=List[HistoryResponse])
async def get_history(
    skip: int = 0, 
    limit: int = 10, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_history(db, current_user.id, skip, limit)

@router.get("/report/pdf")
async def get_pdf_report(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = crud.get_history(db, current_user.id, limit=100)
    pdf_buffer = report_generator.generate_pdf_report(history, current_user.username)
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=report_{current_user.username}.pdf"}
    )

@router.get("/report/excel")
async def get_excel_report(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = crud.get_history(db, current_user.id, limit=100)
    excel_buffer = report_generator.generate_excel_report(history)
    return StreamingResponse(
        excel_buffer, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        headers={"Content-Disposition": f"attachment; filename=report_{current_user.username}.xlsx"}
    )
