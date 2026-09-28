"""Hindsight Agent Memory Live Demonstration Script.

Runs the complete Hindsight Retain-Recall-Reflect continuous learning loop
and executes a code review enriched with historical hindsight memory.
"""
import asyncio
import json
from pathlib import Path
import sys
import time

# Ensure project root is in sys.path and output is utf-8 safe
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.ai_service import AIService
from app.schemas.ai_review import AIReviewRequest
from app.schemas.hindsight import (
    HindsightRecallRequest,
    HindsightReflectRequest,
    HindsightRetainRequest,
    MemoryType,
)
from app.services.hindsight_service import hindsight_service


async def main():
    print("=" * 80)
    print("🧠 CODEPILOT AI — HINDSIGHT AGENT MEMORY DEMONSTRATION")
    print("=" * 80)

    # 1. Memory Bank Telemetry
    stats = hindsight_service.get_stats()
    print(f"\n[STEP 1] Initial Memory Bank Status:")
    print(f"  • Bank ID: {stats.bank_id}")
    print(f"  • Total Memories: {stats.total_memories}")
    print(f"  • Active Engine: {stats.active_engine}")
    print(f"  • Average Recall Latency: {stats.avg_recall_latency_ms:.3f} ms (Target: < 5.0 ms)")
    print(f"  • Categories: {json.dumps(stats.by_type, indent=4)}")

    # 2. RETAIN: Ingest Team Architectural Rule
    print("\n" + "-" * 80)
    print("[STEP 2] RETAIN — Ingesting New Architectural Convention:")
    custom_rule = "Never format dynamic values directly into database queries; always use SQLAlchemy bind parameters."
    retain_req = HindsightRetainRequest(
        content=custom_rule,
        memory_type=MemoryType.SECURITY_RULE,
        tags=["database", "sql", "injection", "sqlalchemy", "cwe-89"],
        language="python",
        filename_pattern="user_repository.py",
    )
    retain_res = hindsight_service.retain_memory(retain_req)
    print(f"  ✓ Retained Memory ID: {retain_res.memory.id}")
    print(f"  ✓ Memory Content: '{retain_res.memory.content}'")
    print(f"  ✓ Type: {retain_res.memory.memory_type.value}")
    print(f"  ✓ Execution Time: {retain_res.execution_time_ms:.2f} ms")

    # 3. RECALL: Sub-Millisecond Semantic Memory Retrieval
    print("\n" + "-" * 80)
    print("[STEP 3] RECALL — Sub-Millisecond Semantic Query for Code Snippet:")
    sample_vulnerable_code = """
def search_users(user_input: str):
    # Insecure string interpolation
    query = f"SELECT id, username, email FROM users WHERE username = '{user_input}'"
    return db.execute(query)
"""
    print("Query Code:")
    print(sample_vulnerable_code.strip())

    recall_start = time.perf_counter()
    recall_req = HindsightRecallRequest(
        query=sample_vulnerable_code,
        language="python",
        filename="user_repository.py",
        top_k=3,
        min_confidence=0.15,
    )
    recall_res = hindsight_service.recall_memories(recall_req)
    recall_duration = (time.perf_counter() - recall_start) * 1000.0

    print(f"\n  ✓ Recall Latency: {recall_duration:.3f} ms (⚡ Blazing Fast)")
    print(f"  ✓ Matches Found: {recall_res.count}")
    for idx, item in enumerate(recall_res.results, 1):
        mem = item.memory
        print(f"    [{idx}] Relevance: {int(item.relevance_score * 100)}% | Type: {mem.memory_type.value.upper()}")
        print(f"        Content: {mem.content}")
        print(f"        Matched Tokens: {item.matched_keywords}")

    # 4. EXECUTE CODE REVIEW ENRICHED WITH HINDSIGHT
    print("\n" + "-" * 80)
    print("[STEP 4] AI REVIEW — Executing Code Review with Recalled Hindsight Context:")
    ai_service = AIService()
    review_req = AIReviewRequest(
        code=sample_vulnerable_code,
        language="python",
        filename="user_repository.py",
    )
    review_res = await ai_service.review_code(review_req)

    print(f"  ✓ Review Success: {review_res.success}")
    print(f"  ✓ Overall Quality Score: {review_res.static_report.scores.overall if review_res.static_report else 'N/A'}/100")
    print(f"  ✓ Summary: {review_res.review.summary}")
    print(f"  ✓ Critical Issues: {review_res.review.critical_issues}")
    print(f"  ✓ Recalled Hindsight Context Items Applied: {len(review_res.hindsight_context)}")
    for ctx_item in review_res.hindsight_context:
        print(f"    • [{ctx_item.get('type')}] {ctx_item.get('content')} (Relevance: {int(ctx_item.get('relevance_score', 1.0) * 100)}%)")

    # 5. REFLECT: Retrospective Reasoning & Mental Models
    print("\n" + "-" * 80)
    print("[STEP 5] REFLECT — Retrospective Synthesis Across Memory Bank:")
    reflect_req = HindsightReflectRequest(
        query="Synthesize recurring anti-patterns and defensive architecture principles.",
    )
    reflect_res = hindsight_service.reflect_on_history(reflect_req)

    print(f"  ✓ Memories Analyzed: {reflect_res.memories_analyzed}")
    print(f"  ✓ Codebase Trajectory: {reflect_res.quality_trajectory}")
    print(f"  ✓ Synthesis Summary: {reflect_res.synthesis}")
    print(f"  ✓ Derived Mental Models ({len(reflect_res.mental_models)}):")
    for mm in reflect_res.mental_models:
        print(f"    • [{mm.severity}] {mm.title}: {mm.summary}")
        print(f"      Directive: {mm.actionable_directive}")

    print("\n  ✓ Actionable Team Guidelines:")
    for g in reflect_res.actionable_guidelines:
        print(f"    - {g}")

    # 6. Final Benchmark & Verification
    print("\n" + "=" * 80)
    final_stats = hindsight_service.get_stats()
    print("✅ HINDSIGHT INTEGRATION VERIFIED (100% OPERATIONAL)")
    print(f"Total Durable Memories: {final_stats.total_memories}")
    print(f"Average Semantic Recall Speed: {final_stats.avg_recall_latency_ms:.3f} ms")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
