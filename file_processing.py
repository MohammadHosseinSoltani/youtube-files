#!/usr/bin/env python3
"""
Comprehensive Text Analysis Tool
Demonstrates multiple Python features, optimizations, and best practices.
"""

import os
import re
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter
from contextlib import contextmanager
from functools import wraps, lru_cache
import argparse

# Configuration and Data Classes
@dataclass
class TextStats:
    """Data class to store text analysis results"""
    filename: str
    word_count: int = 0
    char_count: int = 0
    line_count: int = 0
    avg_word_length: float = 0.0
    most_common_words: List[Tuple[str, int]] = field(default_factory=list)
    sentiment_score: float = 0.0
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.word_count > 0:
            self.avg_word_length = self.char_count / self.word_count

# Custom Exceptions
class TextAnalysisError(Exception):
    pass

class FileProcessingError(TextAnalysisError):
    pass

# Decorators
def timer(func):
    """Decorator to measure function execution time using perf_counter"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        logging.info(f"{func.__name__} executed in {duration:.4f} seconds")
        return result
    return wrapper

def validate_file(func):
    """Decorator to validate file existence"""
    @wraps(func)
    def wrapper(self, filepath, *args, **kwargs):
        if not Path(filepath).exists():
            raise FileProcessingError(f"File not found: {filepath}")
        return func(self, filepath, *args, **kwargs)
    return wrapper

# Context Manager
@contextmanager
def file_handler(filepath: str, mode: str = 'r'):
    """Context manager for safe file handling"""
    file_obj = None
    try:
        file_obj = open(filepath, mode, encoding='utf-8')
        yield file_obj
    except IOError as e:
        raise FileProcessingError(f"Error opening file {filepath}: {e}")
    finally:
        if file_obj is not None:
            file_obj.close()

# Main Analysis Class
class TextAnalyzer:
    """
    Comprehensive text analyzer demonstrating OOP principles,
    property decorators, and modern Python features.
    """
    
    def __init__(self, stop_words: Optional[List[str]] = None):
        self._stop_words = set(stop_words or self._default_stop_words())
        self._analysis_cache = {}
        self.logger = self._setup_logging()
        
    @property
    def stop_words(self) -> set:
        return self._stop_words
    
    @stop_words.setter
    def stop_words(self, words: List[str]):
        self._stop_words = set(words)
    
    @staticmethod
    def _default_stop_words() -> List[str]:
        return ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    
    @classmethod
    def from_config(cls, config_path: str):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return cls(stop_words=config.get('stop_words'))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Could not load config: {e}. Using defaults.")
            return cls()
    
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    @lru_cache(maxsize=128)
    def _clean_word(self, word: str) -> str:
        """Clean and normalize a word (cached for performance)"""
        return re.sub(r'[^\w]', '', word.lower())
    
    @timer
    @validate_file
    def analyze_file(self, filepath: str) -> TextStats:
        """
        Synchronous file analysis method.
        """
        if filepath in self._analysis_cache:
            return self._analysis_cache[filepath]

        try:
            with file_handler(filepath) as file_obj:
                content = file_obj.read()
            
            lines = content.splitlines()
            
            # Use Walrus Operator (:=) to prevent empty strings after cleaning
            words = [cleaned for word in content.split() if (cleaned := self._clean_word(word))]
            filtered_words = [word for word in words if word not in self._stop_words]
            
            word_freq = Counter(filtered_words)
            
            stats = TextStats(
                filename=Path(filepath).name,
                word_count=len(words),
                char_count=sum(len(word) for word in words),
                line_count=len(lines),
                most_common_words=word_freq.most_common(10)
            )
            
            stats.sentiment_score = self._calculate_sentiment(filtered_words)
            self._analysis_cache[filepath] = stats
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {filepath}: {e}")
            raise TextAnalysisError(f"Analysis failed: {e}")
    
    def _calculate_sentiment(self, words: List[str]) -> float:
        """Optimized sentiment analysis using generator expressions."""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'}
        negative_words = {'bad', 'terrible', 'awful', 'horrible', 'disappointing'}
        
        # Generator expressions are much faster and memory efficient than len(list(filter(...)))
        positive_count = sum(1 for w in words if w in positive_words)
        negative_count = sum(1 for w in words if w in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0
        
        return (positive_count - negative_count) / total_sentiment_words
    
    async def analyze_multiple_files(self, filepaths: List[str]) -> List[TextStats]:
        """
        True Asynchronous method for processing multiple files.
        Uses asyncio.to_thread to prevent blocking the event loop with synchronous file I/O.
        """
        tasks = [asyncio.to_thread(self.analyze_file, filepath) for filepath in filepaths]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def generate_report(self, stats_list: List[TextStats]) -> str:
        """Generates report string."""
        if not stats_list:
            return "No data to report."

        total_words = sum(stats.word_count for stats in stats_list)
        avg_sentiment = sum(stats.sentiment_score for stats in stats_list) / len(stats_list)
        
        report_lines = [
            "=" * 50,
            "TEXT ANALYSIS REPORT",
            "=" * 50,
            f"Total files analyzed: {len(stats_list)}",
            f"Total words processed: {total_words:,}",
            f"Average sentiment score: {avg_sentiment:.3f}",
            "",
            "Individual File Results:",
            "-" * 30
        ]
        
        for i, stats in enumerate(stats_list, 1):
            top_words = ', '.join(f"{word}({count})" for word, count in stats.most_common_words[:5])
            report_lines.extend([
                f"{i}. {stats.filename}",
                f"   Words: {stats.word_count:,}",
                f"   Lines: {stats.line_count:,}",
                f"   Avg word length: {stats.avg_word_length:.2f}",
                f"   Sentiment: {stats.sentiment_score:.3f}",
                f"   Top words: {top_words}",
                ""
            ])
        
        return '\n'.join(report_lines)

# Utility Functions
def setup_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Comprehensive Text Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('files', nargs='+', help='Text files to analyze')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--output', type=str, help='Output file for results')
    
    # Bug Fix: mapped to 'use_async' instead of the reserved keyword 'async'
    parser.add_argument(
        '--async-mode',
        dest='use_async',
        action='store_true',
        help='Use asynchronous processing'
    )
    return parser

def save_results_json(stats_list: List[TextStats], output_path: str):
    """Save results to JSON file using built-in dataclass serialization"""
    # Much cleaner way to convert dataclasses to dicts
    results = [asdict(stats) for stats in stats_list]
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

# Main execution function
async def main():
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    try:
        analyzer = TextAnalyzer.from_config(args.config) if args.config else TextAnalyzer()
        
        if args.use_async:
            print("Processing files asynchronously...")
            results = await analyzer.analyze_multiple_files(args.files)
            
            # Filter out exceptions and notify user of errors
            stats_list = []
            for filepath, result in zip(args.files, results):
                if isinstance(result, Exception):
                    print(f"Error processing {filepath}: {result}")
                else:
                    stats_list.append(result)
        else:
            print("Processing files synchronously...")
            stats_list = []
            for filepath in args.files:
                try:
                    stats_list.append(analyzer.analyze_file(filepath))
                except TextAnalysisError as e:
                    print(f"Error processing {filepath}: {e}")
        
        if not stats_list:
            print("No files were successfully processed.")
            return
        
        report = analyzer.generate_report(stats_list)
        print(report)
        
        if args.output:
            if args.output.endswith('.json'):
                save_results_json(stats_list, args.output)
            else:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(report)
            print(f"Results saved to {args.output}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.exception("Unexpected error occurred")

if __name__ == "__main__":
    asyncio.run(main())
