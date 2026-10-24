import os
import subprocess


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_file = (
            os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        )
        valid_file = os.path.isfile(target_file)

        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not valid_file:
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_file]

        if args:
            command.extend(args)

        complete = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

        process_string = ""

        if complete.returncode != 0:
            process_string += f"Process exited with code {complete.returncode}"

        elif complete.stdout == "" and complete.stderr == "":
            process_string += "No output produced"
        else:
            process_string += f"STDOUT: {complete.stdout}STDERR: {complete.stderr}"

        return process_string

    except Exception as e:
        return f"Error: executing Python file: {e}"
