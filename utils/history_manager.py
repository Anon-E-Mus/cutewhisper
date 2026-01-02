"""
History Manager - Store and retrieve transcription history
Uses SQLite database for persistence
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manage transcription history"""

    def __init__(self, db_path='data/transcriptions.db'):
        """
        Initialize history manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()

    def init_database(self):
        """Create SQLite database and table if not exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    text TEXT NOT NULL,
                    language TEXT,
                    duration REAL,
                    audio_file TEXT
                )
            ''')
            conn.commit()
            conn.close()
            logger.info(f"History database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def add_transcription(self, text, language='en', duration=None, audio_file=None):
        """
        Add a transcription to history

        Args:
            text: Transcribed text
            language: Detected language code
            duration: Audio duration in seconds
            audio_file: Path to audio file (optional)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transcriptions (timestamp, text, language, duration, audio_file)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), text, language, duration, audio_file))
            conn.commit()
            conn.close()
            logger.debug(f"Added transcription to history: {text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to add transcription: {e}")

    def get_all(self, limit=None, search=None):
        """
        Retrieve all transcriptions

        Args:
            limit: Maximum number of entries to return
            search: Optional search string to filter results

        Returns:
            List of tuples (id, timestamp, text, language, duration, audio_file)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if search:
                cursor.execute('''
                    SELECT * FROM transcriptions
                    WHERE text LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (f'%{search}%', limit if limit else 1000))
            else:
                limit_str = limit if limit else 1000
                cursor.execute('''
                    SELECT * FROM transcriptions
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit_str,))

            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve transcriptions: {e}")
            return []

    def get_by_id(self, id):
        """
        Get a specific transcription by ID

        Args:
            id: Transcription ID

        Returns:
            Tuple (id, timestamp, text, language, duration, audio_file) or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM transcriptions WHERE id = ?', (id,))
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Failed to get transcription {id}: {e}")
            return None

    def delete(self, id):
        """
        Delete a transcription by ID

        Args:
            id: Transcription ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transcriptions WHERE id = ?', (id,))
            conn.commit()
            conn.close()
            logger.info(f"Deleted transcription {id}")
        except Exception as e:
            logger.error(f"Failed to delete transcription {id}: {e}")

    def clear_all(self):
        """Clear all transcriptions from history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transcriptions')
            conn.commit()
            conn.close()
            logger.info("Cleared all transcription history")
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")

    def export_to_file(self, output_path):
        """
        Export all transcriptions to text file

        Args:
            output_path: Path to output text file
        """
        try:
            results = self.get_all()
            with open(output_path, 'w', encoding='utf-8') as f:
                for row in results:
                    id, timestamp, text, language, duration, audio_file = row
                    # Format timestamp nicely
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        formatted_time = timestamp

                    f.write(f"[{formatted_time}] ({language.upper()})\n")
                    f.write(f"{text}\n")
                    f.write("="*80 + "\n\n")
            logger.info(f"Exported {len(results)} transcriptions to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            raise

    def get_count(self):
        """Get total number of transcriptions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM transcriptions')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Failed to get count: {e}")
            return 0
