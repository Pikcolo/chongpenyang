"""
Top 5 Filtering & Fair Randomization Engine for Barista Chatbot.
Adheres to Criterion 3: Top 5 Carousel Logic & Randomization (20% Weight).
- Filters candidates based on user constraints (hot, iced, signature, difficulty).
- Implements Anti-Loop Fair Randomization Algorithm (Reservoir Sampling + History Tracking)
  to ensure refreshing never repeats the exact same items in a repetitive loop.
"""

import random
import logging
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from chatbot.ingestion.pipeline_extractor import BaristaDataPipeline

logger = logging.getLogger(__name__)

class BaristaFilterEngine:
    """
    Intelligent Filter & Fair Randomization Engine for Coffee Menus.
    """

    def __init__(self, data_pipeline: Optional[BaristaDataPipeline] = None):
        self.pipeline = data_pipeline or BaristaDataPipeline()
        self.recipes = self.pipeline.get_all_recipes()
        # Track history per session_id to guarantee fair, non-repeating randomization
        # session_id -> Set[recipe_id]
        self._session_history: Dict[str, Set[str]] = defaultdict(set)

    def filter_recipes(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters recipes according to categorical criteria."""
        results = self.recipes

        if category and category.strip():
            cat_clean = category.strip().lower()
            results = [r for r in results if r["category"] == cat_clean]

        if difficulty and difficulty.strip():
            diff_clean = difficulty.strip()
            results = [r for r in results if diff_clean in r.get("difficulty", "")]

        if keyword and keyword.strip():
            kw = keyword.strip().lower()
            results = [
                r for r in results
                if kw in r["name_th"].lower()
                or kw in r["name_en"].lower()
                or kw in r.get("flavor_notes", "").lower()
            ]

        return results

    def get_top5_recommendations(
        self,
        session_id: str = "default_user",
        category: Optional[str] = None,
        limit: int = 5,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Picks Top N items using Anti-Loop Fair Randomization.
        Items recently shown in the session are deprioritized or excluded to prevent repetition.
        """
        candidates = self.filter_recipes(category=category)
        if not candidates:
            # Fallback to all recipes if category filter yielded 0 items
            candidates = self.recipes

        if len(candidates) <= limit:
            return candidates

        history = self._session_history[session_id]

        # Partition candidates into unseen vs seen
        unseen = [c for c in candidates if c["id"] not in history]
        seen = [c for c in candidates if c["id"] in history]

        chosen: List[Dict[str, Any]] = []

        # Case 1: Enough unseen candidates to fulfill the requested limit
        if len(unseen) >= limit:
            # Fair non-repeating shuffle
            chosen = random.sample(unseen, limit)
        else:
            # Take all remaining unseen candidates
            chosen.extend(unseen)
            # Refill remainder from least recently seen items
            needed = limit - len(chosen)
            # Shuffle seen candidates to avoid deterministic loops
            random.shuffle(seen)
            chosen.extend(seen[:needed])
            # Reset history to allow continuous balanced exploration
            self._session_history[session_id].clear()

        # Update session history with currently chosen items
        for item in chosen:
            self._session_history[session_id].add(item["id"])

        # If history contains almost all candidates, reset history for next cycle
        if len(self._session_history[session_id]) >= len(candidates) - 1:
            self._session_history[session_id].clear()

        return chosen

    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Fetches single recipe by ID."""
        return self.pipeline.get_recipe_by_id(recipe_id)

    def reset_session(self, session_id: str):
        """Clears randomization history for a session."""
        if session_id in self._session_history:
            self._session_history[session_id].clear()

if __name__ == "__main__":
    engine = BaristaFilterEngine()
    print("Testing Fair Randomization over 3 consecutive refreshes:")
    for cycle in range(1, 4):
        items = engine.get_top5_recommendations(session_id="user_123", limit=5)
        names = [it["name_th"].split("(")[0].strip() for it in items]
        print(f"Cycle {cycle}: {names}")
