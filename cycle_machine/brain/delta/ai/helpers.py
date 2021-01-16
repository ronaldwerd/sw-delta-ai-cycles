import os


def remove_all_csv_files(directory):
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.endswith(".csv"):
                os.remove(os.path.join(root, name))


def prepend_txt_to_file(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
