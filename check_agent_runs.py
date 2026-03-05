"""检查 Agent 调用记录"""

from openclaw_studio.database import CaseDatabase

db = CaseDatabase()
runs = db.get_agent_runs('case-eca55ddc')

print(f"Agent runs: {len(runs)}\n")
for r in runs:
    print(f"  - {r.agent_type}: {r.status} ({r.model})")
    print(f"    Time: {r.created_at}")

db.close()
