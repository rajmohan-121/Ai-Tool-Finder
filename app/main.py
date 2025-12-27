from fastapi.security import OAuth2PasswordRequestForm
from app.auth import create_access_token, verify_password, get_current_admin, hash_password
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from typing import List
from app.database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Auth"
    },
    {
        "name": "User"
    },
    {
        "name": "Admin"
    }
]


app = FastAPI(
    title="AI Tool Finder Backend",
    openapi_tags=tags_metadata
)


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- ADMIN APIs ---------------- #

@app.post("/admin/register", tags=["Auth"])
def register_admin(admin: schemas.AdminCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)):
    existing = db.query(models.Admin).filter(models.Admin.email == admin.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")

    hashed_pwd = hash_password(admin.password)

    new_admin = models.Admin(
        email=admin.email,
        password_hash=hashed_pwd
    )

    db.add(new_admin)
    db.commit()
    return {"message": "Admin created successfully"}

@app.post("/admin/login", tags=["Auth"])
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(
        models.Admin.email == form_data.username
    ).first()

    if not admin or not verify_password(
        form_data.password, admin.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": admin.email, "role": "admin"}
    )

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
        return {"error": "Tool not found"}

    for key, value in tool.dict().items():
        setattr(db_tool, key, value)

    db.commit()
    return {"message": "Tool updated successfully"}


@app.delete("/admin/tools/{tool_id}", tags=["Admin"])
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
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
        return {"error": "Review not found"}

    review.status = "Rejected"
    db.commit()
    return {"message": "Review rejected"}


# ---------------- USER APIs ---------------- #

@app.get("/tools", response_model=List[schemas.ToolResponse], tags=["User"])
def get_tools(
    category: str = None,
    pricing: str = None,
    rating: float = Query(None),
    db: Session = Depends(get_db)
):
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

@app.get("/admin/reviews", response_model=List[schemas.ReviewResponse], tags=["User"])
def get_all_reviews(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    reviews = db.query(models.Review).all()
    return reviews

