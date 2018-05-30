import os
import glob
import time
import requests
import subprocess
from ConfigPaths import input_dir, output_dir, pdffigures2_dir
from MainParser import parse_XML

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
    # go to the director of where the PDF's are located
    os.chdir(input_dir)

    # remove spaces from names of PDF's since spaces causes pdffigures2 to skip pdf
    for file in glob.glob("*.pdf"):
        remove_space(file)

    os.chdir(pdffigures2_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    extract_figures(input_dir, output_dir)

    os.chdir(input_dir)

    for file in glob.glob("*.pdf"):

        file_name = data_extractor(file)
        if type(file_name) is bytes:
            file_name = file_name.decode('utf8')

        pdf_name = file[:-4]
        print(pdf_name)

        os.chdir(output_dir)

        for pdf in glob.glob(pdf_name + "*"):
            dest = file_name + '/Figures/' + pdf
            os.rename(pdf, dest)

        os.chdir(input_dir)



def data_extractor(file):

    papers = {"input": open(file, 'rb'), "consolidateCitations": "1"}

    start = time.time()
    r = requests.post('http://localhost:8070/api/processFulltextDocument', files=papers)
    finish = time.time()
    time_taken = finish - start
    times_taken.append(str({file: time_taken}))

    print("Status code for " + file + " = " + str(r.status_code))

    tei_result = r.text

    if tei_result is bytes:
        tei_result.decode('utf8')

    file_name = os.path.splitext(file)[0]

    XMLfile = open(output_dir + file_name + ".xml", 'w+', encoding='utf8')
    XMLfile.write(tei_result)
    XMLfile.close()
    os.chdir("../outputs")
    folder_name = parse_XML(XMLfile.name)
    os.chdir('../inputs')

    return folder_name


def extract_figures(input_path, output_path):

    command = ' '.join(['run-main', 'org.allenai.pdffigures2.FigureExtractorBatchCli', input_path, '-m', output_path])
    sbt_command = ' '.join(['sbt', '"' + command + '"'])
    print(sbt_command)
    subprocess.Popen(sbt_command, shell=True, universal_newlines=True).communicate()


def remove_space(file):

    new_name = file.translate(trans_table)
    os.rename(file, new_name)


if __name__ == '__main__':
    main()
    print("--- %s seconds ---" % (time.time() - start_time))