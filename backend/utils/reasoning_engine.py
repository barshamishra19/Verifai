def generate_reasoning(spatial, temporal, forensic, metadata):
    evidence = []
    if spatial > 0.7:
        evidence.append({"type": "Spatial", "explanation": "Detected distortions in skin texture/hand geometry."})
    if temporal > 0.7:
        evidence.append({"type": "Temporal", "explanation": "Movement is unnaturally smooth (Characteristic of AI)."})
    if forensic > 0.6:
        evidence.append({"type": "Forensic", "explanation": "Frequency domain spikes match GAN/Diffusion fingerprints."})
    return evidence