import re
from typing import List, Set, Tuple

class ToolSelector:
    """
    V2.1 Constraint-Aware Tool Selector for JARVIS.
    Features strict relative scoring, context-awareness, and safe fallbacks.
    """
    def __init__(self, registry):
        self.registry = registry
        
        self.KNOWN_SITES = {
            "youtube", "google", "coursera", "spotify", "github", 
            "amazon", "netflix", "leetcode"
        }
        
        self.MATH_KEYWORDS = {
            "+", "-", "*", "/", "calculate", "compute", "evaluate", 
            "sqrt", "square", "cube", "power", "percent", "%"
        }

    def select(self, query: str, top_k: int = 2, context=None) -> List:
        print(f"\n[ToolSelector V2.1] Evaluating query: '{query}'")
        
        all_tools = self.registry.list_tools()
        
        # 1. HARD FILTER
        valid_tools = self._hard_filter(query, all_tools, context)
        
        if not valid_tools:
            print("[ToolSelector V2.1] All tools filtered out by hard constraints.")
            return self._safe_fallback()

        # 2. INTENT CLASSIFICATION
        intents = self._detect_intents(query)
        if not intents:
            intents.add("information")
        print(f"[ToolSelector V2.1] Detected Intents → {intents}")


        # 3. MATCHING & SCORING
        scored_tools = self._score_tools(query, valid_tools, intents, context)
        print("[ToolSelector V2.1] Candidate Scores →", [(t.name, round(s, 2)) for t, s in scored_tools])

        # 4. STRICT SELECTION
        if not scored_tools:
            return self._safe_fallback()

        best_score = scored_tools[0][1]
        
        # 🔥 Fix 3: Safe fallback to explain for weak queries
        if best_score < 0.8:
            print(f"[ToolSelector V2.1] Weak confidence ({round(best_score, 2)}). Falling back to explain.")
            return self._safe_fallback()

        # Strict relative thresholding 
        selected = [
            tool for tool, score in scored_tools
            if score >= best_score * 0.8
        ]
            
        final_selection = selected[:top_k]
        print(f"[ToolSelector V2.1] Final Selection → {[t.name for t in final_selection]}\n")
        
        return final_selection

    def _safe_fallback(self) -> List:
        """Helper to safely fallback to the explain tool."""
        explain_tool = self.registry.get("explain")
        return [explain_tool] if explain_tool else []

    def _hard_filter(self, query: str, tools: List, context) -> List:
        valid = []
        q = query.lower().strip()
        words = q.split()

        doc_loaded = self._is_document_loaded(context)
        has_web_context = self._has_retrieved_content(context)

        for tool in tools:
            name = tool.name

            if name == "load_document":
                if doc_loaded:
                    print("  [Reject] load_document → document already in context.")
                    continue
                if not re.search(r'\.(pdf|txt|md)\b', q):
                    continue

            elif name == "calculator":
                has_num = bool(re.search(r'\d', q))
                has_math_word = any(kw in q for kw in self.MATH_KEYWORDS)
                is_pure_math = bool(re.match(r'^[\d\s\+\-\*\/\^\(\)\.]+$', q))
                if not (is_pure_math or (has_num and has_math_word)):
                    continue

            elif name == "open_website":
                has_target = any(site in q for site in self.KNOWN_SITES) or bool(re.search(r'\.[a-z]{2,3}\b', q))
                has_nav_word = any(phrase in q for phrase in ["open", "visit", "launch", "go to"])
                
                # 🔥 Fix 2: Require BOTH navigation intent AND a valid target
                if not (has_target and has_nav_word):
                    print("  [Reject] open_website → requires BOTH navigation intent and a valid target.")
                    continue

            elif name == "web_retriever":
                if has_web_context:
                    print("  [Reject] web_retriever → web context already exists.")
                    continue
                if len(words) <= 1:
                    print("  [Reject] web_retriever → single-word query is too vague.")
                    continue

            elif name == "rag_search":
                if not doc_loaded and not re.search(r'\.(pdf|txt|md)\b', q):
                    continue

            valid.append(tool)
            
        return valid

    def _detect_intents(self, query: str) -> Set[str]:
        q = query.lower()
        intents = set()
        
        signatures = {
            "navigation": ["open", "visit", "launch", "go to"] + list(self.KNOWN_SITES),
            "calculation": list(self.MATH_KEYWORDS),
            "document": ["load", "read", "file", "document", "pdf", "txt", "md", "summarize"],
            "information": ["explain", "what is", "who is", "how to", "guide", "learn", "teach", "latest", "news"]
        }
        
        for intent_name, keywords in signatures.items():
            if any(k in q for k in keywords):
                intents.add(intent_name)
                
        if bool(re.search(r'\d', q)) and "calculation" in intents:
            intents.add("calculation")
            
        return intents

    def _score_tools(self, query: str, valid_tools: List, intents: Set[str], context) -> List[Tuple[any, float]]:
        q = query.lower()
        scored = []
        
        doc_loaded = self._is_document_loaded(context)
        has_web_context = self._has_retrieved_content(context)
        
        for tool in valid_tools:
            score = 0.0
            
            # 1. Intent Alignment
            if tool.name == "open_website" and "navigation" in intents: 
                score += 3.0
            if tool.name == "calculator" and "calculation" in intents: 
                score += 3.0
                
            if tool.name in ["load_document", "rag_search"] and "document" in intents:
                score += 3.0
                if tool.name == "rag_search" and doc_loaded:
                    score += 1.0 
                    
            if tool.name == "explain" and "information" in intents: 
                score += 3.0
                if len(q.split()) <= 3:
                    score += 0.5
                # 🔥 Fix 1: Boost explain if web context already exists
                if has_web_context:
                    score += 1.5
            
            if tool.name == "web_retriever" and "information" in intents:
                score += 2.5 
            
            # 2. Metadata Keyword/Entity matching
            for intent_kw in getattr(tool, "intents", []):
                if intent_kw in q: score += 1.5
            for entity_kw in getattr(tool, "entities", []):
                if entity_kw in q: score += 1.0
                
            # 3. Semantic Similarity (Capped)
            if hasattr(self.registry, "semantic"):
                semantic_score = self.registry.semantic.similarity(query, tool)
                score += min(semantic_score, 0.6) * 2.0
                
            scored.append((tool, score))
            
        return sorted(scored, key=lambda x: x[1], reverse=True)

    # =========================
    # 🧠 V2 CONTEXT HELPERS
    # =========================
    def _is_document_loaded(self, context) -> bool:
        if not context: return False
        if getattr(context, "document_loaded", False): return True
        
        history = getattr(context, "history", []) or []
        for entry in history:
            if entry.get("tool") == "load_document":
                result_str = str(entry.get("result", "")).lower()
                if not any(sig in result_str for sig in ("⚠️", "error", "failed", "not found")):
                    return True
        return False

    def _has_retrieved_content(self, context) -> bool:
        if not context: return False
        tool_outputs = getattr(context, "tool_outputs", {}) or {}
        return bool(tool_outputs.get("retrieved_content") or tool_outputs.get("search_results"))