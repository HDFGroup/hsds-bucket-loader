import sys
import h5pyd

#
# Remove all domains in given folder
#
def printUsage():
    print("python folder_remove_all.py [--bucket bucketname] <folder>")
    print("Removes all domains in give folder!")
    sys.exit(0)


def main():
    if len(sys.argv) == 1 or (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        printUsage()
        sys.exit(1)
    
    bucket = None

    if len(sys.argv) == 4 and sys.argv[1] == "--bucket":
        bucket = sys.argv[2]
        print("using bucket:", bucket)
    
    folder_path = sys.argv[-1]
    if folder_path[0] != '/' or folder_path[-1] != '/':
        print("domain folder must start and end with '/")
        printUsage()

    folder = h5pyd.Folder(folder_path, mode='r+')
    domains = []
    for domain in folder:
        domains.append(domain)

    for domain in domains:
        print(f"removing: {domain}")
        del folder[domain]

main()



