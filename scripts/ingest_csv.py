import os
import sys
import argparse

# Allow running from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.utils.db_insert import insert_from_csv_chunked, insert_all_from_cleaned


def main():
    parser = argparse.ArgumentParser(description="Ingest CSV data into the trips database (chunked)")
    parser.add_argument("csv_path", nargs="?", help="Path to CSV file (omit with --all-cleaned)")
    parser.add_argument("--chunksize", type=int, default=50000, help="Pandas chunksize")
    parser.add_argument("--batch-size", dest="batch_size", type=int, default=1000, help="DB insert batch size")
    parser.add_argument("--all-cleaned", action="store_true", help="Ingest all CSV files under backend/data/cleaned")
    args = parser.parse_args()

    if args.all_cleaned:
        inserted = insert_all_from_cleaned()
        print(f"Inserted {inserted} rows from backend/data/cleaned")
        return

    if not args.csv_path or not os.path.isfile(args.csv_path):
        print("Provide a valid CSV path or use --all-cleaned")
        sys.exit(1)

    inserted = insert_from_csv_chunked(args.csv_path, chunksize=args.chunksize, batch_size=args.batch_size)
    print(f"Inserted {inserted} rows from {args.csv_path}")


if __name__ == "__main__":
    main()
