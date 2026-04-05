from fastapi import APIRouter, HTTPException
from app.models.render_settings import RenderSettings
from app.models.render_plan import RenderPlan
from app.services.planning_service import calculate_render_plan

router = APIRouter(prefix="/api/render", tags=["render"])

@router.post("/plan", response_model=RenderPlan)
async def generate_render_plan(settings: RenderSettings):
    """
    Validates render settings and returns a computed render plan.
    Does not start actual rendering.
    """
    try:
        plan = calculate_render_plan(settings)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate render plan: {str(e)}")
