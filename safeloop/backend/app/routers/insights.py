from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.insights import analytics as analytics_service, user_insights
from ..utils.security import current_user, require_role


router = APIRouter(prefix="/api", tags=["insights"])


@router.get("/insights")
def insights(user=Depends(current_user), db: Session = Depends(get_db)):
    return user_insights(db, user.id)


@router.get("/analytics")
def analytics(user=Depends(require_role("admin", "responder")), db: Session = Depends(get_db)):
    data = analytics_service(db)
    from ..models import User
    data["total_users"] = db.query(User).count()
    return data
