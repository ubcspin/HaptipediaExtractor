import requests
import glob, os
import time

times_taken = []
total_time = 0

os.chdir("inputs")
for file in glob.glob("*.pdf"):
    paper = open(file, 'rb').read()

    start = time.time()
    r = requests.post("http://scienceparse.allenai.org/v1", data=paper, json={"key": "value"})
    finish = time.time()
    time_taken = finish - start
    times_taken.append(str({file: time_taken}))
    total_time += time_taken

    print("Status code for " + file + " = " + str(r.status_code))
    json_result = r.text

    file_name = os.path.splitext(file)[0]

    open("../myOutputs/" + file_name + ".json", 'w').write(json_result.encode('utf-8'))

total_time_str = "Total time for these files: " + str(total_time // 60) + "min " \
                 + str(total_time % 60) + "s"
times_taken.append(total_time_str)
times_taken_lines = "\n".join(times_taken)

open("../myOutputs/" + "times_taken.txt", 'w').write(str(times_taken_lines))