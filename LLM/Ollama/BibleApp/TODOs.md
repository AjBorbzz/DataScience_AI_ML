### Lock the evaluation gate (final tuning loop)
#### Expand eval to ≥50 questions
* Categories balanced (≥5 each): money, anxiety, forgiveness, work, guidance, anger, relationships, suffering, speech, generosity.
* Keep questions realistic and varied phrasing.

### Run eval and freeze config
#### Freeze these once metrics pass:
* embedding model
* hybrid retrieval params (top_k_vec, top_k_bm25)
* max_passages
* temperature
### Save a run config JSON with a hash.