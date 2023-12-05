import os
import shutil
import subprocess
import time  # Import the time module
from github import Github

def split_range(start, stop, num_subranges):
    if num_subranges <= 0:
        raise ValueError("Number of subranges must be greater than zero.")

    subrange_size = (stop - start) // num_subranges

    subranges = []
    current_start = start

    for _ in range(num_subranges - 1):
        current_stop = current_start + subrange_size
        subranges.append((current_start, current_stop))
        current_start = current_stop + 1

    # Last subrange extends to the original stop value
    subranges.append((current_start, stop))

    return subranges

def find_and_replace_ranges(script_content, start_range, end_range, new_start, new_end):
    # Find and replace ranges in the script content
    start_range_placeholder = "start_range_placeholder"
    end_range_placeholder = "end_range_placeholder"

    script_content = script_content.replace(start_range, start_range_placeholder)
    script_content = script_content.replace(end_range, end_range_placeholder)

    script_content = script_content.replace(start_range_placeholder, new_start)
    script_content = script_content.replace(end_range_placeholder, new_end)

    return script_content

def generate_and_save_scripts(script_content, num_duplicates, new_subranges, export_folder):
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    for i, new_subrange in enumerate(new_subranges):
        modified_script_content = find_and_replace_ranges(
            script_content, existing_start_range, existing_end_range, hex(new_subrange[0]), hex(new_subrange[1])
        )

        file_name = f"generated_script_{i + 1}.py"
        file_path = os.path.join(export_folder, file_name)
        with open(file_path, 'w') as modified_script_file:
            modified_script_file.write(modified_script_content)

    print(f"Generated and saved {num_duplicates} modified scripts in the '{export_folder}' folder.")

def delete_old_scripts(export_folder):
    # Check and delete old generated scripts before uploading new ones
    for file_name in os.listdir(export_folder):
        file_path = os.path.join(export_folder, file_name)
        os.remove(file_path)
        print(f"Deleted old script: {file_name}")

def upload_to_github(username, repo_name, access_token, export_folder):
    # Authenticate with GitHub
    g = Github(access_token)
    repo = g.get_user().get_repo(repo_name)

    # Check if the main branch exists, if not, create it
    main_branch = repo.get_branch("main")
    if not main_branch:
        repo.create_git_ref(ref="refs/heads/main", sha=repo.get_branch("master").commit.sha)

    # Delete old scripts before uploading new ones
    delete_old_scripts(export_folder)

    # Upload each modified script to the 'main' branch
    for file_name in os.listdir(export_folder):
        file_path = os.path.join(export_folder, file_name)
        content = open(file_path, 'rb').read()

        try:
            contents = repo.get_contents(file_name, ref="main")
            repo.update_file(contents.path, f"Upload {file_name}", content, contents.sha, branch="main")
            print(f"File '{file_name}' updated on GitHub in the 'main' branch.")
        except Exception:
            repo.create_file(file_name, f"Upload {file_name}", content, branch="main")
            print(f"File '{file_name}' created on GitHub in the 'main' branch.")

def run_multiplexer_script(ssh_command):
    # Add a 3-second rate limit before opening a new session
    time.sleep(3)

    # Run a new session using multiplexer
    subprocess.run(["tmux", "new-session", "-d", "-s", "my_session", ssh_command])

if __name__ == "__main__":
    # GitHub repository details
    github_username = "paranomicvibes"
    github_repo_name = "X"
    github_access_token = "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"

    # SSH server details
    ssh_server = "root@segfault.net"
    ssh_password = "segfault"

    # Read the content of the external script 'ABC.py'
    script_file_path = 'ABC.py'
    if not os.path.isfile(script_file_path):
        print("Error: 'ABC.py' not found. Please make sure the external script is in the same directory.")
    else:
        with open(script_file_path, 'r') as script_file:
            script_content = script_file.read()

        # Specify the existing ranges and the new subranges
        existing_start_range = "0000000000000000000000000000000000000000000000020000000000000000"
        existing_end_range = "000000000000000000000000000000000000000000000003ffffffffffffffff"
        num_subranges = int(input("Enter the number of subranges: "))
        provided_start = int(existing_start_range, 16)
        provided_stop = int(existing_end_range, 16)
        new_subranges = split_range(provided_start, provided_stop, num_subranges)

        # Specify the number of duplicates
        num_duplicates = int(input("Enter the number of duplicates: "))

        # Generate and save modified scripts in the 'export' folder
        export_folder = 'export'
        generate_and_save_scripts(script_content, num_duplicates, new_subranges, export_folder)

        # Upload the modified scripts to GitHub
        upload_to_github(github_username, github_repo_name, github_access_token, export_folder)

        # Run a new session using multiplexer and execute each generated code
        for i, _ in enumerate(new_subranges):
            # Set up the SSH command with GitHub repository and installing requirements
            ssh_command = f"sshpass -p {ssh_password} ssh {ssh_server} 'git clone https://github.com/{github_username}/{github_repo_name}.git /path/to/repo && cd /path/to/repo && pip install -r requirements.txt && python {export_folder}/generated_script_{i + 1}.py'"
            run_multiplexer_script(ssh_command)
