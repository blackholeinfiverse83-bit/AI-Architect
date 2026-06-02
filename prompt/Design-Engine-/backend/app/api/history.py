from typing import Optional

from app.auth_mongodb import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter()


@router.get("/history/{spec_id}")
async def get_spec_history(
    spec_id: str,
    current_user: str = Depends(get_current_user),
    db=Depends(get_db),
    limit: Optional[int] = Query(50, description="Maximum number of iterations to return"),
):
    """Get complete history for a specific spec including iterations and evaluations"""

    # Get the spec
    spec = await db.specs.find_one({"_id": spec_id})
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")

    # Get iterations
    iterations = (
        await db.iterations.find({"spec_id": spec_id})
        .sort("created_at", -1)
        .limit(limit)
        .to_list(None)
    )

    # Get evaluations
    evaluations = (
        await db.evaluations.find({"spec_id": spec_id})
        .sort("created_at", -1)
        .limit(limit)
        .to_list(None)
    )

    return {
        "spec_id": spec_id,
        "spec": {
            "spec_id": spec.get("_id"),
            "user_id": spec.get("user_id"),
            "project_id": spec.get("project_id"),
            "prompt": spec.get("prompt"),
            "spec_json": spec.get("spec_json"),
            "version": spec.get("version"),
            "created_at": spec.get("created_at"),
            "updated_at": spec.get("updated_at"),
        },
        "iterations": [
            {
                "iter_id": iter.get("_id"),
                "query": iter.get("query"),
                "diff": iter.get("diff"),
                "spec_json": iter.get("spec_json"),
                "timestamp": iter.get("created_at"),
            }
            for iter in iterations
        ],
        "evaluations": [
            {
                "eval_id": eval.get("_id"),
                "user_id": eval.get("user_id"),
                "rating": eval.get("rating"),
                "notes": eval.get("notes"),
                "timestamp": eval.get("created_at"),
            }
            for eval in evaluations
        ],
        "total_iterations": len(iterations),
        "total_evaluations": len(evaluations),
    }


@router.get("/history")
async def get_user_history(
    current_user: str = Depends(get_current_user),
    db=Depends(get_db),
    limit: Optional[int] = Query(20, description="Maximum number of specs to return"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
):
    """Get complete history with data integrity for all specs"""

    search_filter = {"user_id": current_user}
    if project_id:
        search_filter["project_id"] = project_id

    specs = await db.specs.find(search_filter).sort("updated_at", -1).limit(limit).to_list(None)

    specs_data = []
    for spec in specs:
        spec_id = spec.get("_id")
        # Get counts for related data
        iterations_count = await db.iterations.count_documents({"spec_id": spec_id})
        evaluations_count = await db.evaluations.count_documents({"spec_id": spec_id})
        compliance_count = await db.compliance_checks.count_documents({"spec_id": spec_id})

        specs_data.append(
            {
                "spec_id": spec_id,
                "project_id": spec.get("project_id"),
                "prompt": spec.get("prompt"),
                "city": spec.get("city"),
                "design_type": spec.get("design_type"),
                "version": spec.get("version"),
                "status": spec.get("status"),
                "compliance_status": spec.get("compliance_status"),
                "estimated_cost": spec.get("estimated_cost"),
                "currency": spec.get("currency", "INR"),
                "preview_url": spec.get("preview_url"),
                "geometry_url": spec.get("geometry_url"),
                "created_at": spec.get("created_at").isoformat() if spec.get("created_at") else None,
                "updated_at": spec.get("updated_at").isoformat() if spec.get("updated_at") else None,
                "data_integrity": {
                    "has_spec_json": spec.get("spec_json") is not None,
                    "has_preview": spec.get("preview_url") is not None,
                    "has_geometry": spec.get("geometry_url") is not None,
                    "iterations_count": iterations_count,
                    "evaluations_count": evaluations_count,
                    "compliance_count": compliance_count,
                    "auditable": True,
                },
            }
        )

    return {
        "user_id": current_user,
        "specs": specs_data,
        "total_specs": len(specs),
        "data_integrity_summary": {
            "total_specs": len(specs),
            "specs_with_json": sum(1 for s in specs if s.get("spec_json") is not None),
            "specs_with_preview": sum(1 for s in specs if s.get("preview_url") is not None),
            "specs_with_geometry": sum(1 for s in specs if s.get("geometry_url") is not None),
            "all_auditable": True,
        },
    }
