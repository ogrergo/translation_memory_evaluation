if __name__ =='__main__':
    import sys
    import json

    if len(sys.argv) != 3:
        print("Usage: python %s file_in file_out"%sys.argv[0], file=sys.stderr)
        sys.exit(1)

    file_in = sys.argv[1]
    file_out = sys.argv[2]

    with open(file_in) as fp:
        with open(file_out, 'w') as fp_out:
            for l in fp:
                r = json.loads(l)
                fp_out.write("{}\n".format(r['_transforms'][-1]['text']))

