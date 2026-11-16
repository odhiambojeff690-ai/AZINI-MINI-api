from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Azin mini API")


class MemberCreate(BaseModel):
    name: str
    email: str


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    balance: float


@app.post("/members", response_model=MemberOut)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    db_member = models.Member(name=member.name, email=member.email)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@app.get("/members/{member_id}", response_model=MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@app.post("/members/{member_id}/deposit")
def deposit(member_id: int, amount: float, db: Session = Depends(get_db)):
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    member.balance += amount
    db.commit()
    db.refresh(member)
    return {"message": f"Deposited {amount}. New balance: {member.balance}"}