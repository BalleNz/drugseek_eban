from fastapi import APIRouter, Depends, HTTPException

from schemas.drug import Drug

drug_router = APIRouter(prefix="/drugs", tags=["Drugs"])

@drug_router.get("/", response_model=Drug)
async def get_drug():
