#!/usr/bin/env python3

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for many-to-many relationships
regulation_reference = Table(
    'regulation_reference',
    Base.metadata,
    Column('source_id', Integer, ForeignKey('regulation.id'), primary_key=True),
    Column('target_id', Integer, ForeignKey('regulation.id'), primary_key=True)
)

class Agency(Base):
    """Agency model representing a regulatory agency."""
    __tablename__ = "agency"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(255), nullable=True)
    
    # Relationships
    titles = relationship("Title", back_populates="agency")
    regulations = relationship("Regulation", back_populates="agency")
    
    def __repr__(self):
        return f"<Agency {self.name}>"

class Title(Base):
    """Title model representing a CFR title."""
    __tablename__ = "title"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    agency_id = Column(Integer, ForeignKey("agency.id"))
    
    # Additional metadata
    reserved = Column(Boolean, default=False)
    full_name = Column(String(255), nullable=True)  # Full title name with number
    description = Column(Text, nullable=True)  # Description or summary
    up_to_date_as_of = Column(DateTime, nullable=True)
    latest_amended_on = Column(DateTime, nullable=True)
    latest_issue_date = Column(DateTime, nullable=True)
    source_url = Column(String(255), nullable=True)  # URL to source (eCFR website)
    
    # Relationships
    agency = relationship("Agency", back_populates="titles")
    regulations = relationship("Regulation", back_populates="title")
    chapters = relationship("Chapter", back_populates="title", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Title {self.number}: {self.name}>"

class Regulation(Base):
    """Regulation model representing a specific regulation."""
    __tablename__ = "regulation"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), unique=True, index=True)
    title_id = Column(Integer, ForeignKey("title.id"))
    agency_id = Column(Integer, ForeignKey("agency.id"))
    label = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    html_url = Column(String(255), nullable=True)
    
    # Content
    html_content = Column(Text, nullable=True)
    text_content = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    title = relationship("Title", back_populates="regulations")
    agency = relationship("Agency", back_populates="regulations")
    metrics = relationship("RegulationMetrics", back_populates="regulation", uselist=False, foreign_keys="[RegulationMetrics.regulation_id]")
    
    # Many-to-many self-referential relationship for references
    references = relationship(
        "Regulation", 
        secondary=regulation_reference,
        primaryjoin=id==regulation_reference.c.source_id,
        secondaryjoin=id==regulation_reference.c.target_id,
        backref="referenced_by"
    )
    
    def __repr__(self):
        return f"<Regulation {self.identifier}: {self.name}>"

class Chapter(Base):
    """Chapter model representing a chapter within a title."""
    __tablename__ = "chapter"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(10), nullable=False)  # Roman or Arabic numerals
    name = Column(String(255), nullable=False)
    title_id = Column(Integer, ForeignKey("title.id"))
    
    # Additional metadata
    identifier = Column(String(50), nullable=True)  # Full identifier (e.g., "Chapter I")
    description = Column(Text, nullable=True)
    agency_name = Column(String(255), nullable=True)  # Agency name if different from title
    
    # Relationships
    title = relationship("Title", back_populates="chapters")
    subchapters = relationship("Subchapter", back_populates="chapter", cascade="all, delete-orphan")
    parts = relationship("Part", back_populates="chapter")
    
    def __repr__(self):
        return f"<Chapter {self.number}: {self.name}>"

class Subchapter(Base):
    """Subchapter model representing a subchapter within a chapter."""
    __tablename__ = "subchapter"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(50), nullable=False)  # Like "A", "B", etc.
    name = Column(String(255), nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapter.id"))
    
    # Additional metadata
    description = Column(Text, nullable=True)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="subchapters")
    parts = relationship("Part", back_populates="subchapter")
    
    def __repr__(self):
        return f"<Subchapter {self.identifier}: {self.name}>"

class Part(Base):
    """Part model representing a part within a title, chapter, or subchapter."""
    __tablename__ = "part"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    title_id = Column(Integer, ForeignKey("title.id"))
    chapter_id = Column(Integer, ForeignKey("chapter.id"), nullable=True)
    subchapter_id = Column(Integer, ForeignKey("subchapter.id"), nullable=True)
    
    # Additional metadata
    full_identifier = Column(String(50), nullable=True)  # Like "Part 1"
    description = Column(Text, nullable=True)
    authority_note = Column(Text, nullable=True)  # Legal authority
    source_note = Column(Text, nullable=True)  # Source information
    
    # Relationships
    title = relationship("Title")
    chapter = relationship("Chapter", back_populates="parts")
    subchapter = relationship("Subchapter", back_populates="parts")
    subparts = relationship("Subpart", back_populates="part", cascade="all, delete-orphan")
    sections = relationship("Section", back_populates="part")
    
    def __repr__(self):
        return f"<Part {self.number}: {self.name}>"

