from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, Query, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import SessionLocal, engine
from app.auth import create_access_token, verify_password, get_current_admin, hash_password

# ------------------- Database Setup ------------------- #
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- FastAPI Setup ------------------- #
tags_metadata = [
    {"name": "Auth"},
    {"name": "User"},
    {"name": "Admin"},
    {"name": "Frontend"},
]

app = FastAPI(title="AI Tool Finder Backend", openapi_tags=tags_metadata)

# ------------------- CORS & Static ------------------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ------------------- Frontend ------------------- #
@app.get("/", tags=["Frontend"])
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ------------------- Admin APIs ------------------- #
@app.post("/admin/register", tags=["Auth"])
def register_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    """Register first admin or new admin if allowed"""
    existing = db.query(models.Admin).filter(models.Admin.email == admin.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")

    hashed_pwd = hash_password(admin.password)
    new_admin = models.Admin(email=admin.email, password_hash=hashed_pwd)
    db.add(new_admin)
    db.commit()
    return {"message": "Admin created successfully"}

@app.post("/admin/login", tags=["Auth"])
def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    if not admin or not verify_password(form_data.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(data={"sub": admin.email, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/admin/tools", response_model=schemas.ToolResponse, tags=["Admin"])
def add_tool(tool: schemas.ToolCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    new_tool = models.Tool(**tool.dict())
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)
    return new_tool

@app.put("/admin/tools/{tool_id}", tags=["Admin"])
def update_tool(tool_id: int, tool: schemas.ToolCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    db_tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    for key, value in tool.dict().items():
        setattr(db_tool, key, value)

    db.commit()
    return {"message": "Tool updated successfully"}

@app.delete("/admin/tools/{tool_id}", tags=["Admin"])
def delete_tool(tool_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    db.delete(tool)
    db.commit()
    return {"message": "Tool deleted successfully"}

@app.put("/admin/reviews/{review_id}/approve", tags=["Admin"])
def approve_review(review_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.status = "Approved"
    db.commit()

    approved_reviews = db.query(models.Review).filter(
        models.Review.tool_id == review.tool_id,
        models.Review.status == "Approved"
    ).all()

    avg_rating = sum(r.rating for r in approved_reviews) / len(approved_reviews)
    tool = db.query(models.Tool).filter(models.Tool.id == review.tool_id).first()
    tool.avg_rating = round(avg_rating, 2)
    db.commit()

    return {"message": "Review approved and rating updated"}

@app.put("/admin/reviews/{review_id}/reject", tags=["Admin"])
def reject_review(review_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.status = "Rejected"
    db.commit()
    return {"message": "Review rejected"}

@app.get("/admin/reviews", response_model=List[schemas.ReviewResponse], tags=["Admin"])
def get_all_reviews(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(models.Review).all()

# ------------------- User APIs ------------------- #
@app.get("/tools", response_model=List[schemas.ToolResponse], tags=["User"])
def get_tools(category: str = None, pricing: str = None, rating: float = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Tool)
    if category:
        query = query.filter(models.Tool.category == category)
    if pricing:
        query = query.filter(models.Tool.pricing == pricing)
    if rating:
        query = query.filter(models.Tool.avg_rating >= rating)
    return query.all()

@app.post("/review", tags=["User"])
def submit_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    tool = db.query(models.Tool).filter(models.Tool.id == review.tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    new_review = models.Review(**review.dict())
    db.add(new_review)
    db.commit()
    return {"message": "Review submitted and waiting for admin approval"}
