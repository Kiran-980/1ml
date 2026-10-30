# generative

## Generative models, LLMs, and RAG

**Documented:** The original RAG architecture combines a generator with retrieved external memory, enabling knowledge-intensive generation. Its published improvements do not establish factual correctness for every later application. [RAG paper](https://arxiv.org/abs/2005.11401)

**Decision synthesis:** Choose retrieval when the answer depends on versioned external evidence; compare direct retrieval/extractive answers and prompting before adding training. Fine-tuning targets learned behavior or task specialization, but does not replace permissions, evidence freshness or evaluation. Version corpus, index, chunker, embedding model, prompt, generator and generation settings as one system. Apply document access controls before retrieval, keep retrieved content untrusted, and test unavailable evidence, conflicting documents, prompt injection, citation support and abstention.

**Documented:** RAG evaluation has separate retrieval-relevance, context-faithfulness and generation-quality dimensions; automated reference-free metrics are one proposed approach. [Ragas paper](https://arxiv.org/abs/2309.15217)

**Decision synthesis:** Use a representative, held-out question set with expected evidence or human rubrics. Measure retrieval recall, answer correctness, citation support, groundedness, safety, latency and cost separately; diagnose retrieval versus generation failures. Calibrate automated judges against blinded human judgments and inspect judge bias. Never treat a high judge score or plausible citation as proof. If tool use is involved, test action correctness and permissions separately from answer quality.
