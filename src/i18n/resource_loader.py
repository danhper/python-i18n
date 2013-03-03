from formats import Format

def load_resource(filename, format=None):
    if not format:
        format = guess_format(filename)
    if format == Format.YAML:
        pass
    # elif format == Format.

def guess_format(filename):
    if filename.endswith("yml"):
        return Format.YAML
    elif filename.endswith("json"):
        return Format.JSON
    else:
        raise KeyError("could not guess format for file {filename} and no format given".format(filename))
