DEFAULT_ENCODING = "utf_8"


def prefix_filename(subfolder: str, filename: str) -> str:
    if subfolder is not None:
        if len(subfolder) > 1 and subfolder[1].__eq__(":"):
            return subfolder + "\\" + filename
        return "..\\" + subfolder + "\\" + filename
    return "..\\" + filename


def read_input_file(filename: str, encoding=DEFAULT_ENCODING) -> str:
    try:
        with open(filename, "r", encoding=encoding) as handle:
            text = handle.read()
            return text
    except IOError:
        print("Could not read file {}.".format(filename))


def write_output_file(filename: str, data: str, encoding=DEFAULT_ENCODING):
    try:
        with open(filename, "w", encoding=encoding) as handle:
            handle.write(data)
    except IOError:
        print("Could not write to file {}.".format(filename))