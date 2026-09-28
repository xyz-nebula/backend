from app.api.v1.routers.models import AIEvaluationResult

EVIDENCE = {"is_ai": True, "quote": "q", "message_index": 1}


def _verdict(college: str) -> dict:
    return {
        "status": "ready",
        "college": college,
        "verdict": {
            "college": college,
            "choice": "opponent",
            "decisive_criterion": "c",
            "evidence": EVIDENCE,
            "observation": "o",
            "effect": "e",
            "comparison": "cmp",
        },
        "error_code": None,
    }


def _payload(judge_verdicts: list[dict], trainer_feedback: dict) -> dict:
    return {
        "contract_version": "2.0.0-rc.1",
        "outcome": {
            "basis": "dialogue_inference",
            "status": "ready",
            "assessment": {
                "kind": "partial_agreement",
                "summary": "s",
                "agreed_terms": ["a"],
                "open_points": ["p"],
                "next_step": None,
                "evidence": [EVIDENCE],
            },
            "error_code": None,
        },
        "judge_verdicts": judge_verdicts,
        "trainer_feedback": trainer_feedback,
    }


def test_result_with_ready_judges_and_feedback_validates():
    point = {"action": "a", "evidence": EVIDENCE, "situation_change": "s", "consequence": "c"}
    feedback = {
        "status": "ready",
        "feedback": {
            "summary": "s",
            "strengths": [point],
            "mistakes": [],
            "missed_opportunities": [point],
            "next_try": ["n"],
            "plan_vs_reality": None,
            "goal_assessment": {
                "status": "not_achieved",
                "goal_text": None,
                "explanation": "e",
                "evidence": [EVIDENCE],
            },
        },
        "error_code": None,
    }
    payload = _payload([_verdict(c) for c in ("hiring", "negotiation", "ownership")], feedback)

    result = AIEvaluationResult.model_validate(payload)

    assert [slot.college for slot in result.judge_verdicts] == [
        "hiring",
        "negotiation",
        "ownership",
    ]


def test_result_with_failed_judges_and_feedback_validates():
    failed = [
        {"status": "failed", "college": c, "verdict": None, "error_code": "invalid_judge_output"}
        for c in ("hiring", "negotiation", "ownership")
    ]
    feedback = {"status": "failed", "feedback": None, "error_code": "invalid_trainer_output"}

    result = AIEvaluationResult.model_validate(_payload(failed, feedback))

    assert all(slot.status == "failed" for slot in result.judge_verdicts)
