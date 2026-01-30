"""
Enhanced reasoning engine for generating detailed, frame-grounded evidence
"""
from typing import List, Dict

def generate_reasoning(spatial: float, temporal: float, forensic: float, metadata: float) -> List[Dict]:
    """
    Generate ranked evidence based on detection scores
    
    Args:
        spatial: Spatial artifact score (0-1)
        temporal: Temporal consistency score (0-1)
        forensic: Forensic analysis score (0-1)
        metadata: Metadata analysis score (0-1)
    
    Returns:
        List of evidence dictionaries, ranked by confidence
    """
    evidence_list = []
    
    # 1. Spatial Artifacts (Threshold: 0.75 - increased from 0.5)
    if spatial > 0.75:
        severity = "high" if spatial > 0.9 else "medium"
        evidence_list.append({
            "rank": 0,
            "type": "Spatial Artifacts",
            "confidence": round(spatial, 3),
            "severity": severity,
            "explanation": f"Detected significant spatial anomalies (score: {spatial:.2f}). "
                          f"This includes distortions in skin texture or facial inconsistencies.",
            "technical_details": "CNN-based spatial artifact detection"
        })
    
    # 2. Temporal Smoothness (Threshold: 0.78 - increased from 0.75)
    if temporal > 0.78:
        severity = "high" if temporal > 0.9 else "medium"
        evidence_list.append({
            "rank": 0,
            "type": "Temporal Inconsistency",
            "confidence": round(temporal, 3),
            "severity": severity,
            "explanation": f"Motion patterns exhibit unnatural smoothness (score: {temporal:.2f}). "
                          f"Real videos typically have natural jitter, while AI is often overly smooth.",
            "technical_details": "Optical flow variance analysis"
        })
    
    # 3. Forensic Analysis (Threshold: 0.70 - adjusted from 0.75)
    if forensic > 0.70:
        severity = "high" if forensic > 0.85 else "medium"
        evidence_list.append({
            "rank": 0,
            "type": "Forensic Frequency Anomalies",
            "confidence": round(forensic, 3),
            "severity": severity,
            "explanation": f"Frequency analysis reveals patterns (score: {forensic:.2f}) "
                          f"consistent with AI generation. These high-frequency artifacts "
                          f"are rarely seen in authentic cameras.",
            "technical_details": "FFT-based frequency analysis"
        })
    
    # 4. Metadata Analysis (Threshold: 0.8)
    if metadata > 0.8:
        evidence_list.append({
            "rank": 0,
            "type": "Metadata Inconsistencies",
            "confidence": round(metadata, 3),
            "severity": "medium",
            "explanation": f"Video metadata shows anomalies (score: {metadata:.2f}) typical of AI tools.",
            "technical_details": "EXIF and codec metadata analysis"
        })
    
    # 5. Combined High Confidence
    high_scores = sum([spatial > 0.75, temporal > 0.8, forensic > 0.8, metadata > 0.8])
    if high_scores >= 2:
        avg_high = sum([s for s in [spatial, temporal, forensic, metadata] if s > 0.7]) / max(high_scores, 1)
        evidence_list.append({
            "rank": 0,
            "type": "Multi-Engine Consensus",
            "confidence": round(avg_high, 3),
            "severity": "high",
            "explanation": f"Multiple detection engines flagged this video as AI-generated.",
            "technical_details": "Ensemble agreement"
        })
    
    # 6. Authenticity Indicators (When scores are low)
    if all(s < 0.65 for s in [spatial, temporal, forensic, metadata]):
        avg_low = (spatial + temporal + forensic + metadata) / 4
        evidence_list.append({
            "rank": 0,
            "type": "Natural Motion Patterns",
            "confidence": round(1 - temporal, 3),
            "severity": "low",
            "explanation": "Motion jitter and micro-movements are consistent with a real camera sensor.",
            "technical_details": "Natural temporal variance"
        })
        evidence_list.append({
            "rank": 0,
            "type": "Sensor Noise Integrity",
            "confidence": round(1 - forensic, 3),
            "severity": "low",
            "explanation": "No structured frequency artifacts detected. The sensor noise appears consistent with organic footage.",
            "technical_details": "Spectral domain consistency"
        })
    
    # Sort by confidence (descending) and assign ranks
    evidence_list.sort(key=lambda x: x['confidence'], reverse=True)
    for i, evidence in enumerate(evidence_list):
        evidence['rank'] = i + 1
    
    # Return top 5 most confident pieces of evidence
    return evidence_list[:5]


def generate_detailed_report(spatial: float, temporal: float, forensic: float, 
                            metadata: float, final_score: float, 
                            classification: str) -> Dict:
    """
    Generate a comprehensive analysis report
    
    Returns:
        Detailed report dictionary with summary, evidence, and recommendations
    """
    evidence = generate_reasoning(spatial, temporal, forensic, metadata)
    
    # Confidence level
    if final_score > 0.8 or final_score < 0.2:
        confidence_level = "Very High"
    elif final_score > 0.65 or final_score < 0.35:
        confidence_level = "High"
    elif final_score > 0.55 or final_score < 0.45:
        confidence_level = "Moderate"
    else:
        confidence_level = "Low (Uncertain)"
    
    # Summary
    if classification == "AI-Generated":
        summary = f"This video is classified as AI-Generated with {final_score*100:.1f}% confidence. "
        summary += f"Analysis confidence: {confidence_level}. "
        if final_score > 0.8:
            summary += "Strong indicators across multiple detection methods."
        elif final_score > 0.65:
            summary += "Multiple detection methods flagged this content."
        else:
            summary += "Some AI characteristics detected, but results are uncertain."
    else:
        summary = f"This video is classified as Real with {(1-final_score)*100:.1f}% confidence. "
        summary += f"Analysis confidence: {confidence_level}. "
        if final_score < 0.2:
            summary += "Strong indicators of authentic footage."
        elif final_score < 0.35:
            summary += "Most detection methods indicate real content."
        else:
            summary += "Appears real, but some anomalies detected."
    
    return {
        "summary": summary,
        "confidence_level": confidence_level,
        "evidence": evidence,
        "engine_breakdown": {
            "spatial": {
                "score": round(spatial, 3),
                "weight": 0.30,
                "contribution": round(spatial * 0.30, 3)
            },
            "temporal": {
                "score": round(temporal, 3),
                "weight": 0.35,
                "contribution": round(temporal * 0.35, 3)
            },
            "forensic": {
                "score": round(forensic, 3),
                "weight": 0.25,
                "contribution": round(forensic * 0.25, 3)
            },
            "metadata": {
                "score": round(metadata, 3),
                "weight": 0.10,
                "contribution": round(metadata * 0.10, 3)
            }
        }
    }