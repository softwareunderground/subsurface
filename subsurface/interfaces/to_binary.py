import json


def base_structs_to_binary_file(path, base_struct, order='F'):
    bytearray_le, header = base_struct.to_binary(order=order)
    with open(path+'.json', 'w') as outfile:
        json.dump(header, outfile)

    new_file = open(path+".le", "wb")
    new_file.write(bytearray_le)