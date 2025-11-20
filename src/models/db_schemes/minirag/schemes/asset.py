from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Index, Integer, String, DateTime , ForeignKey , func
from sqlalchemy.dialects.postgresql import UUID , JSONB
from sqlalchemy.orm import relationship
import uuid


class Asset(SQLAlchemyBase):
    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    asset_type = Column(String , nullable=False)
    asset_name = Column(String , nullable=False) 
    asset_size = Column(Integer , nullable=False)
    #metadata : thwo types of json in sqlalchemy : JSON : slow in reading and fast in writing and JSONB (binary json) fast in reading and slow in writing
    asset_config = Column(JSONB , nullable=True)
    
    created_at = Column(DateTime(timezone=True) , server_default=func.now() , nullable=False)
    updated_at = Column(DateTime(timezone=True) , server_default=func.now() , onupdate=func.now() , nullable=True)
    
    asset_project_id = Column(Integer , ForeignKey("projects.project_id") , nullable=False)
    project = relationship("Project", back_populates="assets")
    chunks = relationship("DataChunk", back_populates="asset") 
    # we should do indexing on asset_project_id for faster querying 
    # sqlalchemy automatically creates index for primary key and unique = True columns
    __table__args__ = (
        Index("idx_asset_project_id", "asset_project_id"),
        Index("idx_asset_type", "asset_type")
    )