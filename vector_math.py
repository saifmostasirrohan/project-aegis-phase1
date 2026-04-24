import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Module-level resources (shared by main and search)
# ---------------------------------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

agronomy_corpus = [
    "Infection by Puccinia striiformis causes yellow rust in wheat, characterized by linear chlorotic lesions on adult leaves.",
    "Early blight in tomatoes, caused by Alternaria solani, presents as concentric necrotic rings on lower foliage.",
    "Application of systemic triazole fungicides is recommended to halt mycelial growth during the incubation period of soybean rust.",
    "Fusarium head blight not only reduces grain yield but also contaminates wheat with deoxynivalenol mycotoxins.",
    "Bacterial leaf streak in corn, caused by Xanthomonas vasicola, thrives in high humidity and prolonged canopy wetness.",
    "Acidic soils with a pH below 5.5 frequently exhibit aluminum toxicity, which severely stunts root elongation in sensitive cultivars.",
    "To ameliorate subsoil acidity, surface application of fine agricultural limestone requires physical incorporation to expedite neutralization.",
    "Phosphorus bioavailability is highly pH-dependent, often precipitating with calcium in alkaline soils and with iron in acidic soils.",
    "Cation exchange capacity dictates the soil's ability to retain nutrient cations like potassium, magnesium, and calcium against leaching.",
    "Excessive application of anhydrous ammonia can temporarily spike soil pH, followed by a long-term acidifying effect due to nitrification.",
    "Misadjustment of the combine harvester's concave clearance and rotor speed directly correlates with increased grain cracking and dockage.",
    "Modern combine headers utilize automatic terrain contouring sensors to maintain optimal cutting height across undulating topography.",
    "Telematics systems on agricultural tractors stream real-time CAN bus data, allowing for predictive maintenance of the diesel powertrain.",
    "Cleaning shoe overload in a rotary combine often results from an excessive volume of material other than grain entering the sieve.",
    "Proper calibration of the yield monitor's mass flow sensor is critical for generating accurate spatial harvest data maps.",
    "Subsurface drip irrigation significantly reduces evaporative water loss and allows for precise fertigation directly to the root zone.",
    "Center pivot irrigation systems equipped with variable rate nozzles can optimize water application based on soil moisture zoning.",
    "Evapotranspiration models combined with soil moisture probes provide the data necessary to trigger precision irrigation scheduling.",
    "Salinity buildup in the root zone is a common consequence of utilizing brackish irrigation water without an adequate leaching fraction.",
    "Capillary action in fine-textured clay loam facilitates upward water movement, potentially bringing subsurface salts into the active rooting profile.",
]

corpus_embeddings = model.encode(agronomy_corpus, convert_to_numpy=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cosine_similarity_manual(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity manually: dot(vec1, vec2) / (||vec1|| * ||vec2||)."""
    dot_product = float(np.dot(vec1, vec2))
    norm_product = float(np.linalg.norm(vec1) * np.linalg.norm(vec2))
    if norm_product == 0.0:
        raise ValueError("Cannot compute cosine similarity with a zero vector.")
    return dot_product / norm_product


# ---------------------------------------------------------------------------
# Task 3 – Search Function
# ---------------------------------------------------------------------------

def search(query_string, threshold=0.3):
    # Step A: Embed the query_string into a vector.
    query_embedding = model.encode([query_string], convert_to_numpy=True)[0]

    # Step B: Calculate cosine similarity using pure numpy.
    # Formula: dot(query, corpus_vectors) / (norm(query) * norms(corpus_vectors))
    dot_products = np.dot(corpus_embeddings, query_embedding)
    norm_query = np.linalg.norm(query_embedding)
    norm_corpus = np.linalg.norm(corpus_embeddings, axis=1)
    scores = dot_products / (norm_query * norm_corpus)

    # Step C: Get the indices of the top 3 highest scores.
    top_indices = np.argsort(scores)[::-1][:3]

    # Step D: Check the threshold.
    if scores[top_indices[0]] < threshold:
        print("No relevant agricultural context found.")
        return

    # Step E: Loop through top 3 and print score + matching sentence.
    for idx in top_indices:
        print(f"Score: {round(float(scores[idx]), 3)} | {agronomy_corpus[idx]}")


# ---------------------------------------------------------------------------
# Task 2 – Gate Constraint Proof
# ---------------------------------------------------------------------------

def main() -> None:
    sentence_a = "The corn crop requires heavy nitrogen fertilization for optimal yield."
    sentence_b = "Applying urea supplements will significantly improve maize growth."
    sentence_c = "The diesel engine on the John Deere tractor needs an oil change."

    embeddings = model.encode([sentence_a, sentence_b, sentence_c], convert_to_numpy=True)
    emb_a, emb_b, emb_c = embeddings

    sim_a_b = cosine_similarity_manual(emb_a, emb_b)
    sim_a_c = cosine_similarity_manual(emb_a, emb_c)

    print("Manual cosine similarity results:")
    print(f"A vs B: {sim_a_b:.4f}")
    print(f"A vs C: {sim_a_c:.4f}")
    print(f"Corpus embeddings shape: {corpus_embeddings.shape}")

    print("\nInterpretation:")
    if sim_a_b > sim_a_c:
        print("A and B are more semantically related than A and C.")
    else:
        print("Unexpected result: A and B are not more related than A and C.")


if __name__ == "__main__":
    main()

print("\n--- TEST 5: Polysemy (Manufacturing) ---")
search("The new manufacturing plant was shut down due to a power outage.", threshold=0.0)

print("\n--- TEST 6: Polysemy (Finance) ---")
search("The bond yield dropped significantly after the financial announcement.", threshold=0.0)