class Subpart(Base):
    """Subpart model representing a subpart within a part."""
    __tablename__ = "subpart"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(50), nullable=False)  # Like "A", "B", etc.
    name = Column(String(255), nullable=False)
    part_id = Column(Integer, ForeignKey("part.id"))
    
    # Additional metadata
    description = Column(Text, nullable=True)
    
    # Relationships
    part = relationship("Part", back_populates="subparts")
    sections = relationship("Section", back_populates="subpart")
    
    def __repr__(self):
        return f"<Subpart {self.identifier}: {self.name}>"

class Section(Base):
    """Section model representing a section within a part or subpart."""
    __tablename__ = "section"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), nullable=False)  # Like "1.1", "1.2", etc.
    name = Column(String(255), nullable=False)
    part_id = Column(Integer, ForeignKey("part.id"))
    subpart_id = Column(Integer, ForeignKey("subpart.id"), nullable=True)
    
    # Content
    text_content = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    
    # Additional metadata
    full_identifier = Column(String(50), nullable=True)  # Like "Section 1.1"
    source_url = Column(String(255), nullable=True)
    effective_date = Column(DateTime, nullable=True)
    
    # Relationships
    part = relationship("Part", back_populates="sections")
    subpart = relationship("Subpart", back_populates="sections")
    paragraphs = relationship("Paragraph", back_populates="section", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Section {self.number}: {self.name}>"

class Paragraph(Base):
    """Paragraph model representing a paragraph within a section."""
    __tablename__ = "paragraph"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(50), nullable=True)  # Like "(a)", "(1)", "(i)", etc.
    section_id = Column(Integer, ForeignKey("section.id"))
    parent_id = Column(Integer, ForeignKey("paragraph.id"), nullable=True)
    
    # Content
    text_content = Column(Text, nullable=False)
    
    # Additional metadata
    level = Column(Integer, nullable=False, default=1)  # Nesting level
    order_index = Column(Integer, nullable=False, default=0)  # Order within parent
    
    # Relationships
    section = relationship("Section", back_populates="paragraphs")
    parent = relationship("Paragraph", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<Paragraph {self.identifier}>"

class RegulationMetrics(Base):
    """Metrics for regulations and content."""
    __tablename__ = "regulation_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    regulation_id = Column(Integer, ForeignKey("regulation.id"), nullable=True)
    title_id = Column(Integer, ForeignKey("title.id"), nullable=True)
    agency_id = Column(Integer, ForeignKey("agency.id"), nullable=True)
    part_id = Column(Integer, ForeignKey("part.id"), nullable=True)
    section_id = Column(Integer, ForeignKey("section.id"), nullable=True)
    
    # Basic metrics
    word_count = Column(Integer, nullable=False, default=0)
    section_count = Column(Integer, nullable=False, default=0)
    paragraph_count = Column(Integer, nullable=False, default=0)
    
    # Complexity metrics
    avg_word_length = Column(Float, nullable=True)
    avg_sentence_length = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)  # Flesch-Kincaid
    
    # Change metrics
    version_number = Column(Integer, nullable=False, default=1)
    word_count_change = Column(Integer, nullable=True)  # From previous version
    
    # Timestamps
    calculated_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    regulation = relationship("Regulation", back_populates="metrics", foreign_keys=[regulation_id])
    
    def __repr__(self):
        entity_type = "Unknown"
        entity_id = None
        
        if self.title_id:
            entity_type = "Title"
            entity_id = self.title_id
        elif self.part_id:
            entity_type = "Part"
            entity_id = self.part_id
        elif self.section_id:
            entity_type = "Section"
            entity_id = self.section_id
            
        return f"<RegulationMetrics for {entity_type} {entity_id}>"

class Term(Base):
    """Significant terms extracted from regulations."""
    __tablename__ = "term"
    
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(255), nullable=False, index=True)
    
    # Frequencies
    total_occurrences = Column(Integer, nullable=False, default=0)
    document_occurrences = Column(Integer, nullable=False, default=0)
    
    # Timestamp
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Term {self.term}>"

class TermFrequency(Base):
    """Term frequency within a specific regulation."""
    __tablename__ = "term_frequency"
    
    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, ForeignKey("term.id"))
    regulation_id = Column(Integer, ForeignKey("regulation.id"))
    
    # Frequency data
    frequency = Column(Integer, nullable=False, default=0)
    tfidf_score = Column(Float, nullable=True)  # Term Frequency-Inverse Document Frequency
    
    def __repr__(self):
        return f"<TermFrequency {self.term_id} in {self.regulation_id}>"