import os
import sys
from pathlib import Path

import requests

API_ENDPOINTS = {
    "sarif": "https://app.aviator.co/api/signals/sarif",
    "astgrep": "https://app.aviator.co/api/signals/astgrep",
}


def main():
    commit_sha = os.getenv("GITHUB_SHA", None)
    if commit_sha is None:
        print("GITHUB_SHA is not set. Exiting...")
        sys.exit(1)
    repo_name = os.getenv("REPO_NAME", None)
    if repo_name is None:
        print("REPO_NAME is not set. Exiting...")
        sys.exit(1)
    access_token = os.getenv("AVIATOR_API_TOKEN", None)
    if access_token is None:
        print("AVIATOR_API_TOKEN is not set. Exiting...")
        sys.exit(1)
    input_format = os.getenv("INPUT_FORMAT", None)
    if input_format is None:
        print("INPUT_FORMAT is not set. Exiting...")
        sys.exit(1)
    file_paths_str = os.getenv("FILE_PATHS", "")
    file_paths = list(
        filter(lambda p: p != "", [p.strip() for p in file_paths_str.split(",")])
    )
    if not file_paths:
        print("FILE_PATHS is not set. Exiting...")
        sys.exit(1)

    api_endpoint = API_ENDPOINTS.get(input_format, None)
    if api_endpoint is None:
        print(f"Invalid input format {input_format}. Exiting...")
        sys.exit(1)
    api_endpoint += f"?repo_name={repo_name}&commit_sha={commit_sha}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    all_file_paths: set[str] = set()
    for file_path in file_paths:
        for input_file in Path.cwd().glob(file_path):
            if not input_file.is_file():
                print(f"File {input_file} does not exist. Skipping...")
                continue
            all_file_paths.add(str(input_file))

    for input_file in all_file_paths:
        with open(input_file, "r") as f:
            response = requests.post(api_endpoint, data=f, headers=headers)
            print(f"Server response {response.status_code}: {response.text}")


if __name__ == "__main__":
    main()
