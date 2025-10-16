import os, csv ,fetch_mod_code
#file_path = (input("Enter the path to the file: ") + ".csv").strip().upper()
file_path = 'Estimated GPA.csv'
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, file_path)
mods_cache = {}
SAVE_CSV_TO_PARENT_DIR = True
CACHE_FILE = os.path.join(script_dir,"mods_cache.json")
HEADER = ['AY','Module','AU','Grade','Points','SGPA','CGPA','Weight','Description'] 
gpa_list = []
print(script_dir,end="-> Directory Path\n")
print(file_path,end= "->File Path\n")
def select_file(file_path='GPA.csv'):
    #options to edit actual gpa file, estimating gpa file, new gpa file
    return file_path
def check_file_exist(file_path:str)->bool:
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file: 
            writer = csv.writer(file)
            writer.writerow(HEADER)
            return False
    else: 
        return True 
    
def read_file(file_path)->list[dict[str,str]]: #improve using pandas , learn about dataframe while ur at it
    global gpa_dict
    global HEADER 
    global gpa_list 
    gpa_list = [] 
    """Reads the content of a file and returns it."""
    if check_file_exist(file_path):
        with open(file_path, 'r') as file:
            file.readline()
            for line in file:
                line = list(line.strip().split(','))
                print(line)
                if len(line) == len(HEADER) - 1 :
                    HEADER = ['AY','Module','AU','Grade','Points','SGPA','CGPA','Weight'] 
                elif len(line) != len(HEADER):
                    raise ValueError("The number of columns in the file does not match the HEADER.")
                #gpa_dict = {HEADER[i]: line[i] for i in range(len(HEADER))} 
                gpa_dict = dict(zip(HEADER, line))
                gpa_list.append(gpa_dict)
                gpa_dict = {}
    else:
        print("New file detected. Creating entries....")
        updating_list(gpa_list)
            #print(gpa_list)
    return gpa_list

def mod_sorting(gpa_list,key="Module"): #putting default value so that u can sort by diff key with reference to AY
    temp = None 
    temp_list = []
    new_list = []
    for index,dict in enumerate(gpa_list):
        if index == len(gpa_list) -1 :
            temp_list.append(dict)
        if temp!=dict["AY"] or index == len(gpa_list) - 1: 
            if temp is not None: 
                temp_list.sort(key=lambda dict : dict[key])
                calculate_cgpa(temp_list,True)
                temp_sgpa = temp_list[-1]['SGPA']
                for temp_dict in temp_list:
                    temp_dict['SGPA'] = temp_sgpa
                new_list.extend(temp_list)
                temp_list = [] 
            else: #if temp is None and theres only one dict in the list
                new_list.extend(temp_list)
            temp = dict["AY"]
        temp_list.append(dict)
    gpa_list = new_list[:]
    return gpa_list

def formating(gpa_list):
    global HEADER,mods_cache
    au_weight = 0 
    for current_index , gpa_dict in enumerate(gpa_list):
        for key, value in gpa_dict.items():
            try:
                if key == 'AY':
                    gpa_dict[key] = value.strip().upper()
                elif key == 'Module':
                    gpa_dict[key] = value.strip().upper()
                #elif key == 'Description':
                    #gpa_dict[key] = mods_cache[gpa_dict["Module"]] if gpa_dict["Module"] in mods_cache else "NA"
                elif key == 'AU':
                    gpa_dict[key] = int(value.strip()) if isinstance(value,str) else value
                    au_weight+=gpa_dict[key]
                elif key == 'Grade':
                    gpa_dict[key] = value.strip().upper()
                    gpa_dict['Points'] = GRADE_SYSTEM[value]
                elif key == 'Points':
                    gpa_dict[key] = float(value.strip()) if isinstance(value,str) else value
                elif key == 'SGPA':
                    gpa_dict[key] = float(value.strip()) if isinstance(value,str) else value
                elif key == 'CGPA':
                    gpa_dict[key] = float(value.strip()) if isinstance(value,str) else value
                    calculate_cgpa(gpa_list,current_index)
                elif key == 'Weight' : 
                    #gpa_dict[key] = int(value.strip()) if isinstance(gpa_dict[key],str) else value
                    gpa_dict[key] = au_weight
            except Exception as e: 
                print(e,end='this is the error at start up\n')
                continue
        gpa_dict["Description"] = mods_cache[gpa_dict["Module"]] if gpa_dict["Module"] in mods_cache else "NA"
        if gpa_dict[key] == "NA":
            fetch_mod_code.main()
    return gpa_list 

def calculate_cgpa(gpa_list,startup_index=len(gpa_list),SGPA = False): #adding default values to prevent start up error
    au_counter =  0 
    total_points = 0.0
    for dict_index, gpa_dict in enumerate(gpa_list):
        #if 'AU' in gpa_dict and 'Points' in gpa_dict:
        if dict_index > startup_index:
            break
        if gpa_dict:
            au = gpa_dict['AU']
            points = gpa_dict['Points']
            au_counter += au
            total_points += (au * points)
            cgpa = total_points / au_counter if au_counter > 0 else 0.0
            if SGPA == False:
                gpa_list[dict_index]['CGPA'] = f"{cgpa:.2f}"
            else: 
                gpa_list[dict_index]['SGPA'] = f"{cgpa:.2f}"
            #print(au_counter,total_points,cgpa)
            #print(gpa_dict)
    return gpa_list
 
