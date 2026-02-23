#!/usr/bin/env python3
"""BlackRoad AI Model Optimizer — quantization + benchmarking utilities."""
import json, time, os

def benchmark_model(model_name: str, prompt: str = "Hello!", runs: int = 5) -> dict:
    """Benchmark an Ollama model for tokens/sec."""
    import urllib.request, urllib.parse
    results = []
    for i in range(runs):
        payload = json.dumps({"model": model_name, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request("http://localhost:11434/api/generate", data=payload,
            headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
                elapsed = time.time() - t0
                tok = data.get("eval_count", 0)
                results.append({"run": i+1, "tokens": tok, "elapsed_s": round(elapsed, 2),
                                 "tokens_per_sec": round(tok/elapsed, 1) if elapsed > 0 else 0})
        except Exception as e:
            results.append({"run": i+1, "error": str(e)})
    avg_tps = sum(r.get("tokens_per_sec",0) for r in results) / len(results)
    return {"model": model_name, "avg_tokens_per_sec": round(avg_tps, 1), "runs": results}

if __name__ == "__main__":
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:7b"
    print(f"Benchmarking {model}...")
    result = benchmark_model(model)
    print(json.dumps(result, indent=2))

