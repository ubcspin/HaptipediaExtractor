import os
import glob
import time
import requests

times_taken = []
total_time = 0
start_time = time.time()

'''
Before Running script, make sure to have grobid running in the background, see github.com/grobid
'''



def main():
    os.chdir('inputs')
    grobid_extractor()
    # call parsers to begin extracting references, section titles and section text
    rename_pdf()
    os.chdir('..')

def rename_pdf():


def grobid_extractor():

    for file in glob.glob("*.pdf"):
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

        XMLfile.close();


if __name__ == '__main__':
    main()
    print("--- %s seconds ---" % (time.time() - start_time))