from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer


def fine_tune_llm(texts, model_name="gpt2", output_dir="./finetuned_model", epochs=3):
    """
    Fine-tune a generative language model on preprocessed texts.

    :param texts: List of preprocessed texts
    :param model_name: Pre-trained model name
    :param output_dir: Directory to save the fine-tuned model
    :param epochs: Number of training epochs
    """
    # Convert texts into a Hugging Face dataset
    dataset = Dataset.from_dict({"text": texts})

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Tokenize dataset
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=5e-5,
        per_device_train_batch_size=8,
        num_train_epochs=epochs,
        save_steps=10_000,
        save_total_limit=2,
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    # Fine-tune the model
    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
