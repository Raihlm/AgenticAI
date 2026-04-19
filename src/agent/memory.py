"""Conversation memory and context management."""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
from ..config import config


class ConversationMemory:
    """Manage conversation history and long-term memory."""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.memory_dir = Path(config.MEMORY_DIR)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.session_file = self.memory_dir / f"session_{self.session_id}.json"
        self.long_term_file = self.memory_dir / "long_term_memory.json"

        self.conversation_history: List[Dict] = []
        self.long_term_memories: List[Dict] = []

        self._load_session()
        self._load_long_term_memory()

    def _load_session(self):
        """Load current session from file."""
        if self.session_file.exists():
            try:
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                    self.conversation_history = data.get("history", [])
            except Exception:
                self.conversation_history = []

    def _save_session(self):
        """Save current session to file."""
        data = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "history": self.conversation_history,
            "updated_at": datetime.now().isoformat(),
        }
        with open(self.session_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_long_term_memory(self):
        """Load long-term memory from file."""
        if self.long_term_file.exists():
            try:
                with open(self.long_term_file, "r") as f:
                    self.long_term_memories = json.load(f)
            except Exception:
                self.long_term_memories = []

    def _save_long_term_memory(self):
        """Save long-term memory to file."""
        with open(self.long_term_file, "w") as f:
            json.dump(self.long_term_memories, f, indent=2)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to conversation history.

        Args:
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (tools_used, timestamp, etc.)
        """
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            entry["metadata"] = metadata

        self.conversation_history.append(entry)
        self._save_session()

    def add_to_long_term_memory(
        self,
        key: str,
        value: str,
        category: str = "general",
    ):
        """
        Add information to long-term memory.

        Args:
            key: Memory key/identifier
            value: Memory content
            category: Category for organization (facts, preferences, context)
        """
        entry = {
            "key": key,
            "value": value,
            "category": category,
            "created_at": datetime.now().isoformat(),
        }
        self.long_term_memories.append(entry)
        self._save_long_term_memory()

    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve relevant memories for the current context.

        Args:
            query: Current user query for relevance matching
            limit: Maximum number of memories to return

        Returns:
            List of relevant memory entries
        """
        # Simple keyword-based retrieval
        # (Could be enhanced with embeddings later)
        query_words = set(query.lower().split())

        scored_memories = []
        for memory in self.long_term_memories:
            text = f"{memory['key']} {memory['value']}".lower()
            score = sum(1 for word in query_words if word in text)
            if score > 0:
                scored_memories.append((score, memory))

        scored_memories.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored_memories[:limit]]

    def get_conversation_summary(self, last_n: int = 10) -> str:
        """Get a summary of recent conversation."""
        recent = self.conversation_history[-last_n:]
        if not recent:
            return ""

        summary_lines = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary_lines.append(f"{role}: {content}")

        return "\n".join(summary_lines)

    def get_context_for_query(self, query: str) -> str:
        """
        Build context string for the agent to use.

        Args:
            query: Current user query

        Returns:
            Formatted context string
        """
        context_parts = []

        # Add relevant long-term memories
        relevant = self.get_relevant_memories(query)
        if relevant:
            memories_str = "\n".join([f"- {m['key']}: {m['value']}" for m in relevant])
            context_parts.append(f"Relevant memories:\n{memories_str}")

        # Add recent conversation summary
        recent_summary = self.get_conversation_summary(5)
        if recent_summary:
            context_parts.append(f"Recent conversation:\n{recent_summary}")

        return "\n\n".join(context_parts) if context_parts else ""

    def clear_session(self):
        """Clear current session history."""
        self.conversation_history = []
        if self.session_file.exists():
            self.session_file.unlink()

    def list_sessions(self) -> List[str]:
        """List all saved session IDs."""
        sessions = []
        for f in self.memory_dir.glob("session_*.json"):
            sessions.append(f.stem.replace("session_", ""))
        return sorted(sessions)


# Global memory instance
_memory: Optional[ConversationMemory] = None


def get_memory() -> ConversationMemory:
    """Get or create the global memory instance."""
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory


def reset_memory():
    """Reset the global memory."""
    global _memory
    _memory = None
