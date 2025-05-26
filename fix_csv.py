import csv

file_path = "StudentDetails/StudentDetails.csv"
clean_path = "StudentDetails/StudentDetails_clean.csv"
expected_fields = 11  # Change this if your file has a different number of columns

with open(file_path, "r", encoding="utf-8") as infile, open(clean_path, "w", newline='', encoding="utf-8") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    for i, row in enumerate(reader, start=1):
        if len(row) == expected_fields:
            writer.writerow(row)
        else:
            print(f"Skipped line {i} with {len(row)} fields: {row}")
