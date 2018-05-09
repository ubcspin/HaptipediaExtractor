import requests
import glob, os
import time

times_taken = []
total_time = 0

for file in glob.glob("*.pdf"):
    papers = {"input": open(file, 'rb'), "consolidateCitations": "1"}

    start = time.time()
    r = requests.post('http://localhost:8070/api/processFulltextDocument', files=papers)
    finish = time.time()
    time_taken = finish - start
    times_taken.append(str({file: time_taken}))
    total_time += time_taken

    print("Status code for " + file + " = " + str(r.status_code))

    tei_result = r.text

    file_name = os.path.splitext(file)[0]

    XMLfile = open("../myOutputs/" + file_name + ".xml", 'w+')
    XMLfile.write(tei_result.encode('utf8'))

    XMLfile.close();

total_time_str = "Total time for these files: " + str(total_time//60) + "min " \
    + str(total_time%60) + "s"
times_taken.append(total_time_str)
times_taken_lines = "\n".join(times_taken)

open("../outputs/" + "times_taken.txt", 'w').write(str(times_taken_lines))