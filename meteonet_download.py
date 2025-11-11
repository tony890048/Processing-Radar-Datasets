import os
import argparse
import requests
import tarfile
from tqdm import tqdm

def download_file(url, save_path):
    print(f"Starting download from {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        total_size = int(r.headers.get("content-length", 0)) # Get total file size (bytes)
        block_size = 8192  # Read 8KB at a time

        with open(save_path, "wb") as f, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=os.path.basename(save_path),
            initial=0,
            ascii=True,
            miniters=1
        ) as progress_bar:
            for chunk in r.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))

    print(f"Download completed: {save_path}")


def extract_tar_gz(file_path, extract_path):
    if not tarfile.is_tarfile(file_path):
        print(f"{file_path} is not a valid tar.gz file")
        return False

    print(f"Extracting: {file_path}")
    try:
        with tarfile.open(file_path, "r:gz") as tar:
            members = tar.getmembers()
            total_files = len(members)

            with tqdm(
                total=total_files,
                unit="file",
                desc="Extracting",
                ascii=True,
            ) as pbar:
                for member in members:
                    tar.extract(member, path=extract_path)
                    pbar.update(1)

        print(f"Extraction completed: {extract_path}")
        return True
    
    except Exception as e:
        print(f"Error extracting {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download and extract MeteoNet dataset")
    parser.add_argument("--region", type=str, default="SE", choices=["SE", "NW"], help="Region code, SE or NW")
    parser.add_argument("--year", type=int, nargs="+", required=True, choices=[2016, 2017, 2018], help="Years to download, e.g., --year 2016 2017 2018")
    parser.add_argument("--save_dir", type=str, default=".", help="Directory to save downloaded files")
    args = parser.parse_args()

    base_url = f"https://meteonet.umr-cnrm.fr/dataset/data/{args.region}/radar/reflectivity_old_product"

    for y in args.year:
        filename = f"{args.region}_reflectivity_old_product_{y}.tar.gz"
        url = os.path.join(base_url, filename)
        save_path = os.path.join(args.save_dir, filename)
        extract_dir = os.path.join(args.save_dir, f"{args.region}_reflectivity_{y}")

        print(f"\nProcessing {y}...")

        # Download file
        if os.path.exists(save_path):
            print(f"File already exists: {save_path}")
        else:
            try:
                download_file(url, save_path)
            except Exception as e:
                print(f"Failed to download file: {e}")
                continue

        # Extract file
        if os.path.exists(extract_dir) and os.listdir(extract_dir):
            print(f"Extraction folder already exists and is not empty, skipping extraction: {extract_dir}")
        else:
            os.makedirs(extract_dir, exist_ok=True)
            try:
                extract_tar_gz(save_path, extract_dir)
            except Exception as e:
                print(f"Failed to extract file: {e}")
                continue
        
        # Batch extract
        inner_dir = os.path.join(extract_dir, f"{args.region}_reflectivity_old_product_{y}")

        if not os.path.exists(inner_dir):
            print(f"Inner directory not found: {inner_dir}")
            continue

        print(f"\nBatch extracting all inner .tar.gz in: {inner_dir}")

        for fname in os.listdir(inner_dir):
            if fname.startswith("._") or not fname.endswith(".tar.gz"):
                continue
            
            tar_path = os.path.join(inner_dir, fname)

            print(f"→ Extracting inner file: {fname}")
            success = extract_tar_gz(tar_path, inner_dir)

            if success:
                print(f"Deleting {tar_path} ...")
                os.remove(tar_path)
            else:
                print(f"Skipping deletion (extraction failed): {tar_path}")

        print(f"Completed processing year {y}\n")


if __name__ == "__main__":
    main()