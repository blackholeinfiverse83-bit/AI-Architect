import logging
from datetime import datetime, timezone
from typing import Optional

from app.auth_mongodb import get_current_user
from app.database_mongodb import get_database
from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/history/{spec_id}")
async def get_spec_history(
    spec_id: str,
    current_user: str = Depends(get_current_user),
    limit: Optional[int] = Query(50, description="Maximum number of items"),
):
    """Get complete history for a specific spec from MongoDB Atlas"""
    try:
        db = get_database()
        spec = await db.specs.find_one({"$or": [{"_id": spec_id}, {"spec_id": spec_id}]})
        if not spec:
            raise HTTPException(status_code=404, detail="Spec not found")

        spec["_id"] = str(spec.get("_id", spec_id))

        iterations = await db.iterations.find({"spec_id": spec_id}).limit(limit or 50).to_list(length=limit or 50)
        evaluations = await db.evaluations.find({"spec_id": spec_id}).limit(limit or 50).to_list(length=limit or 50)

        for item in iterations:
            item["_id"] = str(item["_id"])
        for item in evaluations:
            item["_id"] = str(item["_id"])

        return {
            "spec_id": spec_id,
            "spec": spec,
            "iterations": iterations,
            "evaluations": evaluations,
            "total_iterations": len(iterations),
            "total_evaluations": len(evaluations),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HISTORY] Error fetching spec history {spec_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_user_history(
    current_user: str = Depends(get_current_user),
    limit: Optional[int] = Query(20, description="Maximum number of specs to return"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    all_users: bool = Query(False, description="Whether to include designs from all users"),
):
    """Get complete history for user specs from MongoDB Atlas"""
    try:
        db = get_database()
        filter_doc = {}
        if not all_users:
            filter_doc["$or"] = [
                {"user_id": current_user},
                {"user_id": f"user_{current_user}"},
                {"user_id": {"$regex": current_user, "$options": "i"}},
            ]
        if project_id:
            filter_doc["project_id"] = project_id

        cursor = db.specs.find(filter_doc).sort("created_at", -1).limit(limit or 20)
        specs_raw = await cursor.to_list(length=limit or 20)


        specs_data = []
        for s in specs_raw:
            sid = str(s.get("spec_id") or s.get("_id"))
            specs_data.append(
                {
                    "spec_id": sid,
                    "project_id": s.get("project_id"),
                    "prompt": s.get("prompt", ""),
                    "city": s.get("city", "Mumbai"),
                    "design_type": s.get("design_type", "apartment"),
                    "version": s.get("version", 1),
                    "status": s.get("status", "completed"),
                    "compliance_status": s.get("compliance_status", "passed"),
                    "estimated_cost": s.get("estimated_cost", 0),
                    "currency": s.get("currency", "INR"),
                    "preview_url": s.get("preview_url"),
                    "geometry_url": s.get("glb_url") or s.get("preview_url"),
                    "created_at": str(s.get("created_at", "")),
                    "updated_at": str(s.get("updated_at", "")),
                    "spec_json": s.get("spec_json", {}),
                    "data_integrity": {
                        "has_spec_json": s.get("spec_json") is not None,
                        "has_preview": s.get("preview_url") is not None,
                        "has_geometry": (s.get("glb_url") or s.get("preview_url")) is not None,
                        "auditable": True,
                    },
                }
            )

        return {
            "user_id": current_user,
            "specs": specs_data,
            "total_specs": len(specs_data),
            "data_integrity_summary": {
                "total_specs": len(specs_data),
                "specs_with_json": sum(1 for s in specs_data if s["data_integrity"]["has_spec_json"]),
                "specs_with_preview": sum(1 for s in specs_data if s["data_integrity"]["has_preview"]),
                "specs_with_geometry": sum(1 for s in specs_data if s["data_integrity"]["has_geometry"]),
                "all_auditable": True,
            },
        }
    except Exception as e:
        logger.error(f"[HISTORY] Error fetching user history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
