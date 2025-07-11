from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, SessionLocal
from .auth import router as auth_router
from .websocket import router as ws_router
from .ai import router as ai_router
from .models import Document, DocumentVersion, User
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path


SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth_router)
app.include_router(ws_router)
app.include_router(ai_router)

# Allow local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "frontend" / "templates")

# Routes to serve pages
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# --- New routes ---
@app.post("/create_doc")
def create_doc(title: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = Document(title=title, owner_id=user.id)
    db.add(doc)
    db.commit()
    return {"message": "created"}

@app.get("/allDocs")
def list_docs(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [{"id": d.id, "title": d.title} for d in docs]


@app.get("/get_doc/{doc_id}")
def get_doc(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "title": doc.title, "content": doc.current_content}



class ContentSchema(BaseModel):
    content: str

@app.post("/save_version/{doc_id}")
def save_version(doc_id: int, data: ContentSchema, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.current_content = data.content
    version = DocumentVersion(doc_id=doc_id, content=data.content)
    db.add(version)
    db.commit()
    return {"message": "saved"}

@app.get("/versions/{doc_id}")
def versions(doc_id: int, db: Session = Depends(get_db)):
    vs = db.query(DocumentVersion).filter(DocumentVersion.doc_id == doc_id).all()
    return [{"id": v.id, "timestamp": v.timestamp.isoformat()} for v in vs]
