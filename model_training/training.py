from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split

def fine_tune_llm(texts, model_name="gpt2", output_dir="./finetuned_model", epochs=3, eval_split=0.2):
    """
    Fine-tune a generative language model on preprocessed texts.

    :param texts: List of preprocessed texts
    :param model_name: Pre-trained model name
    :param output_dir: Directory to save the fine-tuned model
    :param epochs: Number of training epochs
    :param eval_split: Fraction of the dataset to use for evaluation
    """
    # Split dataset into training and evaluation datasets
    texts_train, texts_eval = train_test_split(texts, test_size=eval_split, random_state=42)

    # Ensure evaluation set is not empty
    if not texts_eval:
        raise ValueError("Evaluation dataset is empty. Adjust `eval_split` or check input data.")

    # Convert texts into Hugging Face datasets
    train_dataset = Dataset.from_dict({"text": texts_train})
    eval_dataset = Dataset.from_dict({"text": texts_eval})

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Ensure the tokenizer has a padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token  # Use eos_token as pad_token

    # Tokenize datasets
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)

    tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
    tokenized_eval_dataset = eval_dataset.map(tokenize_function, batched=True)

    # Ensure tokenized datasets are not empty
    if len(tokenized_eval_dataset) == 0:
        raise ValueError("Tokenized evaluation dataset is empty. Check the tokenization process.")

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
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_eval_dataset,  # Provide eval dataset here
    )

    # Fine-tune the model
    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
