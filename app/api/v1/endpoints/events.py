from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_operator
from app.schemas.event import SupplyEventCreate, SupplyEventFilter, SupplyEventResponse
from app.services.event_service import create_event, get_event_by_id, get_events

router = APIRouter()


@router.post("", response_model=SupplyEventResponse, status_code=201)
def ingest_event(
    data: SupplyEventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_operator),
):
    """
    Ingest a new supply chain event.
    Webhook delivery happens asynchronously in the background.
    """
    try:
        event = create_event(db, data, background_tasks)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[SupplyEventResponse])
def list_events(
    supplier_id: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = SupplyEventFilter(
        supplier_id=supplier_id,
        event_type=event_type,
        status=status,
        limit=limit,
        offset=offset,
    )
    return get_events(db, filters)


@router.get("/{event_id}", response_model=SupplyEventResponse)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
