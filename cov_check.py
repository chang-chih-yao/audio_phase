import os

input_dir = 'audio_data_path_auto_gen_patterns/'



with open('env/cust_audio_data_phase_coverage_model.sv', 'r') as f:
    coverage = f.readlines()
cov_arr = []
for cov in coverage:
    if cov.find('bins C_') != -1:
        #print(cov)
        cov_list = cov.split('C_')[-1].split(' ')[0].split('_')
        cov_list_map = map(int, cov_list)
        cov_list_int = list(cov_list_map)
        cov_arr.append(cov_list_int)
#print(cov_arr, len(cov_arr))
cov_check = [0]*len(cov_arr)


if(os.path.isdir(input_dir)):
    for dirPath, dirNames, fileNames in os.walk(input_dir):
        for f in fileNames:
            with open(os.path.join(dirPath, f), 'r') as ptr_f:
                pattern = ptr_f.readlines()

            for item in pattern:
                if item.find('expect_path_log_0') != -1:
                    path_0_str = item.split('"')[1].split(' ')
                    path_0_map = map(int, path_0_str)
                    path_0 = list(path_0_map)
                    #print(path_0)
                    
                if item.find('expect_path_log_1') != -1:
                    path_1_str = item.split('"')[1].split(' ')
                    path_1_map = map(int, path_1_str)
                    path_1 = list(path_1_map)
                    #print(path_1)
                
                if item.find("combination_idx = '") != -1:
                    combination_idx_str = item.split('{')[-1].split('}')[0].replace(',', '').split(' ')
                    combination_idx_map = map(int, combination_idx_str)
                    combination_idx = list(combination_idx_map)
                    #print(combination_idx)

            for idx in combination_idx:
                first_node = cov_arr[idx][0]
                second_node = cov_arr[idx][1]
                #print(cov_arr[idx])
                
                success_flag = False
                for i in range(len(path_0)):
                    if path_0[i] == first_node:
                        for j in range(i, len(path_0)):
                            if path_0[j] == second_node:
                                success_flag = True
                                break
                
                if success_flag == False:
                    for a in range(len(path_1)):
                        if path_1[a] == first_node:
                            for b in range(a, len(path_1)):
                                if path_1[b] == second_node:
                                    success_flag = True
                                    break
                
                if success_flag == False:
                    print('coverage ERROR!!!!')
                    print('filename:', f)
                    print('path 0:', path_0)
                    print('path 1:', path_1)
                    print('not found combination_idx:', idx)
                    exit()
                else:
                    cov_check[idx] = 1
    
#print(cov_check)
for i in range(len(cov_check)):
    if cov_check[i] == 0:
        print(i)