def handle_uploaded_file(f):
    with open('/home/encoding/a.txt', 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)