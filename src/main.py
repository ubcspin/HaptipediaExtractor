import os
import glob
import time
import requests
import subprocess
import json
import ConfigPaths as config
from CrossReference import initialize_connections
from Device import get_devices
from MainParser import parse_file
from TextWriter import writeFiles
# from DatabaseConnection import add_data


devices = {}
times_taken = []
total_time = 0
start_time = time.time()

trans_table = str.maketrans(' ', '_')

main_dir = os.getcwd()

input_dir = config.input_dir
output_dir = config.output_dir
pdffigures2_dir = config.pdffigures2_dir


'''
Before running main():
1) make sure to have grobid running in the background, see github.com/grobid
2) have ConfigPaths.py set-up for the input and output directory
'''


def main():
    start = time.time()
    extract_figures(input_dir, output_dir)
    finish = time.time()
    print("Extracted Figures in " + str(finish - start) + "seconds")

    start = time.time()
    data_extractor()
    finish = time.time()
    print("Extracted Data in " + str(finish - start) + " seconds")

    start = time.time()
    parse_output_files()
    finish = time.time()
    print("Parsed Files in " + str(finish - start) + " seconds")

    clean_output_folder()


"""
For each XML File and JSON File, passes it to the MainParser module to extract data from both files
After finished parsing, place specific images into their folder, initialize connections between papers
and place in database(to be done on a later date)
"""


def parse_output_files():
    os.chdir(output_dir)

    count = 1
    number_files = str(len(glob.glob('*.xml')))
    for file in glob.glob('*.xml'):
        XMLfile_path = file
        pdf_name = XMLfile_path[:-4]
        print("XML: " + XMLfile_path)
        folder_name = parse_file(XMLfile_path, pdf_name)
        print("Parsed file " + str(count) + " out of " + number_files)
        if folder_name is not None:
            if type(folder_name) is bytes:
                folder_name = folder_name.decode('utf8')

            folder_name = folder_name.strip()  # remove any trailing spaces
            organize_images(pdf_name, folder_name)
        count += 1

    devices = get_devices()
    connections = {}
    if config.should_init_crossrefs:
        connections = initialize_connections(devices)
    # if config.add_to_db:
    #     add_data(devices, connections)
    if config.writeToFile:
        writeFiles(devices, connections)


def clean_output_folder():
    os.chdir(output_dir)
    os.makedirs('JSON and XML Files')
    for file in (glob.glob('*.xml') + glob.glob('*.json')):
        dest = 'JSON and XML Files/' + file
        os.rename(file, dest)


"""
Moves all images from a PDF to its specific folder
"""


def organize_images(pdf_name, folder_name):

    pdf_length = len(pdf_name) + 1 # to take into account the dash at the end and 0-index

    # figures are named by pdf_name-FigureX-01.png
    pdfs = glob.glob(pdf_name + '-Figure' + "*" +".png") + glob.glob(pdf_name + '-Table' + "*" +".png")

    write_fig_captions(pdf_name, folder_name)

    for pdf in pdfs:
        # new name of the pdf is now FigureX
        new_name = pdf[pdf_length:-6] + '.png'
        dest = folder_name + '/Figures/' + new_name
        os.rename(pdf, dest)


"""
JSON parser to write figure captions into the same folder as the figures
"""


def write_fig_captions(pdf_name, folder_name):
    file = pdf_name + '.json'
    try:
        with open(file, 'r') as json_file:
            data = json.load(json_file)

            for x in range(len(data)):
                caption = data[x]["caption"]
                figType = data[x]["figType"]
                number = data[x]['name']

                figure_number = number

                if figType == 'Figure':
                    figure_number = "Figure" + number
                elif figType == 'Table':
                    figure_number = 'Table' + number

                with open(folder_name + '/Figures/' + figure_number + '.txt', 'w+', encoding='utf8') as fig_text:
                    fig_text.write(caption)
    except:
        print("No JSON found for " + file)


"""
API call to GROBID to extract text, references and metadata. All extracted data written into an XML file.
If status code != 200, skips PDF since GROBID couldn't extract data.
"""
def data_extractor():
    os.chdir(input_dir)

    for file in glob.glob('*.pdf'):

        papers = {"input": open(file, 'rb'), "consolidateCitations": "1"}

        start = time.time()
        r = requests.post('http://localhost:8070/api/processFulltextDocument', files=papers)
        finish = time.time()
        time_taken = finish - start
        times_taken.append(str({file: time_taken}))

        print("Status code for " + file + " = " + str(r.status_code))

        if r.status_code == 200:

            tei_result = r.text

            if tei_result is bytes:
                tei_result.decode('utf8')

            file_name = os.path.splitext(file)[0]

            XMLfile = open(output_dir + file_name + ".xml", 'w+', encoding='utf8')

            XMLfile.write(tei_result)
            XMLfile.close()

        else:
            print("Status Code Not 200 for %s" % file)


"""
Call to PDFFigures2.0 Batch Mode to extract all figures and figure captions from all papers
TODO: place all images into an image folder and sort them later
"""

def extract_figures(input_path, output_path):

    # go to the director of where the PDF's are located
    os.chdir(input_dir)

    # remove spaces from names of PDF's since spaces causes pdffigures2 to skip pdf
    for file in glob.glob("*.pdf"):
        remove_space(file)

    os.chdir(pdffigures2_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    command = ' '.join(['run-main', 'org.allenai.pdffigures2.FigureExtractorBatchCli', input_path, '-m', output_path, '-d', output_path])
    sbt_command = ' '.join(['sbt', '"' + command + '"'])
    print(sbt_command)
    subprocess.Popen(sbt_command, shell=True, universal_newlines=True).communicate()


def remove_space(file):

    new_name = file.translate(trans_table)
    os.rename(file, new_name)


if __name__ == '__main__':
    main()
    print("--- %s seconds ---" % (time.time() - start_time))