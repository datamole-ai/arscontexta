# Reading notes: Attention Is All You Need (Vaswani et al., 2017)

Quick notes from first pass. Will structure properly later.

## Claims worth capturing

Self-attention replaces recurrence entirely. The architecture has no RNN or CNN
components - just attention and feed-forward layers stacked. This is the core
architectural claim.

Multi-head attention attends to different representation subspaces simultaneously.
Rather than one attention function over d_model dimensions, they run h parallel
attention heads over d_k dimensions each, then concatenate. The idea is that
different heads learn different relationships.

Positional encodings inject sequence order without recurrence. Since there are
no recurrent connections, the model has no inherent notion of position. They add
sinusoidal encodings to the input embeddings. Fixed, not learned (in this paper).

Transformers parallelize better than RNNs during training. RNNs require sequential
computation - position t depends on position t-1. Attention is computed over all
positions simultaneously, so training parallelizes across the sequence length.

## Open questions

Does multi-head attention actually attend to linguistically meaningful relationships,
or is the human-interpretable structure post-hoc? The visualization in the paper
suggests yes but the evidence is thin.

## Method notes

Scaled dot-product attention: softmax(QK^T / sqrt(d_k)) V. The scaling by sqrt(d_k)
prevents the dot products from growing large in high dimensions, which pushes
softmax into low-gradient regions.
