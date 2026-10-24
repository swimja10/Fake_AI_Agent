import os


def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
        valid_target_dir = (
            os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        )
        valid_dir = os.path.isdir(target_dir)

        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if valid_dir:
            statements = []
            for item in os.listdir(target_dir):
                item_dir = f"{target_dir}/{item}"
                statements.append(
                    f"- {item}: file_size={os.path.getsize(item_dir)}, is_dir={os.path.isdir(item_dir)}"
                )
            return "\n".join(statements))
        else:
            return f'Error: "{directory}" is not a directory'
    except Exception as e:
        return f"Error {e}"
