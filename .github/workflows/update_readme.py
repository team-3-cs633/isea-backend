import sys


def main(argv):
    """ Function for updating the project README
    to have the most up to date coverage bagde
    
    Args:
      coverage percentage, generated from
      the last line of coverage run -m pytest
    
    """
    
    coverage = None
    color = None
    updated = None
    
    if len(argv) == 1:
        coverage = argv[0]
        
        try:
            coverage_number = int(coverage[:-1])
        except TypeError:
            sys.stdout.write("0")
            sys.exit(0)
        if coverage_number == 00:
            color = "sucess"
        elif coverage_number <=50:
            color = 'red'
        elif 50 < coverage_number  <90:
            color = 'orange'
        else:
            color = 'success'
        
        updated = f"![](https://img.shields.io/badge/coverage-{coverage}25-{color})\n"
    
    with open('README.md', 'r+') as file:
        lines = file.readlines()
        
        if updated and updated != lines[1]:
            lines[1] = updated
    
            file.seek(0)
            file.writelines(lines)
            sys.stdout.write("1")
        else:
            sys.stdout.write("0")
        
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])