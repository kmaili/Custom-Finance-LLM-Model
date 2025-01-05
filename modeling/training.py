from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
import torch


def __split_text_into_chunks(text, tokenizer, max_length=512):
    """
    Split input text into chunks of specified maximum length using the provided tokenizer.

    Args:
        text (str or List[str]): Input text to be split into chunks
        tokenizer: HuggingFace tokenizer instance
        max_length (int): Maximum length of each chunk in tokens (default: 512)

    Returns:
        list: List of decoded text chunks
    """
    if isinstance(text, str):
        text = [text]

    all_chunks = []
    for text_item in text:
        tokens = tokenizer(text_item, return_tensors="pt", truncation=False, add_special_tokens=False)["input_ids"][0]
        chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]
        decoded_chunks = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]
        all_chunks.extend(decoded_chunks)

    return all_chunks


def fine_tune_llm(text, model_name="gpt2", output_dir="./finetuned_model", epochs=3, eval_split=0.2):
    """
    Fine-tune a pre-trained language model on custom text data without evaluation.

    Args:
        text (str or List[str]): Training text data - can be either a single string or a list of strings
        model_name (str): Name of the pre-trained model to fine-tune (default: "gpt2")
        output_dir (str): Directory to save the fine-tuned model (default: "./finetuned_model")
        epochs (int): Number of training epochs (default: 3)
        eval_split (float): Fraction of data to use for evaluation split (default: 0.2)
    """
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    text_chunks = __split_text_into_chunks(text, tokenizer, max_length=512)
    texts_train, _ = train_test_split(text_chunks, test_size=eval_split, random_state=42)

    train_dataset = Dataset.from_dict({"text": texts_train})

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.pad_token_id

    def tokenize_function(examples):
        """
        Tokenize text examples with padding and truncation.
        Also prepare labels for language modeling.
        """
        tokenized = tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=512
        )
        tokenized["input_ids"] = torch.tensor(tokenized["input_ids"])
        tokenized["attention_mask"] = torch.tensor(tokenized["attention_mask"])
        tokenized["labels"] = tokenized["input_ids"].clone()

        return tokenized

    tokenized_train_dataset = train_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=train_dataset.column_names
    )

    training_args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="no",  # Evaluation disabled
        save_strategy="steps",
        save_steps=500,
        learning_rate=5e-5,
        per_device_train_batch_size=8,
        num_train_epochs=epochs,
        save_total_limit=2,
        report_to="none",  # Disable wandb logging
        logging_steps=100,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train_dataset,
    )

    trainer.train()

    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    return model, tokenizer
