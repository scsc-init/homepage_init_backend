from datetime import datetime, timezone     
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.db import SessionDep, SessionLocal
from src.model import KeyValue, SCSCGlobalStatus, UserRole       


@lru_cache
def get_user_role_level(role_name: str) -> int:
    """
    Retrieves the numerical level for a given role name from the database.
    Raises ValueError if the role name does not exist.

    Args:
        role_name (str): The name of the role to look up.

    Returns:
        int: The level associated with the role.

    Raises:
        HTTPException: 400 if a role with the given name is not found in the database.
    """
    session = None
    try:
        session = SessionLocal()  # Get a new session
        user_role = session.exec(select(UserRole).where(UserRole.name == role_name)).first()
        if not user_role:
            raise HTTPException(400, f"Role '{role_name}' not found in the database.")
        return user_role.level

    finally:
        if session: session.close()

def get_kv_entry(session: SessionDep, key: str) -> KeyValue:                                                                                                                       
    kv_entry = session.get(KeyValue, key)                                                                             
    if kv_entry is None:                                                                                              
        raise HTTPException(503, detail=f"config entry '{key}' not configured")                                           
    return kv_entry                                                                                                   
                                                                                                                          
                                                                                                                        
                                                                                                                        
def update_kv_entry(                                                                                                  
    session: SessionDep,                                                                                                  
    *,                                                                                                                    
    key: str,                                                                                                             
    value: str,                                                                                                           
    actor_role: int,                                                                                                      
    min_role: int | None = None,                                                                                          
) -> KeyValue:                                                                                                         
    kv_entry = get_kv_entry(session, key)                                                                         

    required_role = kv_entry.writing_permission_level                                                                                        
    if actor_role < required_role:                                                                    
        raise HTTPException(403, detail="insufficient permission")                                                        
                                                                                                                        
    kv_entry.value = value                                                                                            
    kv_entry.updated_at = datetime.now(timezone.utc)                                                                  
                                                                                                                        
    session.add(kv_entry)                                                                                             
    session.commit()                                                                                                      
    session.refresh(kv_entry)                                                                                         
    return kv_entry                                                                                                   
                                    
    
def _get_scsc_global_status(session: SessionDep) -> SCSCGlobalStatus:
    status = session.get(SCSCGlobalStatus, 1)
    if status is None: raise HTTPException(503, detail="scsc global status does not exist")
    return status


SCSCGlobalStatusDep = Annotated[SCSCGlobalStatus, Depends(_get_scsc_global_status)]
