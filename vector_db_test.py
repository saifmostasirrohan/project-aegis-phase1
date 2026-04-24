import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. The 20-Sentence Agronomy Corpus
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
    "Capillary action in fine-textured clay loam facilitates upward water movement, potentially bringing subsurface salts into the active rooting profile."
]

print("1. Loading model and embedding corpus...")
model = SentenceTransformer('all-MiniLM-L6-v2')
corpus_embeddings = model.encode(agronomy_corpus)

# 2. Initialize the FAISS Index
# all-MiniLM-L6-v2 outputs a 384-dimensional vector. FAISS needs to know this upfront to allocate memory.
dimension = 384
print(f"2. Creating FAISS IndexFlatL2 with dimension {dimension}...")

# 3. Create the FAISS IVF Index (Approximate Search)
nlist = 4  # Divide our data into 4 clusters (Voronoi cells)

print(f"3. Creating FAISS IndexIVFFlat with {nlist} clusters...")
# The quantizer is a basic flat index used just to assign vectors to the correct cluster
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)

# CRITICAL STEP: An IVF index must be trained on your data BEFORE you add it,
# so it can learn where to place the 4 cluster centers.
print("Training the index...")
index.train(corpus_embeddings)

# 4. Add the embeddings to the trained index
index.add(corpus_embeddings)
print(f"4. Total vectors loaded into FAISS: {index.ntotal}")

# 5. Perform the Search
query = "How do I fix aluminum toxicity in low pH dirt?"
print(f"\nSearching for: '{query}'")
query_embedding = model.encode([query])

# nprobe controls how many clusters we search.
# We have 4 clusters total. Setting nprobe=2 means we search the 2 closest clusters.
# Higher nprobe = more accurate but slower.
index.nprobe = 2

k = 3
distances, indices = index.search(query_embedding, k)

print("\n--- FAISS IVF SEARCH RESULTS ---")
for i in range(k):
    match_idx = indices[0][i]
    distance = distances[0][i]
    sentence = agronomy_corpus[match_idx]
    print(f"Rank {i+1} | L2 Score: {distance:.4f} | {sentence}")

# 6. Persistence: Save the database to disk
file_name = "agronomy_faiss.index"
faiss.write_index(index, file_name)
print(f"\nDatabase saved to disk as '{file_name}'")

# Prove that it saved successfully by loading it back into a new variable
loaded_index = faiss.read_index(file_name)
print(f"Successfully loaded database from disk. Vectors inside: {loaded_index.ntotal}")