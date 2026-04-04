#from planner.planner import Planner
#from executor.executor import Executor
#from tools.registry import ToolRegistry
#from tools.basic_tools import OpenWebsiteTool, EchoTool
#from tools.rag_tool import RAGTool
#from tools.load_doc_tool import LoadDocTool

#from rag.qa import RAGQA
#from rag.embedder import Embedder
#from rag.store import VectorStore
#from rag.retriever import Retriever
#from rag.ingestor import Ingestor
#from tools.explain_tool import ExplainTool

#def is_good_result(results):
    #for r in results:
      #  if "⚠️" in str(r):
     #       return False
    #return True


#if __name__ == "__main__":
    #embedder = Embedder()
    #store = VectorStore()

    #ingestor = Ingestor(embedder, store)
    #retriever = Retriever(embedder, store)
    #rag = RAGQA(retriever)

    #registry = ToolRegistry()
    #registry.register(OpenWebsiteTool())
    #registry.register(EchoTool())
    #registry.register(RAGTool(rag))
    #registry.register(LoadDocTool(ingestor))
    #registry.register(ExplainTool())

    #planner = Planner(registry)
    #executor = Executor(registry)

    #print("JARVIS started. Type 'exit' to quit.")

    #while True:
        #user_input = input("You: ").strip()

        #if any(word in user_input.lower() for word in ["exit", "quit", "bye", "goodbye"]):
          #  print("JARVIS: Goodbye 👋")
         #   break

        #max_attempts = 2
        #attempt = 0
        #final_results = None

        #while attempt < max_attempts:
            #print(f"\n🔁 Attempt {attempt+1}")

            #plan = planner.plan(user_input)

            #if plan is None:
              #  print("⚠️ Failed to generate plan.")
             #   break

            # 🔥 REMOVE NOISY ECHO STEPS
            #plan.steps = [
              #  step for step in plan.steps
             #   if not (step.action == "echo" and "open" in str(step.args).lower())
            #]

            #print("PLAN:", plan)

            #results = executor.execute(plan)

           # for result in results:
            #    print("RESULT:", result)

           # reflection = planner.llm.generate_reflection(
            #    goal=user_input,
             #   plan=plan,
              #  results=results
            #)

            #if reflection is None:
             #   final_results = results
              #  break

            #print("🧠 Reflection:", reflection)

            ## 🔥 SMART ACCEPTANCE
            #if reflection.status.lower() == "success" or is_good_result(results):
             #   final_results = results
              #  break

            #print("⚠️ Retrying...\n")
            #attempt += 1

        #if final_results is None:
           # print("❌ Could not complete task successfully.")

from planner.planner import Planner
from executor.executor import Executor
from tools.registry import ToolRegistry
from tools.basic_tools import OpenWebsiteTool, EchoTool
from tools.rag_tool import RAGTool
from tools.load_doc_tool import LoadDocTool
from tools.explain_tool import ExplainTool

from rag.qa import RAGQA
from rag.embedder import Embedder
from rag.store import VectorStore
from rag.retriever import Retriever
from rag.ingestor import Ingestor


if __name__ == "__main__":
    # =========================
    # 🔧 RAG SETUP
    # =========================
    embedder = Embedder()
    store = VectorStore()

    ingestor = Ingestor(embedder, store)
    retriever = Retriever(embedder, store)
    rag = RAGQA(retriever)

    # =========================
    # 🔧 TOOL REGISTRY
    # =========================
    registry = ToolRegistry()
    registry.register(OpenWebsiteTool())
    registry.register(EchoTool())
    registry.register(RAGTool(rag))
    registry.register(LoadDocTool(ingestor))
    registry.register(ExplainTool())

    # =========================
    # 🧠 CORE SYSTEM
    # =========================
    planner = Planner(registry)
    executor = Executor(registry)

    print("JARVIS started. Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()

        if any(word in user_input.lower() for word in ["exit", "quit", "bye", "goodbye"]):
            print("JARVIS: Goodbye 👋")
            break

        # =========================
        # 🧠 PLAN
        # =========================
        plan = planner.plan(user_input)

        if plan is None or not plan.steps:
            print("⚠️ No valid plan generated.")
            continue

        # 🔥 REMOVE NOISY ECHO STEPS
        plan.steps = [
            step for step in plan.steps
            if not (step.action == "echo" and "open" in str(step.args).lower())
        ]

        print("PLAN:", plan)

        # =========================
        # ⚙️ EXECUTE
        # =========================
        results = executor.execute(plan)

        for result in results:
            print("RESULT:", result)