from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class AriaBrain:
    def __init__(self, model_id="microsoft/phi-2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            load_in_8bit=True
        )

    def respond(self, prompt):
        input_ids = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        output = self.model.generate(
            **input_ids,
            max_new_tokens=100,
            temperature=0.8,
            top_p=0.95
        )
        return self.tokenizer.decode(output[0], skip_special_tokens=True)