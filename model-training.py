import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

model_name = "rmihaylov/bert-base-bg"

# Зареждане на токенизатора
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Зареждане на модела
model = AutoModelForMaskedLM.from_pretrained(model_name)

print("Моделът и токенизаторът са заредени успешно!")

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=500)

# Зареждане на данните от текстовия файл
data_path = "corpus/structured_mushroom_dialogs.txt"
with open(data_path, "r", encoding="utf-8") as f:
    raw_data = f.read().split("\n\n" + "="*80 + "\n\n")  # Разделяне на диалозите

# Обработване на текстовите примери и извличане на вход/изход
data = []
for dialog in raw_data:
    lines = dialog.strip().split("\n")
    if len(lines) > 2:
        input_text = "\n".join(lines[:-2])  # Целият диалог
        label_line = lines[-2]
        label = label_line.split("**")[-2].strip()  # Извличане на гъбата
        data.append({"text": input_text, "label": label})

# Преобразуване на етикетите в числа
labels_list = sorted(set(d["label"] for d in data))  # Всички уникални етикети (гъби)
label_to_id = {label: i for i, label in enumerate(labels_list)}

for d in data:
    d["label"] = label_to_id[d["label"]]  # Преобразуване на етикета в индекс

# Създаване на dataset
dataset = Dataset.from_list(data)

# Токенизиране на текста
def tokenize_function(example):
    return tokenizer(example["text"], padding="max_length", truncation=True, max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Разделяне на тренировъчния и тестовия сет
split = tokenized_dataset.train_test_split(test_size=0.2)
train_dataset = split["train"]
eval_dataset = split["test"]

# Определяне на хиперпараметрите
training_args = TrainingArguments(
    output_dir="./bert-mushroom-results",
    num_train_epochs=5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=3e-5,
    weight_decay=0.01,
    evaluation_strategy="steps",
    eval_steps=100,
    logging_steps=50,
    save_steps=200,
    save_total_limit=2,
    load_best_model_at_end=True,
)

# Обучение с Trainer API
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Стартиране на обучението
trainer.train()

# Запазване на модела и токенизатора
model.save_pretrained("./mushroom_bert_model")
tokenizer.save_pretrained("./mushroom_bert_model")