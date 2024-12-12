#!/usr/bin/env python

import json
import os
import cattrs
import sarif_om as om
import subprocess
import requests
from pathlib import Path

directory_name = "linting_outputs"

def run_linters():
    # API endpoint
    url = "http://localhost:5000/api/signals"
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    top_level_dir = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        
    repo_name = os.path.basename(top_level_dir)
    
    output_dir = Path(directory_name)
    output_dir.mkdir(exist_ok=True)
    try:
        # todo: add to reviewdog config instead
        linters = ['mypy', 'pylint']
        for linter in linters:
            save_file = f"sarif_output.json"

            subprocess.run(
                f'{linter} | reviewdog -reporter=sarif -runners={linter} --name={linter} >> {save_file}',
                shell=True,
                stderr=subprocess.PIPE,
                check=True,
            )
            
            with open(save_file, "r") as file:
                file.write(commit_hash)
                file.write("\n")
                file.write(repo_name)
                # data = {
                #     "repo_name": repo_name,
                #     "commit_hash": commit_hash,
                #     "sarif_data": json.load(file) 
                # }

                # response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
                # print(f"Server response {response.status_code}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")
        print(f"Error output: {e.stderr.decode()}")

if __name__ == "__main__":
    run_linters()
