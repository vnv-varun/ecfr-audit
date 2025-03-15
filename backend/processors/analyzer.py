#!/usr/bin/env python3

import pandas as pd
import numpy as np
import logging
import re
import textstat
from typing import Dict, List, Any, Optional
from collections import Counter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('analyzer')

def clean_text(text: str) -> str:
    """Clean text for analysis."""
    if not text:
        return ""
    
    # Remove HTML tags if any remain
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove special characters but keep sentence structure
    text = re.sub(r'[^\w\s\.\,\;\:\!\?]', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    
    # Clean the text first
    clean = clean_text(text)
    
    # Split by whitespace and count
    words = re.findall(r'\b\w+\b', clean)
    return len(words)

def count_sentences(text: str) -> int:
    """Count sentences in text."""
    if not text:
        return 0
    
    # Clean the text first
    clean = clean_text(text)
    
    # Split by sentence terminators
    sentences = re.split(r'[.!?]+', clean)
    # Count non-empty sentences
    return sum(1 for s in sentences if s.strip())

def count_paragraphs(text: str) -> int:
    """Count paragraphs in text."""
    if not text:
        return 0
    
    # Split by double newlines
    paragraphs = re.split(r'\n\s*\n', text)
    # Count non-empty paragraphs
    return sum(1 for p in paragraphs if p.strip())

def calculate_readability(text: str) -> Dict[str, float]:
    """Calculate readability metrics."""
    if not text or len(text) < 100:  # Need minimum text length for reliable metrics
        return {
            'flesch_reading_ease': 0,
            'flesch_kincaid_grade': 0,
            'smog_index': 0,
            'dale_chall_readability_score': 0,
            'difficulty_level': 0
        }
    
    clean = clean_text(text)
    
    # Use textstat library to calculate readability
    try:
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(clean),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(clean),
            'smog_index': textstat.smog_index(clean),
            'dale_chall_readability_score': textstat.dale_chall_readability_score(clean),
            'difficulty_level': textstat.text_standard(clean, float_output=True)
        }
    except Exception as e:
        logger.error(f"Error calculating readability: {e}")
        return {
            'flesch_reading_ease': 0,
            'flesch_kincaid_grade': 0,
            'smog_index': 0,
            'dale_chall_readability_score': 0,
            'difficulty_level': 0
        }

def extract_term_frequencies(text: str, min_length: int = 3, max_terms: int = 100) -> List[Dict[str, Any]]:
    """Extract term frequencies from text."""
    if not text:
        return []
    
    clean = clean_text(text)
    
    # Tokenize
    words = re.findall(r'\b\w+\b', clean.lower())
    
    # Filter short words
    words = [w for w in words if len(w) >= min_length]
    
    # Count frequencies
    counter = Counter(words)
    
    # Get most common terms
    return [
        {'term': term, 'frequency': freq} 
        for term, freq in counter.most_common(max_terms)
    ]

def analyze_text(text: str) -> Dict[str, Any]:
    """Perform comprehensive text analysis."""
    metrics = {}
    
    # Basic counts
    metrics['word_count'] = count_words(text)
    metrics['sentence_count'] = count_sentences(text)
    metrics['paragraph_count'] = count_paragraphs(text)
    
    # Average lengths
    if metrics['word_count'] > 0:
        # Average word length
        words = re.findall(r'\b\w+\b', clean_text(text))
        metrics['avg_word_length'] = np.mean([len(w) for w in words]) if words else 0
    else:
        metrics['avg_word_length'] = 0
        
    if metrics['sentence_count'] > 0:
        metrics['avg_sentence_length'] = metrics['word_count'] / metrics['sentence_count']
    else:
        metrics['avg_sentence_length'] = 0
    
    # Readability
    metrics.update(calculate_readability(text))
    
    # Term frequencies
    metrics['term_frequencies'] = extract_term_frequencies(text)
    
    return metrics

