# Author: Cameron Sykes (cjsr4d@umsystem.edu) & Cody Hawkins (ch3rc@umsystem.edu)
# File: corpus.py
# Purpose: Create a corpus of images with metadata recorded in a separate file
# Due: 09/27/2020

from xml.dom import minidom
import getopt
import sys
import os
import cv2 as cv
from PIL import Image
from PIL.ExifTags import TAGS

rows = 480
columns = 640

def xmlCreator(root, xml, picName, i, picNum, xmlData):
    pictureChild = root.createElement(f'picture{i}')
    pictureChild.setAttribute('name', f'{picName}')
    text = root.createTextNode(f'location https://phil.cdc.gov/Details.aspx?pid={picNum}')
    pictureChild.appendChild(text)

    metaChild = root.createElement(f"metadata {i}")
    metaChild.setAttribute('name', 'metadata')
    for j in xmlData:
        metadata = j.split(':')
        dataName = metadata[0]
        data = metadata[1:]

        dataElement = root.createElement("data")
        dataElement.setAttribute('name', f'{dataName}')
        text = root.createTextNode(f'{data}')
        dataElement.appendChild(text)
        metaChild.appendChild(dataElement)

    pictureChild.appendChild(metaChild)
    xml.appendChild(pictureChild)

    return root

def writeMetadata(fileName):
    metadataOutput = []

    im = Image.open(fileName)
    exifdata = im.getexif()

    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes
        if isinstance(data, bytes):
            data = data.decode(encoding='ISO-8859-1')

        if isinstance(data, str):
            data = data.replace("\x00", '')

        metadataOutput.append(f"{tag}:{data}")

    return metadataOutput

def colorConversion(fileName, colorChoice):
    imageArray = None
    thresh = 127

    try:
        imageArray = cv.imread(fileName, cv.IMREAD_GRAYSCALE)
    except cv.error:
        print(f"File {fileName} is not a valid image file")

    if colorChoice == 1:
        imageArray = cv.threshold(imageArray, thresh, 255, cv.THRESH_BINARY)[1]

    return imageArray

def transform(fileArray, keepRatio):
    if keepRatio:
        # Find the ratio that the image will scale by. Multiply both the width and height so as to preserve the aspect ratio. Reassign the element in allFiles to this new image
        (preTransformationRows, preTransformationColumns) = fileArray.shape[:2]
        scaleFactor = max((preTransformationRows / columns), (preTransformationColumns / columns))
        interpolation = cv.INTER_AREA if scaleFactor > 1 else cv.INTER_CUBIC
        fileArray = cv.resize(fileArray, (int(preTransformationColumns / scaleFactor), int(preTransformationRows / scaleFactor)), interpolation=interpolation)
    else:
        fileArray = cv.resize(fileArray, (columns, rows))

    return fileArray

def dfs(directory):
    # Initialize an array to hold all the files found in each directory
    foundFiles = []

    # OS independent path separator
    separator = "\\" if "\\" in directory else "/"
    directory = os.sep.join(directory.split(separator))

    # List all of the files in the passed directory
    # If the directory doesn't exit the os module will throw a FileNotFoundError
    try:
        directory = os.path.realpath(directory)
        directoryContents = os.listdir(directory)
    except FileNotFoundError:
        print("Directory could not be found")
        usage()

    # The contents of the passed directory are stepped through and logged into foundFiles
    # dfs() is called recursively on each directory found. If the file is not a directory the file is logged into foundFiles and eventually returned
    for d in directoryContents:
        content = os.path.join(directory, d)
        try:
            foundFiles.extend(dfs(content))
        except NotADirectoryError:
            foundFiles.append(content)

    return foundFiles

def usage():
    print("\t\t-----Usage-----")
    print("-a, --aspect\t\tPreserve aspect ratio")
    print("-g, --gray\t\tConvert the images to gray scale")
    print("-b, --binary\t\tConvert the image to binary (black and white)")
    print("-r, --rows\t\tChange the number of rows (default: 480)")
    print("-c, --columns\t\tChange the number of columns (default: 640)")
    print("-t, --type\t\tSave the picture as this new type")
    print("provide a directory to get photos from")
    print("specify the name of the directory you would like it to go to")
    print("default output directory is indir.corpus")
    sys.exit(1)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "habgr:c:t:", ["help", "aspect", "binary", "gray", "rows", "columns", "type"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(1)

    global rows
    global columns
    indir = os.getcwd()
    outdir = "indir.corpus"
    type_file = None
    color = None
    preserveRatio = False
    im = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(1)
        elif o in ('-a', '--aspect'):
            preserveRatio = True
        elif o in ('-b', '--binary'):
            color = 1
        elif o in ("-g", "--gray"):
            color = 2
        elif o in ("-r", "--rows"):
            rows = int(a)
        elif o in ("-c", "--columns"):
            columns = int(a)
        elif o in ("-t", "--type"):
            a = a.upper()
            if a in ('JPG', 'TIF', 'BMP', 'PNG'):
                type_file = a.lower()
            else:
                usage()
                sys.exit(1)
        else:
            assert False, "unhandled option"

    if len(args) > 2:
        indir = " ".join(args[:2])
        outdir = args[-1]

        indir = os.path.basename(indir)
    elif len(args) > 0:
        indir = " ".join(args)
        indir = os.path.basename(indir)

    os.makedirs(outdir, exist_ok=True)
    allImages = dfs(indir)

    newRoot = minidom.Document()
    xml = newRoot.createElement("root")
    newRoot.appendChild(xml)
    for i, imageFileName in enumerate(allImages):
        if color:
            im = colorConversion(imageFileName, color)  # Reads file and returns image array
        else:
            try:
                im = cv.imread(imageFileName)
            except cv.error:
                print(f"File {imageFileName} is not a valid image file")

        if im is not None:
            im = transform(im, preserveRatio)

            metadataOutput = writeMetadata(imageFileName)

            imageBaseName = os.path.basename(imageFileName)
            if imageBaseName[:5].isdigit():
                root = xmlCreator(newRoot, xml, imageBaseName, i + 1, imageBaseName[:5], metadataOutput)
            else:
                root = xmlCreator(newRoot, xml, imageBaseName, i + 1, imageBaseName, metadataOutput)

            if type_file:
                imageFileName = os.path.basename(imageFileName).split(".")[0] + "." + type_file

            imageFileName = os.path.join(outdir, os.path.basename(imageFileName))
            cv.imwrite(imageFileName, im)

    xml_str = root.toprettyxml(indent="\t")
    metaDataPath = os.path.join(outdir, "metadata.xml")

    with open(metaDataPath, 'w') as metaWrite:
        metaWrite.write(xml_str)


if __name__ == "__main__":
    main()
