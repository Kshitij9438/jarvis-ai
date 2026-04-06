from planner.schema import Plan, Action


class CompletenessChecker:
    def __init__(self):
        # 🔥 intent → required action mapping
        self.intent_action_map = {
            "open_website": "open_website",
            "explain": "explain",
            "summarize": "rag_search",
            "load_document": "load_document",
        }

    # =========================
    # 🧠 MAIN ENTRY
    # =========================
    def ensure(self, plan: Plan, intents: list, entities: dict) -> Plan:
        """
        Ensures plan covers all intents.
        Adds missing steps deterministically.
        """

        steps = plan.steps.copy()
        actions = [s.action for s in steps]

        for intent in intents:
            required_action = self.intent_action_map.get(intent)

            if not required_action:
                continue

            # already satisfied
            if required_action in actions:
                continue

            # 🔥 Try to fix missing step
            new_step = self._build_missing_step(intent, entities)

            if new_step:
                print(f"DEBUG: Completeness added → {new_step}")
                steps.append(new_step)

        return Plan(steps=steps)

    # =========================
    # 🧠 BUILD MISSING STEP
    # =========================
    def _build_missing_step(self, intent: str, entities: dict):
        """
        Build missing action based on available entities.
        """

        # 🌐 OPEN WEBSITE
        if intent == "open_website":
            if entities.get("websites"):
                site = entities["websites"][0]
                return Action(
                    action="open_website",
                    args={"url": self._normalize_url(site)}
                )

        # 🧠 EXPLAIN
        if intent == "explain":
            topics = entities.get("topics")
            if topics:
                topic = topics[0].strip()
                if topic in {"explain", "summarize", ""}:
                    return None
                return Action(
            action="explain",
            args={"query": topic}
        )

        # 📄 LOAD DOCUMENT
        if intent == "load_document":
            if entities.get("file_path"):
                return Action(
                    action="load_document",
                    args={"file_path": entities["file_path"]}
                )

        # 📚 SUMMARIZE
        if intent == "summarize":
            if entities.get("file_path"):
                return Action(
                    action="rag_search",
                    args={"query": "summary of loaded document"}
                )
            elif entities.get("topics"):
                return Action(
                    action="rag_search",
                    args={"query": entities["topics"][0]}
                )

        return None

    # =========================
    # 🌐 URL NORMALIZATION
    # =========================
    def _normalize_url(self, site: str) -> str:
        site = site.strip().lower()

        sites = {
            "youtube": "https://youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "spotify": "https://www.spotify.com",
            "coursera": "https://www.coursera.org",
        }

        if site in sites:
            return sites[site]

        if site.startswith("http"):
            return site

        if "." in site:
            return f"https://{site}"

        return f"https://www.{site}.com"