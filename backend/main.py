from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uuid
import cv2
from sqlalchemy.future import select

from utils.utils import load_image, remove_white_borders, resize_to_target, verify_class, extract_fields
from classifier import get_closest_class, ratio_config
from database.models import Document
from database.schema import SaveRequest
from database.database import AsyncSessionLocal, init_db
from const import FRONTEND_SERVER, APP_TITLE, BACKEND_SERVER, STATIC_DIR, DOCUMENT_TYPE_ERROR, \
DOCUMENT_TYPE, DOCUMENT_CONTENT, ORIGINAL_URL, PROCESSED_IMAGE_URL, DOCUMENT_UPDATED, DOCUMENT_SAVED,\
FIRST_NAME, LAST_NAME, FULL_NAME

app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_SERVER],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static folder for storing preview images
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
async def startup_event():
    await init_db()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def save_image(image, prefix: str) -> str:
    filename = f"{prefix}_{uuid.uuid4().hex[:8]}.jpg"
    path = os.path.join(STATIC_DIR, filename)
    cv2.imwrite(path, image)
    return f"{BACKEND_SERVER}/static/{filename}"

@app.post("/classify_and_extract")
async def classify_and_extract(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    content = await file.read()

    image = load_image(content, ext)
    original_image = image.copy()

    # Save original image preview
    original_url = save_image(original_image, "original")

    image = remove_white_borders(image)
    processed_url = save_image(image, "processed")

    # Classify and resize
    h, w = image.shape[:2]
    doc_type, ratio_str = get_closest_class(w, h)
    image = resize_to_target(image, ratio_config[doc_type])

    if not verify_class(image, doc_type):
        return JSONResponse(status_code=400, content={"error": DOCUMENT_TYPE_ERROR})

    data = extract_fields(image, doc_type)

    full_name = " ".join(filter(None, [data.pop(FIRST_NAME, ""), data.pop(LAST_NAME, "")])).strip()
    if full_name:
        data[FULL_NAME] = full_name

    return {
        DOCUMENT_TYPE: doc_type,
        DOCUMENT_CONTENT: data,
        ORIGINAL_URL: original_url,
        PROCESSED_IMAGE_URL: processed_url
    }

@app.post("/save")
async def save_document(req: SaveRequest, db=Depends(get_db)):
    if req.id:
        result = await db.execute(select(Document).where(Document.id == req.id))
        doc = result.scalar_one_or_none()
        if doc:
            for field, value in req.dict(exclude_unset=True).items():
                setattr(doc, field, value)
            await db.commit()
            return {"message": DOCUMENT_UPDATED, "id": doc.id}

    new_doc = Document(**req.dict(exclude={"id"}))
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return {"message": DOCUMENT_SAVED, "id": new_doc.id}

@app.get("/recent")
async def recent_documents(db=Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.id.desc()).limit(10))
    return result.scalars().all()

@app.get("/debug_all")
async def debug_all(db=Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.id.desc()))
    return result.scalars().all()