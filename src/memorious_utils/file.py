from os.path import splitext

def shorten(context, data):
    if "file_name" in data:
        response = context.http.rehash(data)
        max_length = context.params.get("max_length", 100)
        context.log.info(data)
        if len(data["file_name"]) > max_length:
            root, ext = splitext(data["file_name"])
            data["file_name"] = "%s%s" % (data["id"], ext)
            context.log.info("File name too long, shortened to %s" % (
                data["file_name"],))
    context.emit(data=data)
