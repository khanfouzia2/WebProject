import sys
import json
import csv
import time
import requests
import os
#from shutil import rmtree
import shutil, sys
import os.path
 
#import subprocess
##
# Convert to string keeping encoding in mind...
##


# To create sonarqube project key
def create_project_key(key_name, project_name):
    url = "http://localhost:9000/api/projects/create?key=" + key_name + "&name=" + project_name
    api_response = requests.post( url)
    print (api_response.text)

def clone_gitRepo(url):
    os.system("git clone %s" %url)
    str = (url.split("/"))[len(url.split("/")) - 1]
    if (str == ""):
        str = (url.split("/"))[len(url.split("/")) - 2]
    if os.path.exists('./'+str):
        #shutil.rmtree('./'+str)
        #os.system('rmdir /S /Q "{}"'.format(str))
        #os.system("git clone %s" %url)
        return str
    else:
        #os.system("git clone %s" %url)
        return str

def run_mvn_analysis(project_key, dir):
    print("check dir")
    print(dir)
    os.chdir(dir)
    if os.path.isfile('pom.xml'):
       os.system("mvn compile")
       os.system("mvn sonar:sonar -Dsonar.projectKey=%s -Dsonar.host.url=http://localhost:9000" %project_key)
       time.sleep(7);
    elif os.path.isfile('build.gradle'):
        os.system("gradlew")
        os.system("gradle sonarqube -Dsonar.projectKey=%s -Dsonar.host.url=http://localhost:9000" %project_key)
    #os.system("gradlew")
    #p = subprocess.Popen(["mvn sonar:sonar -Dsonar.projectKey=%s -Dsonar.host.url=http://localhost:9000" %project_key], cwd=dir)
    #p.wait()
    #os.system("mvn sonar:sonar -Dsonar.projectKey=%s -Dsonar.host.url=http://localhost:9000" %project_key)
    #os.system("gradlew")
    #os.system("mkdir /tmp/empty")
    # -Dsonar.java.binaries=/tmp/empty
    

def to_string(s):
    try:
        return str(s)
    except:
        #Change the encoding type if needed
        return s.encode('utf-8')


def reduce_item(key, value):
    global reduced_item
    
    #Reduction Condition 1
    if type(value) is list:
        i=0
        for sub_item in value:
            reduce_item(key+'_'+to_string(i), sub_item)
            #reduce_item('', sub_item)
            i=i+1

    #Reduction Condition 2
    elif type(value) is dict:
        sub_keys = value.keys()
        for sub_key in sub_keys:
            reduce_item(key+'_'+to_string(sub_key), value[sub_key])
            #reduce_item('', value[sub_key])
    
    #Base Condition
    else:
        reduced_item[to_string(key)] = to_string(value)

	
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print ("\nUsage: python json_to_csv.py <node_name> <json_in_file_path> <csv_out_file_path>\n")
    else:
        #Clone project to be analyzed
        dir_name = clone_gitRepo(sys.argv[3])
        print("directory name is*************")
        print(dir_name)
        #Create sonarqube project_name
        #create_project_key ("mykey", "myproject")
        create_project_key (sys.argv[2], dir_name)
		
        #Run project analysis for mvn based project
        run_mvn_analysis(sys.argv[2], dir_name)
        os.chdir('..')
        os.system('dir')
        if not os.path.exists("results"):
             os.makedirs("results")
        os.chdir("results")
        #try:
         #   os.makedirs("results")
          #  os.chdir("results")
        #except OSError:
         #   print ("Creation of the directory results failed")
        #else:
         #   print ("Successfully created the directory results")
		
        #Reading arguments
        node = sys.argv[1]
        URL = "http://localhost:9000/api/issues/search?componentRoots=" + sys.argv[2]
        response_data = requests.get(url = URL);
        with open(dir_name+'.json', 'w') as outfile:
             json.dump(response_data.json(), outfile)
        json_file_path = dir_name+".json"
        print(json_file_path)
        #csv_file_path = sys.argv[3]
        csv_file_path = dir_name + ".csv"
        print(csv_file_path)
        fp = open(json_file_path, 'r')
        json_value = fp.read()
        raw_data = json.loads(json_value)
        fp.close()

        try:
            data_to_be_processed = raw_data[node]
        except:
            data_to_be_processed = raw_data

        processed_data = []
        header = []
        print ("###############")
        #print (response_data)
        print ("###############")
        myheader = ["_creationDate", "_hash", "_type", "_squid", "_component", "_severity", "_startLine", "_endLine", "_status", "_message", "_effort", "_debt"]
        for item in data_to_be_processed:
            my_item = {}
            my_item["creationDate"] = item["creationDate"]
            #print(item)
            if "hash" in item:
               my_item["hash"] = item["hash"]
            my_item["type"] = item["type"]
            my_item["squid"] = item["rule"]
            my_item["component"] = item["component"]
            if "severity" in item:
                my_item["severity"] = item["severity"]
            if "textRange" in item:
                my_item["startLine"] = item["textRange"]["startLine"]
                my_item["endLine"] = item["textRange"]["endLine"]
            if "status" in item:
                my_item["status"] = item["status"]
            my_item["message"] = item["message"]
            if "effort" in item:
                my_item["effort"] = item["effort"]
            if "debt" in item:
                my_item["debt"] = item["debt"]
            #print(my_item)
			
            reduced_item = {}
            reduce_item('', my_item)

            header += reduced_item.keys()
            #print(header)
            #print("###########")
            #print("&&&&&&&&&&&&&&&&&&&")
            processed_data.append(reduced_item)

        header = list(set(myheader))
        print (header)
        print (processed_data)
        #header.sort()

        with open(csv_file_path, 'w+') as f:
            writer = csv.DictWriter(f, header, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in processed_data:
                writer.writerow(row)

        print ("Just completed writing csv file with %d columns" % len(header))