def analyze_regulation_batch(regulations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze a batch of regulations and return metrics."""
    results = []
    
    for reg in regulations:
        reg_id = reg.get('identifier', 'unknown')
        logger.info(f"Analyzing regulation: {reg_id}")
        
        try:
            # Get text content
            text = reg.get('text_content', '')
            
            # Skip empty regulations
            if not text:
                logger.warning(f"Regulation {reg_id} has no text content")
                continue
                
            # Analyze the text
            metrics = analyze_text(text)
            
            # Add regulation info
            result = {
                'regulation_id': reg_id,
                'title': reg.get('title', ''),
                'agency': reg.get('agency', ''),
                'metrics': metrics
            }
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error analyzing regulation {reg_id}: {e}")
    
    return results

def get_word_counts(
    regulations: Optional[List[Dict[str, Any]]] = None,
    df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """Calculate word count metrics from regulations or DataFrame."""
    if regulations:
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([
            {
                'id': r.get('identifier', ''),
                'title': r.get('title', ''),
                'agency': r.get('agency', ''),
                'title_number': int(r.get('identifier', '').split('-')[1]) if r.get('identifier', '').startswith('title-') else 0,
                'word_count': count_words(r.get('text_content', ''))
            }
            for r in regulations
        ])
    
    if df is None or df.empty:
        return {
            'total_word_count': 0,
            'agencies': [],
            'titles': []
        }
    
    # Calculate total word count
    total_word_count = df['word_count'].sum()
    
    # Group by agency
    agency_counts = df.groupby('agency').agg({
        'word_count': 'sum'
    }).reset_index()
    
    agency_data = [
        {
            'id': a.lower().replace(' ', '-'),
            'name': a,
            'word_count': int(c)
        }
        for a, c in zip(agency_counts['agency'], agency_counts['word_count'])
    ]
    
    # Group by title
    title_counts = df.groupby('title_number').agg({
        'word_count': 'sum'
    }).reset_index()
    
    title_data = [
        {
            'number': int(t),
            'word_count': int(c)
        }
        for t, c in zip(title_counts['title_number'], title_counts['word_count'])
    ]
    
    return {
        'total_word_count': int(total_word_count),
        'agencies': agency_data,
        'titles': title_data
    }

def get_complexity_metrics(
    regulations: Optional[List[Dict[str, Any]]] = None,
    df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """Calculate complexity metrics from regulations or DataFrame."""
    if regulations:
        # Process each regulation to get metrics
        metrics_data = []
        for r in regulations:
            text = r.get('text_content', '')
            if text:
                readability = calculate_readability(text)
                metrics_data.append({
                    'id': r.get('identifier', ''),
                    'title': r.get('title', ''),
                    'agency': r.get('agency', ''),
                    'title_number': int(r.get('identifier', '').split('-')[1]) if r.get('identifier', '').startswith('title-') else 0,
                    'readability_score': readability.get('flesch_reading_ease', 0),
                    'sentence_length': count_words(text) / max(count_sentences(text), 1),
                    'word_length': np.mean([len(w) for w in re.findall(r'\b\w+\b', clean_text(text))]) if text else 0
                })
        
        # Convert to DataFrame
        df = pd.DataFrame(metrics_data)
    
    if df is None or df.empty:
        return {
            'average_readability_score': 0,
            'average_sentence_length': 0,
            'average_word_length': 0,
            'agencies': [],
            'titles': []
        }
    
    # Calculate averages
    avg_readability = df['readability_score'].mean()
    avg_sentence_length = df['sentence_length'].mean()
    avg_word_length = df['word_length'].mean()
    
    # Group by agency
    agency_metrics = df.groupby('agency').agg({
        'readability_score': 'mean'
    }).reset_index()
    
    agency_data = [
        {
            'id': a.lower().replace(' ', '-'),
            'name': a,
            'readability_score': float(s)
        }
        for a, s in zip(agency_metrics['agency'], agency_metrics['readability_score'])
    ]
    
    # Group by title
    title_metrics = df.groupby('title_number').agg({
        'readability_score': 'mean'
    }).reset_index()
    
    title_data = [
        {
            'number': int(t),
            'readability_score': float(s)
        }
        for t, s in zip(title_metrics['title_number'], title_metrics['readability_score'])
    ]
    
    return {
        'average_readability_score': float(avg_readability),
        'average_sentence_length': float(avg_sentence_length),
        'average_word_length': float(avg_word_length),
        'agencies': agency_data,
        'titles': title_data
    }