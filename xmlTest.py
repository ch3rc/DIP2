from xml.dom import minidom
import os


def xmlCreator(root, xml, picName, i, picNum):

    pictureChild = root.createElement(f'picture{i}')
    pictureChild.setAttribute('name', f'{picName}')
    text = root.createTextNode(f'location https://phil.cdc.gov/Details.aspx?pid={picNum}')
    pictureChild.appendChild(text)
    xml.appendChild(pictureChild)

    return root


def main():
    """Mock up for project to create xml document"""
    new_root = None
    # test directory to write to, will be changed to oudir location in project
    outdir = "test"
    # will be changed to indir search path in project
    search_path = "C:\\Users\\codyh\\PycharmProjects\\DIP2\\Electron Microscope\\Colored"
    os.makedirs(outdir, exist_ok=True)
    parent = os.listdir(search_path)
    # set up initial document and create root element
    root = minidom.Document()
    xml = root.createElement('root')
    root.appendChild(xml)
    # get picture number and set as variable, needed for picture location
    for i, child in enumerate(parent):
        k = i+1
        num = child[:5]
        new_root = xmlCreator(root, xml, child, k, num)

    # sets correct indentation for child elements
    xml_str = root.toprettyxml(indent="\t")

    save_path_file = "metadata.xml"

    filepath = os.getcwd()

    filepath = os.path.join(filepath, outdir)

    save_path_file = os.path.join(filepath, save_path_file)

    with open(save_path_file, "w") as f:
        f.write(xml_str)


if __name__ == '__main__':
    main()




