import pandas as pd
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from typing import TypedDict, Optional, Callable
import os
from dotenv import load_dotenv
load_dotenv()

class ClaimState(TypedDict):
    claim: dict
    policy_check: str
    fraud_score: float
    evidence: str
    decision: str
    trace: list


groq_api = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=groq_api,
    temperature=0
)


policy_text = os.getenv("POLICY_TEXT", "")
try:
    from langchain_community.document_loaders import PyPDFLoader
    pdf_path = os.path.join(os.path.dirname(__file__), "data", "AutoDrive_Warranty_Policy_2025.pdf")
    if os.path.exists(pdf_path):
        try:
            loader = PyPDFLoader(pdf_path)
            policy_docs = loader.load()
            policy_text = " ".join([doc.page_content for doc in policy_docs])
        except Exception:
            policy_text = policy_text or "Your policy text here."
    else:
        policy_text = policy_text or "Your policy text here."
except Exception:
    policy_text = policy_text or "Your policy text here."


def policy_check_agent(state: ClaimState) -> ClaimState:
    claim = state["claim"]
    vtype = "Four-Wheeler" if "Four-Wheeler" in claim["model"] else "Two-Wheeler"
    
    prompt = f"""
    You are a warranty compliance officer. 
    Policy manual:
    {policy_text}
    
    Vehicle type: {vtype}
    Claim details: {claim}
    
    Based on warranty days, mileage, and covered parts,
    is this claim covered under the policy? 
    Answer with: "Covered by policy" or "Not covered by policy".
    """
    
    response = llm.invoke(prompt)
    res_text = response.content.strip()
    state.setdefault("trace", []).append({
        "agent": "policy_check_agent",
        "prompt": prompt,
        "response": res_text,
    })
    state["policy_check"] = res_text
    return state


def fraud_scoring_agent(state: ClaimState) -> ClaimState:
    claim = state["claim"]
    prompt = f"""
    You are a fraud detection expert.
    Policy manual:
    {policy_text}
    
    Claim details:
    {claim}
    Policy validation: {state['policy_check']}
    
    Analyze whether this claim looks fraudulent.
    Return ONLY a number between 0 and 1 (fraud likelihood score).
    """
    response = llm.invoke(prompt)
    res_text = response.content.strip()
    try:
        score = float(res_text)
    except:
        score = 0.5
    state.setdefault("trace", []).append({
        "agent": "fraud_scoring_agent",
        "prompt": prompt,
        "response": res_text,
    })
    state["fraud_score"] = score
    return state


def evidence_collector_agent(state: ClaimState) -> ClaimState:
    claim = state["claim"]
    prompt = f"""
    You are tasked with collecting evidence for claim review.
    Policy manual:
    {policy_text}
    
    Claim details:
    {claim}
    Fraud score: {state['fraud_score']}
    
    Compare claim against the policy manual and fraud indicators.
    List any red flags or violations found. If none, say "No issues".
    """
    response = llm.invoke(prompt)
    res_text = response.content.strip()
    state.setdefault("trace", []).append({
        "agent": "evidence_collector_agent",
        "prompt": prompt,
        "response": res_text,
    })
    state["evidence"] = res_text
    return state


def action_agent(state: ClaimState) -> ClaimState:
    claim = state.get("claim", {})
    policy_check = state.get("policy_check", "")
    fraud_score = state.get("fraud_score", 0.0)
    evidence = state.get("evidence", "")

    prompt = f"""
    You are a warranty adjudicator. Given the following information about a warranty claim, choose one of three actions: "Approve claim", "Reject claim", or "Escalate to HITL" (human-in-the-loop for manual review).

    Provide your answer as a single decision on the first line, and then a short (1-2 sentence) justification on the following line.

    Policy manual (for reference):
    {policy_text}

    Claim details: {claim}

    Policy check result: {policy_check}
    Fraud score (0-1): {fraud_score}
    Evidence / red flags found: {evidence}

    Important: If the policy_check indicates the claim is "Not covered by policy" or the evidence highlights a direct policy violation (e.g., part not covered), prefer "Reject claim" unless strong justification exists to approve. If the evidence is ambiguous, but fraud score is moderately high (>0.5), choose "Escalate to HITL".
    """

    decision_text = ""
    try:
        response = llm.invoke(prompt)
        res_text = response.content.strip()
        first_line = res_text.splitlines()[0].strip()
        normalized = first_line.lower()
        if "approve" in normalized:
            decision_text = "Approve claim"
        elif "reject" in normalized:
            decision_text = "Reject claim"
        elif "escalate" in normalized or "hitl" in normalized or "human" in normalized:
            decision_text = "Escalate to HITL"
        else:
            decision_text = ""

        state.setdefault("trace", []).append({
            "agent": "action_agent",
            "prompt": prompt,
            "response": res_text,
        })
    except Exception:
        res_text = ""

    if not decision_text:
        if policy_check == "Not covered by policy":
            decision_text = "Reject claim"
        elif fraud_score > 0.5:
            decision_text = "Escalate to HITL"
        else:
            decision_text = "Approve claim"

        state.setdefault("trace", []).append({
            "agent": "action_agent",
            "prompt": "(rule-based fallback)",
            "response": decision_text,
        })

    state["decision"] = decision_text
    return state


def process_claims(claims_df: pd.DataFrame, progress_callback: Optional[Callable[[int, int], None]] = None) -> pd.DataFrame:
    results = []
    total = len(claims_df)
    for i, (_, claim_row) in enumerate(claims_df.iterrows(), start=1):
        claim_dict = claim_row.to_dict()
        state = ClaimState(claim=claim_dict, policy_check="", fraud_score=0.0, evidence="", decision="")
        state = policy_check_agent(state)
        state = fraud_scoring_agent(state)
        state = evidence_collector_agent(state)
        state = action_agent(state)

        flat = dict(claim_dict)
        flat.update({
            "policy_check": state.get("policy_check", ""),
            "fraud_score": state.get("fraud_score", 0.0),
            "evidence": state.get("evidence", ""),
            "decision": state.get("decision", ""),
            "agent_trace": state.get("trace", []),
        })
        results.append(flat)

        if progress_callback:
            try:
                progress_callback(i, total)
            except Exception:
                pass

    return pd.DataFrame(results)