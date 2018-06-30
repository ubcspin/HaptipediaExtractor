import os
import glob
import time
import requests
import subprocess
from CrossReference import build_geneology, initialize_cross_ref
from Device import get_devices
from ConfigPaths import input_dir, output_dir, pdffigures2_dir, writeToFile
from MainParser import parse_files
from TextWriter import writeFiles

devices = {}
times_taken = []
total_time = 0
start_time = time.time()

trans_table = str.maketrans(' ', '_')

main_dir = os.getcwd()


'''
Before Running script:
1) make sure to have grobid running in the background, see github.com/grobid
'''


def main():
    # start = time.time()
    # extract_figures(input_dir, output_dir)
    # finish = time.time()
    # print("Extracted Figures in " + str(finish - start) + "seconds")
    #
    # start = time.time()
    # data_extractor()
    # finish = time.time()
    # print("Extracted Data in " + str(finish - start) + " seconds")

    start = time.time()
    parse_output_files()
    finish = time.time()
    print("Parsed Files in " + str(finish - start) + " seconds")

    # clean_output_folder()


def parse_output_files():
    os.chdir(output_dir)

    count = 1
    for file in glob.glob('*.xml'):
        number_files = str(len(glob.glob('*.xml')))
        XMLfile_path = file
        pdf_name = XMLfile_path[:-4]
        JSONfile_path = output_dir + pdf_name + '.json'
        print("XML: " + XMLfile_path)
        print("JSON: " + JSONfile_path)
        folder_name = parse_files(XMLfile_path, JSONfile_path)
        print("Parsed file " + str(count) + " out of " + number_files)
        if folder_name is not None:
            if type(folder_name) is bytes:
                folder_name = folder_name.decode('utf8')

            folder_name = folder_name.strip()  # remove any trailing spaces
            organize_images(pdf_name, folder_name)
        count += 1

    devices = get_devices()
    initialize_cross_ref(devices)
    build_geneology(devices)
    if writeToFile:
        writeFiles(devices)


def clean_output_folder():
    os.chdir(output_dir)
    os.makedirs('JSON and XML Files')
    for file in (glob.glob('*.xml') + glob.glob('*.json')):
        dest = 'JSON and XML Files/' + file
        os.rename(file, dest)


def organize_images(pdf_name, folder_name):

    pdf_length = len(pdf_name) + 1 # to take into account the dash at the end and 0-index

    pdfs = glob.glob(pdf_name + '-Figure' + "*" +".png") + glob.glob(pdf_name + '-Table' + "*" +".png")

    for pdf in pdfs:
        new_name = pdf[pdf_length:]
        dest = folder_name + '/Figures/' + new_name
        os.rename(pdf, dest)


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