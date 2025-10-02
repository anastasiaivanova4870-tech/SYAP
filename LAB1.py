import pandas as pd
import numpy as np
from pathlib import Path
import concurrent.futures

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

CATEGORIES = ["A", "B", "C", "D"]
NUM_FILES = 5
NUM_ROWS = 100


def generate_csv_files():
    for i in range(NUM_FILES):
        df = pd.DataFrame({
            "Категория": np.random.choice(CATEGORIES, NUM_ROWS),
            "Значение": np.random.uniform(0, 100, NUM_ROWS).round(2)
        })
        df.to_csv(DATA_DIR / f"file_{i+1}.csv", index=False, encoding="utf-8")
    print("CSV файлы сгенерированы.")


def process_file(filename):
    df = pd.read_csv(filename)
    stats = df.groupby("Категория")["Значение"].agg(
        медиана="median",
        отклонение="std"
    )
    return stats


def main():
    generate_csv_files()


    results = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_file, DATA_DIR / f"file_{i+1}.csv") for i in range(NUM_FILES)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())


    combined = pd.concat(results, keys=range(1, NUM_FILES+1), names=["Файл", "Категория"])

    print("\nРезультаты по каждому файлу:")
    print(combined)

    median_of_medians = combined["медиана"].groupby("Категория").median()
    std_of_medians = combined["медиана"].groupby("Категория").std()

    print("\nАгрегированные результаты:")
    final = pd.DataFrame({
        "медиана медиан": median_of_medians,
        "отклонение медиан": std_of_medians
    })
    print(final)


if __name__ == "__main__":
    main()