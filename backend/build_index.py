"""
Bible Downloader & Index Builder
Downloads KJV Bible JSON from a public source and builds the FAISS index.
Run this script ONCE before starting the server.

Usage: python build_index.py
"""

import json
import logging
import os
import sys
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("bible_builder")

# Public domain KJV Bible JSON
BIBLE_URL = "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master/Books.json"
FALLBACK_URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_kjv.json"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BIBLE_PATH = os.path.join(DATA_DIR, "bible_kjv.json")


def download_bible():
    """Download KJV Bible JSON and convert to our format."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(BIBLE_PATH):
        logger.info(f"Bible JSON already exists at {BIBLE_PATH}. Skipping download.")
        return

    logger.info("Downloading KJV Bible JSON...")

    try:
        # Try primary source (thiagobodruk format: [{name, chapters: [[verse,...]]}])
        urllib.request.urlretrieve(FALLBACK_URL, BIBLE_PATH + ".tmp")
        with open(BIBLE_PATH + ".tmp", "r", encoding="utf-8") as f:
            raw = json.load(f)

        bible = {}
        for book in raw:
            book_name = book["name"]
            bible[book_name] = {}
            for ch_idx, chapter in enumerate(book["chapters"]):
                ch_num = str(ch_idx + 1)
                bible[book_name][ch_num] = {}
                for v_idx, verse_text in enumerate(chapter):
                    v_num = str(v_idx + 1)
                    bible[book_name][ch_num][v_num] = verse_text

        with open(BIBLE_PATH, "w", encoding="utf-8") as f:
            json.dump(bible, f, ensure_ascii=False, indent=2)

        os.remove(BIBLE_PATH + ".tmp")
        logger.info(f"Bible downloaded and saved to {BIBLE_PATH}")

        # Count stats
        total_books = len(bible)
        total_verses = sum(
            len(verses)
            for chapters in bible.values()
            for verses in chapters.values()
        )
        logger.info(f"Books: {total_books} | Total verses: {total_verses}")

    except Exception as e:
        logger.error(f"Download failed: {e}")
        logger.info("Generating minimal KJV sample for testing...")
        _generate_sample_bible()


def _generate_sample_bible():
    """Generate a minimal Bible sample for testing when download fails."""
    sample = {
        "Genesis": {
            "1": {str(i): f"Genesis 1:{i} verse text." for i in range(1, 32)},
            "2": {str(i): f"Genesis 2:{i} verse text." for i in range(1, 26)},
            "50": {str(i): f"Genesis 50:{i} verse text." for i in range(1, 27)},
        },
        "Psalms": {
            "23": {
                "1": "The LORD is my shepherd; I shall not want.",
                "2": "He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
                "3": "He restoreth my soul: he leadeth me in the paths of righteousness for his name's sake.",
                "4": "Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me.",
                "5": "Thou preparest a table before me in the presence of mine enemies: thou anointest my head with oil; my cup runneth over.",
                "6": "Surely goodness and mercy shall follow me all the days of my life: and I will dwell in the house of the LORD for ever.",
            }
        },
        "John": {
            "3": {
                "16": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                "17": "For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
            },
            "4": {str(i): f"John 4:{i} verse text." for i in range(1, 55)},
            "11": {"35": "Jesus wept."},
        },
        "Romans": {
            "5": {
                "8": "But God commendeth his love toward us, in that, while we were yet sinners, Christ died for us.",
            },
            "8": {
                "28": "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.",
                "38": "For I am persuaded, that neither death, nor life, nor angels, nor principalities, nor powers, nor things present, nor things to come,",
                "39": "Nor height, nor depth, nor any other creature, shall be able to separate us from the love of God, which is in Christ Jesus our Lord.",
            },
            "15": {str(i): f"Romans 15:{i} verse text." for i in range(1, 34)},
        },
        "Revelation": {
            "22": {str(i): f"Revelation 22:{i} verse text." for i in range(1, 22)},
        },
        "Matthew": {
            "5": {
                "3": "Blessed are the poor in spirit: for theirs is the kingdom of heaven.",
                "4": "Blessed are they that mourn: for they shall be comforted.",
                "5": "Blessed are the meek: for they shall inherit the earth.",
            },
            "28": {
                "19": "Go ye therefore, and teach all nations, baptizing them in the name of the Father, and of the Son, and of the Holy Ghost:",
                "20": "Teaching them to observe all things whatsoever I have commanded you: and, lo, I am with you always, even unto the end of the world.",
            },
        },
        "Ephesians": {
            "2": {
                "8": "For by grace are ye saved through faith; and that not of yourselves: it is the gift of God:",
                "9": "Not of works, lest any man should boast.",
            }
        },
        "Philippians": {
            "4": {
                "13": "I can do all things through Christ which strengtheneth me.",
            }
        },
    }

    with open(BIBLE_PATH, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)
    logger.info(f"Sample Bible saved to {BIBLE_PATH}")


def build_index():
    """Build FAISS index from the downloaded Bible."""
    from dotenv import load_dotenv
    load_dotenv()

    from rag.vector_store import VectorStore
    store = VectorStore()
    store.initialize()
    logger.info("FAISS index built successfully!")


if __name__ == "__main__":
    download_bible()
    build_index()
    logger.info("✅ Setup complete! You can now run: uvicorn main:app --reload")