def ay()->str:
    ay_dict = {
    1: "Y1S1",
    2: "Y1S2",
    3: "Y2S1",
    4: "Y2S2",
    5: "Y3S1",
    6: "Y3S2",
    7: "Y4S1",
    8: "Y4S2"
}

    print("1.Y1S1\
            \n2.Y1S2\
            \n3.Y2S1\
            \n4.Y2S2\
            \n5.Y3S1\
            \n6.Y3S2\
            \n7.Y4S1\
            \n8.Y4S2")
    user_input = int(input("Enter AY: "))
    if user_input not in range(1,8):
        print("Invalid")
        return
    else:
        return ay_dict[user_input]
    
def updating_list(gpa_list):
    update_list = []
    for header in HEADER:
        if header == 'Module':
            user_input = input(f"{header}: ").strip().upper()
            if user_input in mods_cache:
                print (mods_cache[user_input])
        elif header == 'Grade':
            user_input = input(f"{header}: ").strip().upper()
            grade = GRADE_SYSTEM[user_input]
        elif header == 'Points':
            user_input = grade
        elif header == 'CGPA':
            user_input = 0.0
        elif header == 'Weight':
            user_input = int(0)
        elif header == 'AY':
            user_input = ay().strip()
        elif header == 'SGPA':
            user_input = 0.0
        elif header == 'AU' :
            user_input = input(f"{header}: ").strip()
            while not user_input.isdigit():
                user_input = input(f"Input not a valid integer.\n{header}: ").strip()
        if user_input == '0':
            break
        else:
            update_list.append(user_input)
    updating_dict={}
    for index, header in enumerate(HEADER):
        updating_dict[header] = update_list[index]
    #print(updating_dict)
    gpa_list.append(updating_dict)
    formating(gpa_list)
    return None

def write_file(file_path, gpa_list,description=True):
    """Writes content to a file."""
    HEADER = ['AY','Module','AU','Grade','Points','SGPA','CGPA','Weight']
    HEADER = HEADER if not description else ['AY','Module','AU','Grade','Points','SGPA','CGPA','Weight','Description']
    with open(file_path, 'w', newline='') as file:  # <-- fix here
        writer = csv.writer(file)
        writer.writerow(HEADER)
        for gpa_dict in gpa_list:
            writer.writerow([gpa_dict[key] for key in HEADER])
            
def printing_list(gpa_list): 
    for header in HEADER:
        print(header,end='  ')
    print()
    for dict in gpa_list: 
        for key in dict: 
            if key == 'Grade' and len(dict[key]) == 2: 
                print(dict[key],end='  ')
            else:
                print(dict[key],end='   ')
        print()
    return 

def menu():
    global description
    input_choice = int(input("1. Update List \
                        \n2. Print List\
                        \n3. Delete Last\
                        \n4. Save with Module Name\
                        \n5. Save without Module Name\
                        \n6. Exit\
                        \nEnter: "))
    if input_choice == 1: 
        updating_list(gpa_list)
    elif input_choice == 2: 
        printing_list(gpa_list)
    elif input_choice == 3: 
        gpa_list.pop()
    elif input_choice == 4: 
        description = True
    elif input_choice == 5:
        description = False 
    else: 
        exit()

def main(): 
    global gpa_list,mods_cache,description
    description=True
    mods_cache = fetch_mod_code.checking_cache_file(script_dir)
    read_file(file_path)
    calculate_cgpa(formating(gpa_list))
    while True: 
        menu() # every action triggers sort by ay , formatting , mod sorting and writing file
        gpa_list.sort(key = lambda temp_dict : temp_dict['AY'])  #.sort() already iterate the list hence u only need to reference the key value pair
        formating(gpa_list)         #parameter : return value
        gpa_list = mod_sorting(gpa_list)
        write_file(file_path, gpa_list,description)

GRADE_SYSTEM = {
    'A+': 5.0, 'A': 5.0, 'A-': 4.5,
    'B+': 4.0, 'B': 3.5, 'B-': 3.0,
    'C+': 2.5, 'C': 2.0, 'D+': 1.5, 
    'D': 1.0, 'F': 0.0
    }
grade_percentile = {
    "A+": (85, 100), 
    "A":  (80, 84),  
    "A-": (75, 79),  
    "B+": (70, 74),  
    "B":  (65, 69),  
    "B-": (60, 64),  
    "C+": (55, 59),
    "C":  (50, 54),
    "D+": (45, 49),
    "D":  (40, 44),
    "F":  (0, 39)
}

if __name__ == "__main__":
    main() 
    