import evaluate


def evaluate_finetuned_model(model, tokenizer, eval_dataset, max_length=512, num_samples=100):
    """
    Evaluate a fine-tuned model using BLEU and ROUGE metrics.

    Args:
        model: The fine-tuned model.
        tokenizer: Tokenizer for the model.
        eval_dataset: Evaluation dataset.
        max_length (int): Maximum length for generation.
        num_samples (int): Number of samples to evaluate.

    Returns:
        dict: Evaluation results (BLEU and ROUGE scores).
    """
    bleu_metric = evaluate.load("bleu")
    rouge_metric = evaluate.load("rouge")

    references = []
    predictions = []

    for i in range(min(num_samples, len(eval_dataset))):
        input_text = eval_dataset[i]["text"]
        references.append([input_text.split()])

        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=max_length)
        outputs = model.generate(**inputs, max_length=max_length, num_return_sequences=1)
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        predictions.append(generated_text.split())

    bleu_score = bleu_metric.compute(predictions=predictions, references=references)
    rouge_score = rouge_metric.compute(predictions=[" ".join(pred) for pred in predictions],
                                       references=[" ".join(ref[0]) for ref in references])

    print(f"BLEU Score: {bleu_score['bleu']}")
    print(f"ROUGE Score: {rouge_score}")

    return {"BLEU": bleu_score, "ROUGE": rouge_score}

