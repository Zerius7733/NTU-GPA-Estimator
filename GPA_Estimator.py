import os, csv ,fetch_mod_code

#file_path = (input("Enter the path to the file: ") + ".csv").strip().upper()
file_path = 'Estimated GPA.csv' #one parent dir outside of git repo
#file_path = 'Actual GPA.csv'
root_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(root_directory, file_path)
mods_cache = {}
SAVE_CSV_TO_PARENT_DIR = True #implement later
CACHE_FILE = os.path.join(os.path.dirname(__file__),"mods_cache.json")
HEADER = ['AY','Module','AU','Grade','Points','SGPA','CGPA','Weight','Description'] 
gpa_list = []
print(root_directory,end="-> Directory Path\n")
print(file_path,end= "->File Path\n")
print(CACHE_FILE)
def select_file(file_path='GPA.csv'):
    #options to edit actual gpa file, estimating gpa file, new gpa file
    print ("1.Actual GPA.csv\
            \n2.Estimated GPA.csv\n", end = '' )
    file_selection = int(input("Enter file selection:"))
    match file_selection:
        case 1: 
            return "Actual GPA.csv"
        case 2: 
            return "Estimated GPA.csv"
    return None
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
            reader = csv.reader(file)
            for line in reader:
                if not line:
                    continue
                print(line)
                # Detect header row and set HEADER from file
                if line[0].strip().upper() == 'AY' and 'Module' in line:
                    HEADER = [h.strip() for h in line]
                    continue
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

def mod_sorting(gpa_list, KEY="Module"):  # same signature
    # --- minimal safety: don't mutate caller's rows
    rows = [dict(r) for r in gpa_list]
    if not rows:
        return []

    # 1) Ensure groups are contiguous → sort by (AY, KEY)
    rows.sort(key=lambda r: (r["AY"], r[KEY]))

    temp_ay = None
    temp_list = []
    new_list = []

    for idx, row in enumerate(rows):
        # 2) Initialize current AY once
        if temp_ay is None:
            temp_ay = row["AY"]

        # 3) Append BEFORE deciding to flush (you had it after)
        temp_list.append(row)

        # 4) Decide whether to flush this AY group
        is_last = (idx == len(rows) - 1)
        next_ay = rows[idx + 1]["AY"] if not is_last else None
        need_flush = is_last or (next_ay != temp_ay)

        if need_flush:
            # keep your per-AY KEY sort
            temp_list.sort(key=lambda r: r[KEY])

            # keep your CGPA call and SGPA broadcast
            temp_list = calculate_cgpa(temp_list, True)
            temp_sgpa = temp_list[-1]['SGPA']
            for r in temp_list:
                r['SGPA'] = temp_sgpa

            new_list.extend(temp_list)

            # 5) reset group state for next AY
            temp_list = []
            temp_ay = next_ay

    return new_list


def formating(gpa_list,first_run = True):
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
                    if not first_run:
                        calculate_cgpa(gpa_list,False,current_index)
                elif key == 'Weight' : 
                    #gpa_dict[key] = int(value.strip()) if isinstance(gpa_dict[key],str) else value
                    gpa_dict[key] = au_weight
            except Exception as e: 
                print(e,end=f'this is the error at start up for key {key}\n')
                continue
        description = mods_cache[gpa_dict["Module"]] if gpa_dict["Module"] in mods_cache else "NA"
        gpa_dict["Description"] = description
        if description == "NA":
            fetch_mod_code.main()
    return gpa_list 

def calculate_cgpa(gpa_list,SGPA = False,startup_index=None): #adding default values to prevent start up error
    if startup_index is None:
        startup_index = len(gpa_list) - 1
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
    if user_input not in range(1,9):
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
    print(gpa_list)
    formating(gpa_list)
    print("after formatting\n\n" +f'{gpa_list}')
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
            elif key == "Weight" and dict[key]>= 10:
                if dict[key]>=100:
                    print(dict[key],end=' ')
                else:
                    print(dict[key],end = '  ')
            else:
                print(dict[key],end='   ')
        print()
    return 

def menu():
    global description,gpa_list
    input_choice = int(input("1. Update List \
                        \n2. Print List\
                        \n3. Delete Last\
                        \n4. Save with Module Name\
                        \n5. Save without Module Name\
                        \n6. Reload\
                        \n7. Exit\
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
    elif input_choice == 6 : 
        read_file(file_path)
        calculate_cgpa(formating(gpa_list))
    else: 
        exit()

def main(): 
    global gpa_list,mods_cache,description
    description=True
    mods_cache = fetch_mod_code.checking_cache_file(f'{root_directory}/NTU-GPA-Estimator')
    file_path = os.path.join(root_directory, select_file())
    read_file(file_path)
    calculate_cgpa(formating(gpa_list))
    while True: 
        menu() # every action triggers sort by ay , formatting , mod sorting and writing file
        gpa_list.sort(key = lambda temp_dict : temp_dict['AY'])  #.sort() already iterate the list hence u only need to reference the key value pair
        formating(gpa_list,first_run=False)         #parameter : return value
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
