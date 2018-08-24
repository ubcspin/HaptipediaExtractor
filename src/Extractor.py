import os
import glob
import time
import requests
import subprocess
import json
from ConfigPaths import add_to_db
from DatabaseFunctionalityModules.DatabaseConnection import check_database
from Device import get_devices
from Parser import parse_file


devices = {}
times_taken = []
total_time = 0
start_time = time.time()

trans_table = str.maketrans(' ', '_')

main_dir = os.getcwd()


def check_resources():
    try:
        requests.post('http://localhost:8070/api/isalive')
    except:
        print("GROBID NOT RUNNING IN BACKGROUND, PLEASE TURN IT ON >:(")
        return False

    if add_to_db:
        database_is_up = check_database()
        if database_is_up:
            return True
        else:
            print("DATABASE NOT CONFIGURED")
            return False
    else:
        return True


"""
parse_output_files(output_dir)

Purpose: extracts the pdf_name from XML and passes both to parse_files which returns the name of the paper
         then creates a folder and organizes images into the folder
Parameters: output_dir - directory with all XML files to be parsed
Returns: list of device objects created from XML files
"""


def parse_output_files(output_dir):
    os.chdir(output_dir)

    count = 1
    number_files = str(len(glob.glob('*.xml')))
    for file in glob.glob('*.xml'):
        XMLfile_path = file
        pdf_name = XMLfile_path[:-4]
        folder_name = parse_file(XMLfile_path, pdf_name)
        print("Parsed file " + str(count) + " out of " + number_files)
        create_folder_with_figs(folder_name, pdf_name)

        count += 1
    devices = get_devices()
    return devices


"""
create_folder_with_figs(folder_name, pdf_name)

Purpose: creates folder which holds the figures and figure captions for a pdf
Parameters: folder_name - extracted title of the pdf and name of the folder
            pdf_name - name of the pdf file
Returns: none
"""


def create_folder_with_figs(folder_name, pdf_name):
    if folder_name is not None:
        if type(folder_name) is bytes:
            folder_name = folder_name.decode('utf8')

        folder_name = folder_name.strip()  # remove any trailing spaces
        organize_images(pdf_name, folder_name)
        write_fig_captions(pdf_name, folder_name)


"""
clean_output_folder(output_dir)

Purpose: moves all XML and JSON files into one folder
Parameters: output_dir - directory that contains all the XML and JSON files
Returns: none
"""


def clean_output_folder(output_dir):
    os.chdir(output_dir)
    if not os.path.exists('JSON and XML Files'):
        os.makedirs('JSON and XML Files')
    for file in (glob.glob('*.xml') + glob.glob('*.json')):
        dest = 'JSON and XML Files/' + file
        os.rename(file, dest)


"""
organize_images(pdf_name, folder_name)

Purpose: Moves all images from a PDF to its specific folder
Parameters: pdf_name - name of the pdf where the images came from
            folder_name - title of the pdf extracted from GROBID
Returns: none
"""


def organize_images(pdf_name, folder_name):

    if os.path.exists('temp_imgs'):
        os.chdir('temp_imgs')
        pdf_length = len(pdf_name) + 1 # to take into account the dash at the end and 0-index

        # figures are named in the form pdf_name-FigureX-XX.png
        pdfs = glob.glob(pdf_name + '-Figure' + "*" +".png") + glob.glob(pdf_name + '-Table' + "*" +".png")

        for pdf in pdfs:
            # new name of the pdf is now FigureX
            count = 1
            new_name = pdf[pdf_length:-6] + '.png'
            dest = '../' + folder_name + '/Figures/' + new_name
            if os.path.exists(dest):
                dest = dest[:-4] + '(' + str(count) + ').png'
                count += 1
                # if the name still exists, keep increasing count until new name is not yet created
                while os.path.exists(dest):
                    dest = dest[:-7] + '(' + str(count) + ').png'
                    count += 1
            os.rename(pdf, dest)
        os.chdir('..')


"""
write_fig_captions(pdf_name, folder_name)

Purpose: writes the figure captions from the JSON file into the given folder name's figure directory
Parameters: pdf_name - name of the pdf which has the same name as the json file
             folder_name - name of the folder
Returns: none
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
data_extractor(input_dir, output_dir)

Purpose: calls the GROBID API, extraction successful if status_code is 200 and text is written into an XML file
Parameters: input_dir - input directory that holds all PDFs
            ouput_dir - output directory to write XML files into
Returns: none
"""


def data_extractor(input_dir, output_dir):
    os.chdir(input_dir)

    for file in glob.glob('*.pdf'):

        papers = {"input": open(file, 'rb'), "consolidateCitations": "0"}
        r = requests.post('http://localhost:8070/api/processFulltextDocument', files=papers)

        print("Status code for " + file + " = " + str(r.status_code))

        if r.status_code == 200:

            tei_result = r.text

            if tei_result is bytes:
                tei_result.decode('utf8')

            file_name = os.path.splitext(file)[0]

            XMLfile = open(output_dir + '/' + file_name + ".xml", 'w+', encoding='utf8')

            XMLfile.write(tei_result)
            XMLfile.close()

        else:
            print("Status Code Not 200 for %s" % file)
            #TODO: write error PDFS into some kind of error report


"""
extract_figures(input_dir, output_dir, pdffigures_dir, thread_count)


Purpose: Call to PDFFigures2.0 Batch Mode to extract all figures and figure captions from all papers
Parameters: input_dir - directory that holds all PDF files
            output_dir - director to that will hold extracted figures and JSON files
            pdffigures2_dir - path to pdffigures2.0, needed for subprocess call
            thread_count - number of threads given to pdffigures2.0 to extract figures
Returns: none
"""


def extract_figures(input_dir, output_dir, pdffigures2_dir, thread_count):

    # go to the director of where the PDF's are located
    os.chdir(input_dir)

    os.chdir(pdffigures2_dir)

    image_outputs = output_dir + '/temp_imgs/'
    if not os.path.exists(image_outputs):
        os.makedirs(image_outputs)

    stat_file = output_dir + '/stats.json'

    command = ' '.join(['run-main', 'org.allenai.pdffigures2.FigureExtractorBatchCli', input_dir, '-m', image_outputs, '-d', output_dir, '-s', stat_file, '-t', thread_count, '-e'])
    sbt_command = ' '.join(['sbt', '"' + command + '"'])
    try:
        subprocess.Popen(sbt_command, shell=True, universal_newlines=True).communicate()
    except Exception as e:
        print(e)


"""
remove_space(file)

Purpose: removes trailing spaces in the name of given file since it causes errors
Parameters: file - name of the file to check for trailing spaces
Returns: none
"""


def remove_space(file):

    new_name = file.translate(trans_table)
    os.rename(file, new_name)



