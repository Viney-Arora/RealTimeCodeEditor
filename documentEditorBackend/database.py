from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL ="postgresql://postgres:Viney%40intern4321%40@localhost:5500/documentEditorDb"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit = False, autoflush=False)
Base = declarative_base() 