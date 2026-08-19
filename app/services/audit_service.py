from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.core.security import hash_ip

def log_audit_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[int] = None,
    client_ip: Optional[str] = None
):
    try:
        ip_hash = hash_ip(client_ip or "127.0.0.1")
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            ip_hash=ip_hash
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:
        print(f"Audit log warning: {e}")
