from functions.get_files_info import get_files_info

args = [".", "pkg", "/bin", "../"]

for arg in args:
    if arg == ".":
        print("Result for current directory:")
    else:
        print(f"Result for {arg}:")

    print(get_files_info("calculator", arg))
