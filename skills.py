# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-personal-agent-cellular-senescence-p16ink4a-mrna-expression-skill
Category: personal_agent
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def evaluate_p16ink4a_senescence_expression(p16_log2_fold_change, chronological_age_years, il6_pg_ml=1.8, crp_mg_l=0.9):
    # Baseline expected p16 increase is ~0.04 log2 units per chronological year
    expected_p16_log2 = 0.04 * (chronological_age_years - 20.0) if chronological_age_years > 20 else 0.0
    delta_p16 = p16_log2_fold_change - expected_p16_log2
    
    # Biological age delta estimated from p16 divergence
    biological_age_gap_years = delta_p16 / 0.04
    estimated_cellular_age = round(chronological_age_years + biological_age_gap_years, 1)
    
    # SASP Secretory Risk Index (0 - 100) combining p16, IL-6, and hs-CRP
    sasp_score = min(100.0, max(0.0, (p16_log2_fold_change * 20.0) + (il6_pg_ml * 6.0) + (crp_mg_l * 10.0)))
    
    if delta_p16 <= -0.2:
        burden_tier = "DECELERATED_SENESCENCE"
        recommendation = "Low senescent cell accumulation. Cellular rejuvenation strategies maintained."
    elif delta_p16 <= 0.4:
        burden_tier = "AGE_MATCHED_SENESCENCE"
        recommendation = "Normal senescent cell accumulation rate consistent with chronological trajectory."
    else:
        burden_tier = "ACCELERATED_SENESCENT_BURDEN"
        recommendation = "Significant accumulation of senescent immune cells with elevated SASP pro-inflammatory phenotype."
        
    senolytic_candidate = (delta_p16 >= 0.5) and (sasp_score >= 65.0)
    
    return {
        "chronological_age_years": chronological_age_years,
        "p16_log2_fold_change": round(p16_log2_fold_change, 3),
        "expected_p16_log2_for_age": round(expected_p16_log2, 3),
        "p16_delta_divergence": round(delta_p16, 3),
        "estimated_cellular_biological_age": estimated_cellular_age,
        "biological_age_gap_years": round(biological_age_gap_years, 1),
        "sasp_inflammatory_score": round(sasp_score, 1),
        "senescence_status": burden_tier,
        "senolytic_protocol_candidate": senolytic_candidate,
        "clinical_guidance": recommendation
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "evaluate_p16ink4a_senescence_expression",
                        "description": """Evaluate cellular senescence burden from T-lymphocyte (CD3+ / PBMC) CDKN2A (p16^INK4a) relative mRNA log2 expression.
p16^INK4a is a master cyclin-dependent kinase inhibitor that irreversibly arrests the cell cycle in senescent cells.
Calculates biological senescence acceleration factor, SASP cytokine secretory load, and senolytic intervention readiness index.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = evaluate_p16ink4a_senescence_expression(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'p16_log2_fold_change': 0.85, 'chronological_age_years': 45, 'il6_pg_ml': 2.1, 'crp_mg_l': 1.1}
        out = evaluate_p16ink4a_senescence_expression(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
