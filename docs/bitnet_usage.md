# BitNet Inference Guide

## 🧠 Basic Usage

Run a basic inference prompt using the quantized BitNet model:

```bash
python run_inference.py \
  -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  -p "You are a helpful assistant" \
  -cnv
```

---

## 🔧 Full Argument Reference

| Argument             | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `-m`, `--model`       | Path to the `.gguf` model file                                               |
| `-p`, `--prompt`      | The **prompt** or system message to start with                              |
| `-n`, `--n-predict`   | Number of tokens to predict (default depends on implementation)             |
| `-t`, `--threads`     | Number of CPU threads to use                                                |
| `-c`, `--ctx-size`    | Context window size (token history length)                                  |
| `-temp`, `--temperature` | Temperature to control randomness (e.g. 0.7 = conservative, 1.2 = creative) |
| `-cnv`, `--conversation` | **Chat mode** — interprets prompt as a system prompt for multi-turn use    |

---

## 🧪 Example with Custom Settings

```bash
python run_inference.py \
  -m models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf \
  -p "Write a haiku about neural networks." \
  -n 100 \
  -t 8 \
  -c 2048 \
  -temp 0.8 \
  -cnv
```
