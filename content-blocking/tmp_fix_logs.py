from source.file_manipulation import load_json, get_traffic_files, save_json

traffic_files = get_traffic_files('network')

for file in traffic_files:
    data = load_json(file)
    for log in data:
        init = log.get('initiator')
        if init.get('stack'):
            if init.get('stack').get('parent'):
                print("parent")