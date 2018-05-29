import os
import glob
import time
import requests
import subprocess
from MainParser import parse_XML

times_taken = []
total_time = 0
start_time = time.time()

trans_table = str.maketrans(' ', '_')

'''
Before Running script:
1) make sure to have grobid running in the background, see github.com/grobid
2) PDFFigures2.0 is in the same directory as this script
'''


def main():

    # go to the directory of where the PDF's are found (in this case it's inputs)
    os.chdir('inputs')
    for file in glob.glob("*.pdf"):
        remove_space(file)
        # data_extractor(file)
        # os.chdir('../pdffigures2')
        # extract_figures('../inputs', '../outputs')
        # os.chdir('../inputs')


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

    XMLfile = open("../outputs/" + file_name + ".xml", 'w+', encoding='utf8')
    XMLfile.write(tei_result)
    XMLfile.close()
    os.chdir("../outputs")
    parse_XML(XMLfile.name)
    os.chdir('../inputs')


def extract_figures(input_path, output_path):

    command = ' '.join(['run-main', 'org.allenai.pdffigures2.FigureExtractorBatchCli', input_path, '-m', output_path])
    sbt_command = ' '.join(['sbt', '"' + command + '"'])
    print(sbt_command)
    subprocess.Popen(sbt_command, shell=True, universal_newlines=True).communicate()


def remove_space(file):
    print("old name: " + file)
    new_name = file.translate(trans_table)
    os.rename(file, new_name)
    print("new name: " + file)


if __name__ == '__main__':
    main()
    print("--- %s seconds ---" % (time.time() - start_time))