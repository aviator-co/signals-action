#!/usr/bin/env python

import json
import os
# import cattrs
# import sarif_om as om
import subprocess
import requests
from pathlib import Path

directory_name = "linting_outputs"

def run_linters():
    github_action_path = os.getenv("ACTION_PATH", "Unknown")
    # todo: update URL
    url = "https://app.aviator.co/api/signals"
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    top_level_dir = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        
    access_token = os.getenv("AVIATOR_TOKEN")
    repo_name = os.path.basename(top_level_dir)
    # repo_name = 'aviator-testing-sa/testing-1'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}" 
    }
    
    output_dir = Path(directory_name)
    output_dir.mkdir(exist_ok=True)
    output_file = "output.txt"

    if os.path.exists(output_file):
        os.remove(output_file)

    try:
        # todo: add to reviewdog config instead
        linters = ['mypy', 'pylint']
        for linter in linters:
            save_file = f"sarif_output_{linter}.json"

            subprocess.run(
                f'{linter} | reviewdog -reporter=sarif -runners={linter} --name={linter} -conf={github_action_path}/.reviewdog.yml > {save_file}',
                shell=True,
                stderr=subprocess.PIPE,
                check=True,
            )
            
            with open(save_file, "r") as tool_output:
                data = {
                    "repo_name": repo_name,
                    "commit_hash": commit_hash,
                    "sarif_data": json.load(tool_output) 
                }

                print(headers)
                response = requests.post(url, json=data, headers=headers)
                print(f"Server response {response.status_code}: {response.text}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")
        print(f"Error output: {e.stderr.decode()}")

if __name__ == "__main__":
    run_linters()