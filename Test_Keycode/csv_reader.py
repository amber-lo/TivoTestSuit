import csv

def csv_reader(csv_file):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
    return data

def csv_writer(csv_file, result):
    fieldnames = result[1].keys()
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)
    print(f"Save test keycode result to {csv_file}, Done!")

