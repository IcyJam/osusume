import enum

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Date,
    TIMESTAMP,
    ForeignKey,
    Table,
    Enum,
    func, UniqueConstraint, Float, CheckConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class MediaType(enum.Enum):
    TV = "TV"
    MOVIE = "MOVIE"
    OVA = "OVA"
    ONA = "ONA"
    SPECIAL = "SPECIAL"
    MANGA = "manga"
    NOVEL = "NOVEL"
    ARTBOOK = "ARTBOOK"
    OTHER = "OTHER"


class Status(enum.Enum):
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    FINISHED = "FINISHED"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


# Association tables for many-to-many relations
media_content_descriptors = Table(
    "media_content_descriptors",
    Base.metadata,
    Column("media_id", Integer, ForeignKey("media.media_id", ondelete="CASCADE"), primary_key=True),
    Column(
        "content_descriptor_id",
        Integer,
        ForeignKey("content_descriptors.content_descriptor_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Media(Base):
    __tablename__ = "media"
    __table_args__ = (
        UniqueConstraint("title", "type", "external_url", name="uq_media_title_type_url"),
        CheckConstraint('score >= 0 AND score <= 10', name='score_range'),
    )

    media_id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(MediaType, name="media_type"), nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    external_url = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    status = Column(Enum(Status, name="status"), nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    content_descriptors = relationship("ContentDescriptor", secondary=media_content_descriptors, back_populates="media")

    def __repr__(self):
        return f"<Media(id={self.media_id}, title={self.title!r}, type={self.type}, status={self.status})>"


class ContentDescriptor(Base):
    __tablename__ = "content_descriptors"

    content_descriptor_id = Column(Integer, primary_key=True, autoincrement=True)
    content_descriptor = Column(Text, nullable=False, unique=True)

    media = relationship(
        "Media", secondary=media_content_descriptors, back_populates="content_descriptors"
    )

    def __repr__(self):
        return f"<ContentDescriptor(id={self.content_descriptor_id}, descriptor={self.content_descriptor!r})>"
