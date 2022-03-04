from pickle import NONE
import re
import pandas as pd
import math
import networkx as nx
import matplotlib.pyplot as plt
from openpyxl.styles import colors
from openpyxl.styles import Font, Color
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook
from openpyxl.styles.borders import Border, Side
import math
import os.path
from sys import platform
import json
# from py2cytoscape.data.cyrest_client import CyRestClient
# from IPython.display import Image
import traceback
from networkx.readwrite import json_graph
from colorama import Fore, Back, Style
from colorama import init
import glob
import shutil
import mmap
import random
import linecache
import multiprocessing as mp
from itertools import permutations, combinations
import numpy as np
import time
from difflib import SequenceMatcher
import pickle

########################## global settings ##########################
SIGNATURE = '/*********** Howard Auto Gen Tools ***********/\n'
COMPONENT_NAME_COLUMN_NAME = '主圖形名稱'
BACKUP_DIR  = 'backup'
INPUT_DIR   = 'input'
ENV_DIR     = 'env'
CONTENT_DIR = 'env_content'
DATA_DIR    = 'data'
PATTERN_DIR = 'audio_data_path_auto_gen_patterns'
CHECK_LOG_DIR = 'check_log'
REPORT_DIR  = 'report'
NULL_NODE_ID = -1
TAB = '    '
SELECT_SIGNAL_RESERVED = 'reserved'
REG_READ_WRITE_CMD_ADDR = 'UVM_ADDR'
REG_READ_WRITE_CMD_DATA = 'UVM_DATA'
REG_READ_WRITE_VARIABLE = 'UVM_VARIABLE'
REG_READ_WRITE_VARIABLE_NAME = 'data_tmp'
RESERVED_SELECT_SIGNAL = SELECT_SIGNAL_RESERVED
OFFSET_SELECT_SIGNAL   = '_offset_'
FOR_SD_CHECK_ONLY = False

########################## global settings ##########################

def is_windows():
    if platform == "win32":
        return True
    return False

class ALL_PATH:
    def __init__(self, all_path_file):
        self.file           = open(all_path_file, "r+b")
        self.file_name      = all_path_file
        self.all_path_mmap  = mmap.mmap(self.file.fileno(), 0)
        self.num_path       = self.get_last_path_id() + 1
        self.file_size      = self.get_file_size()
        
    def mmap(self):
        self.all_path_mmap = mmap.mmap(self.file.fileno(), 0)
        
    def unmmap(self):
        self.all_path_mmap.close()
        
    def get_file_size(self):
        self.file.seek(0, os.SEEK_END)
        return self.file.tell()
        
    def get_last_path_id(self):
        with open(self.file_name, "rb") as file:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'P':
                file.seek(-2, os.SEEK_CUR)
            last_line = file.readline().decode('UTF-8')
        try:
            last_path_id = int(re.search(r'\[*[0-9]+\]', last_line).group(0).replace('[','').replace(']', ''))
        except:
            print('ALL_PATH.h() error, last line is "{}"'.format(last_line))
            
        return last_path_id
        
    def get_path_by_id(self, id):
        line = linecache.getline(self.file_name, id + 1)
        path = (line[line.find(':')+1:]).split()
        path = list(map(int, path))
        return path
        
    def get_edges_by_path_id(self, id):
        path = self.get_path_by_id(id)
        edges = []
        for idx in range(len(path)-1):
            edges.append((path[idx], path[idx+1]))

        return edges
        
    def get_random_path_id_list(self, req_num):
        sample_range = range(self.num_path - req_num ) if self.num_path - req_num > 0 else range(self.num_path)
        random_start_pos = random.sample(sample_range, 1)[0]
        return range(random_start_pos, random_start_pos + req_num)
        
    def get_random_path_list(self, req_num):
        id_list   = self.get_random_path_id_list(req_num)
        path_list = []
        for id in id_list:
            path_list.append(self.get_path_by_id(id))
        return path_list, id_list
        
    def find(self, find_pattern):
        self.mmap()
        self.all_path_mmap.seek(0)
        result = self.all_path_mmap.find(find_pattern)
        self.unmmap()
        
        return result
        
    def find_byte(self, byte, pos, IS_FORWARD = True):
        result = pos

        while result > 0 and result < self.file_size:
            self.all_path_mmap.seek(result)
            cur_byte = self.all_path_mmap.read(1)
            if cur_byte == byte:
                break
            else:
                if IS_FORWARD:
                    result -= 1
                else:
                    result += 1
        
        return result
        
    def get_path_by_pos(self, pos):
        self.mmap()
    
        line_start = self.find_byte(b'P', pos)
        if(is_windows()):
            line_end = self.find_byte(b'\r', pos, False) - 1
        else:
            line_end = self.find_byte(b'\n', pos, False) - 1
            
        path_idx = -1
        path = []
        
        line = self.all_path_mmap[line_start:line_end].decode('UTF-8')
        print(line)
        
        path = (line[line.find(':')+1:]).split()
        path = list(map(int, path))
        path_idx = int(re.search(r'\[*[0-9]+\]', line).group(0).replace('[','').replace(']', ''))
        self.unmmap()

        return path_idx, path

    #def get_each_path_pos_in_file(self):
    #    self.all_path_mmap.seek(0, os.SEEK_SET)
    #    for line in iter(self.all_path_mmap.readline, b""):
    #        self.path_pos_list.append(self.all_path_mmap.tell())
    #        print(self.all_path_mmap.tell())
        


def split_list(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

def list_to_string(list):
    result = ""
    for item in list:
        result += ' {}'.format(str(item))
    result = result[1:]
    
    return result

def COLOR_MESSAGE(message, SETTINGS):
    #init()
    #print(SETTINGS + message + Style.RESET_ALL)
    print(message)

def WARNING_MESSAGE(message):
    SETTINGS = Style.BRIGHT + Fore.YELLOW
    COLOR_MESSAGE(WARNING_LOG(message), SETTINGS)

def ERROR_MESSAGE(message):
    SETTINGS = Style.BRIGHT + Fore.RED
    COLOR_MESSAGE(ERROR_LOG(message), SETTINGS)
    
def PASS_MESSAGE(message = 'PASS\n'):
    SETTINGS = Style.BRIGHT + Fore.GREEN
    COLOR_MESSAGE(message, SETTINGS)
    
def FAIL_MESSAGE(message = 'FAIL\n'):
    SETTINGS = Style.BRIGHT + Fore.RED
    COLOR_MESSAGE(message, SETTINGS)
    
def WARNING_LOG(LOG):
    return '[WARNING] ' + LOG
    
def ERROR_LOG(LOG):
    return '[ERROR] ' + LOG
                
def contents_append_endl(CONTENTS, tmp):
    CONTENTS.append(tmp + '\n')
    
def contents_append_tab_endl(CONTENTS, tmp):
    CONTENTS.append(TAB + tmp + '\n')
    
def contents_append_tab_tab_endl(CONTENTS, tmp):
    CONTENTS.append(TAB + TAB + tmp + '\n')
    
def contents_append_tab_tab_tab_endl(CONTENTS, tmp):
    CONTENTS.append(TAB + TAB + TAB + tmp + '\n')
    
def file_with_dir_path(output_file_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, output_file_name)
    
def erase_file_contents(output_file_name, output_dir):
    output_file_name = file_with_dir_path(output_file_name, output_dir)
    open(output_file_name, "w").close()
    
def write_contents_to_file(CONTENTS, output_file_name, output_dir, IS_APPEND_MODE = False, ENDL = '\n'):
    output_file_name = file_with_dir_path(output_file_name, output_dir)
   
    if IS_APPEND_MODE:
        output_file = open(output_file_name, "a", encoding = "UTF-8")
    else:
        output_file = open(output_file_name, "w", encoding = "UTF-8")

    for content in CONTENTS:
        output_file.write(content + ENDL)
    output_file.close()

def backup_file(file_name, backup_dir = BACKUP_DIR):
    new_file_name =  file_name[file_name.rfind('\\')+1:file_name.find('.')] + '_bk'
    new_file_name += file_name[file_name.find('.'):]
    
    new_file_name = file_with_dir_path(new_file_name, backup_dir)
    
    print('back up {} to {}'.format(file_name, new_file_name))
    
    if platform == "linux" or platform == "linux2":
        os.system('cp {} {}'.format(file_name, new_file_name))  
    elif platform == "win32":
        os.system('copy {} {}'.format(file_name, new_file_name)) 
        
def regex_filter(val, regex):
    if val:
        try:
            mo = re.search(regex, val)
        except:
            mo = False
        if mo:
            return True
        else:
            return False
        
    else:
        return False
        
def fill_component_info(one_component_dict, component, i, component_data_frame, IN_PATTERN, OUT_PATTERN, SELECT_PATTERN, SPLIT_POSTFIX = ''):    
    ## parse Out
    try:
        columns_list = list(filter(re.compile(OUT_PATTERN).match, component_data_frame.columns)) 
        output_list = []
        for column in columns_list:
            if str(component_data_frame.iloc[i][column]) != 'nan':
                output = component_data_frame.iloc[i][column].lower()
                output_list.append(output)
                #print('{}: {}'.format(column, component_data_frame.iloc[i][column]))
        one_component_dict.update({'Outputs': output_list})
    except:
        #traceback.print_exc()
        #print('No Out')
        one_component_dict.update({'Outputs': []})
        
    ## case 0: there is a reserved select signal
    ## case 1: there is n-1 offset select signal and 1 non-offset select signal
    CASE0 = False
    CASE1 = False
    CASE0_INPUT_IDX = -1
    CASE1_INPUT_IDX = -1
    num_offset_select_signal     = 0
    num_non_offset_select_signal = 0
    
    ## parse Select
    try:
        columns_list = list(filter(re.compile(SELECT_PATTERN).match, component_data_frame.columns))
        select_list = []
        
        ## check case 0
        for idx, column in enumerate(columns_list):
            if str(component_data_frame.iloc[i][column]) != 'nan':
                select = component_data_frame.iloc[i][column].lower()
                if select == RESERVED_SELECT_SIGNAL:
                    CASE0_INPUT_IDX = idx
                    CASE0 = True
                else:
                    if select.find(OFFSET_SELECT_SIGNAL) != -1:
                        num_offset_select_signal += 1
                    else:
                        num_non_offset_select_signal += 1
                        CASE1_INPUT_IDX = idx
        
        for idx, column in enumerate(columns_list):
            if str(component_data_frame.iloc[i][column]) != 'nan':
                select = component_data_frame.iloc[i][column].lower()
                select_list.append(select)

        #print(num_offset_select_signal)
        #print(num_non_offset_select_signal)
        #print('\n')
        if num_non_offset_select_signal == 1 and num_offset_select_signal > 0 and num_offset_select_signal + num_non_offset_select_signal == len(select_list):
            CASE1 = True
            
        #if CASE0:
        #    print('CASE0')
        #    print(select_list)
        
        #if CASE1:
        #    print('CASE1')
        #    print(select_list)

        if CASE0:
            one_component_dict.update({'Not_Covered_Select': select_list})
            select_list = []
            one_component_dict.update({'Type': one_component_dict['Type'] + '_with_reserved'})
        elif CASE1:
            one_component_dict.update({'Not_Covered_Select': select_list})
            select_list = []
            one_component_dict.update({'Type': one_component_dict['Type'] + '_with_offset'})
            
        one_component_dict.update({'Selects': select_list})
        
        if str(component['Select']).find('Mute') != -1:
            one_component_dict.update({'IS_REVERSE': True})
        else:
            one_component_dict.update({'IS_REVERSE': False})
            
    except:
        #traceback.print_exc()
        #print('No Select')
        one_component_dict.update({'Selects': []})
        
            
    ## parse In
    try:
        columns_list = list(filter(re.compile(IN_PATTERN).match, component_data_frame.columns))
        input_list = []
        not_covered_input_list = []
        for idx, column in enumerate(columns_list):
            if str(component_data_frame.iloc[i][column]) != 'nan':
                input = component_data_frame.iloc[i][column].lower()
                if CASE0:
                    if idx == CASE0_INPUT_IDX:
                        input_list.append(input)
                    else:
                        not_covered_input_list.append(input)
                elif CASE1:
                    if idx == CASE1_INPUT_IDX:
                        input_list.append(input)
                    else:
                        not_covered_input_list.append(input)
                else:
                    input_list.append(input)
                #print('{}: {}'.format(column, component_data_frame.iloc[i][column]))
        one_component_dict.update({'Inputs': input_list})
        if CASE0 or CASE1:
            one_component_dict.update({'Not_Covered_Inputs': not_covered_input_list})
    except:
        #traceback.print_exc()
        #print('No In')
        one_component_dict.update({'Inputs': []})

    return one_component_dict
    
def get_components_parsing_rule(input_file_name = 'components_parsing_rule.json', input_dir = INPUT_DIR):
    input_file_name = file_with_dir_path(input_file_name, input_dir)
    
    with open(input_file_name) as json_file: 
        components_parsing_rule = json.load(json_file)
        
    return components_parsing_rule
    
def get_components_info(components_parsing_rule, input_file_name = 'all.xlsx', input_dir = INPUT_DIR, replace_dot = True):
    print('--------- Parsing Start ---------')
    components_file = file_with_dir_path(input_file_name, input_dir)
    excel_df = pd.read_excel(components_file, skiprows=[0])
    df = pd.DataFrame(excel_df)
    components_info = []
    
    total_got = 0

    for component in components_parsing_rule:
        print("components_info length: {}".format(len(components_info)))
        component_data_frame = df.loc[df[COMPONENT_NAME_COLUMN_NAME].apply(regex_filter, regex=component['Name'])]
        total_got += len(component_data_frame)
        print('Got {} {}'.format(len(component_data_frame), component['Name']))
        for i in range(0, len(component_data_frame)):
            type = component_data_frame.iloc[i][COMPONENT_NAME_COLUMN_NAME]
            if replace_dot:
                type = re.sub(r"\.[0-9]+", "", type)
            #print(component_data_frame.iloc[i][COMPONENT_NAME_COLUMN_NAME])
            
            if 'MulOut_NoSel' in component:
                for idx, split in enumerate(component['MulOut_NoSel']):
                    one_component_dict = {'Type': type + '_' + split, 'IS_REVERSE': False}
                    one_component_dict = fill_component_info(one_component_dict, component, i, component_data_frame, component['In'][idx], component['Out'][idx], component['Select'], SPLIT_POSTFIX = split)
                    components_info.append(one_component_dict)
            else:    
                one_component_dict = {'Type': type, 'IS_REVERSE': False}
                one_component_dict = fill_component_info(one_component_dict, component, i, component_data_frame, component['In'], component['Out'], component['Select'])
                components_info.append(one_component_dict)

    print('--------- Parsing Summary: got total {} components ---------\n'.format(total_got))
    return components_info
    
def set_components_id(components_info):
    for idx, component_info in enumerate(components_info):
        component_info.update({"NODE_ID": str(idx)})
        
    return components_info
    
def to_lower(components_info):
    for component_info in components_info:
        for input in component_info['Inputs']:
            input = input.lower()
            
        for output in component_info['Outputs']:
            output = output.lower()
              
        for select in component_info['Selects']:
            select = select.lower()
    return components_info
    
def make_legal(components_info, ilegal_pattern = r"[^a-z0-9_]", replace_with = '_'):
    for component_idx, component_info in enumerate(components_info):
        for idx, input in enumerate(component_info['Inputs']):
            old = input
            new = re.sub(ilegal_pattern, replace_with, old, count=100)
            if old != new:
                WARNING  = 'component[%3s] input  naming illegal, ' % component_idx
                WARNING += 'auto changed from %35s' % old
                WARNING += ' to %35s' % new
                WARNING_MESSAGE(WARNING)
                component_info['Inputs'][idx] = new
            
        for idx, output in enumerate(component_info['Outputs']):
            old = output
            new = re.sub(ilegal_pattern, replace_with, old, count=100)
            if old != new:
                WARNING  = 'component[%3s] output naming illegal, ' % component_idx
                WARNING += 'auto changed from %35s' % old
                WARNING += ' to %35s' % new
                WARNING_MESSAGE(WARNING)
                component_info['Outputs'][idx] = new
              
        for idx, select in enumerate(component_info['Selects']):
            old = select
            new = re.sub(ilegal_pattern, replace_with, old, count=100)
            if old != new:
                WARNING  = 'component[%3s] select naming illegal, ' % component_idx
                WARNING += 'auto changed from %35s' % old
                WARNING += ' to %35s' % new
                WARNING_MESSAGE(WARNING)
                component_info['Selects'][idx] = new
            
    return components_info
    
def make_distinct(components_info):
    new_components_info = components_info.copy()
    #for idx, x in enumerate(new_components_info):
    #    for y in new_components_info[idx+1:]:
    #        if x['Type'] == y['Type'] and x['Inputs'] == y['Inputs'] and x['Outputs'] == y['Outputs'] and x['Selects'] == y['Selects']:
    #            new_components_info.remove(y)
    #            
    #WARNING_MESSAGE("make dinstinct result, ori({}), new({})".format(len(components_info), len(new_components_info)))
    return new_components_info
    
def sort_components_info(components_info):
    newlist = sorted(components_info, key=lambda k: k['Type']) 
    return newlist
    
def check_single_output(components_info, output_file_name = 'check_single_output.txt', output_dir = CHECK_LOG_DIR):
    PASS = True
    CONTENTS = []
    for idx, component_info in enumerate(components_info):
        if len(component_info['Outputs']) > 1:
            PASS = False
            component_id   = '%3s'  % idx
            component_type = '%35s' % component_info['Type']
            
            outputs = ''
            for output in component_info['Outputs']:
                outputs += output + ' '

            LOG = 'Error: : component[{}]({}) has multiple outputs: {}'.format(component_id, component_type, outputs)
            CONTENTS.append(LOG)
            print(LOG)
            
    write_contents_to_file(CONTENTS, output_file_name, output_dir)        
    return PASS
 
def check_output_distinct(components_info, output_file_name = 'check_output_distinct.txt', output_dir = CHECK_LOG_DIR):
    PASS = True
    CONTENTS = []
    for idx_x, x in enumerate(components_info):
        for idx_y, y in enumerate(components_info):
            if idx_x < idx_y:
                for x_output in x['Outputs']:
                    for y_output in y['Outputs']:
                        if x_output == y_output:
                            PASS = False
                            component_id_x   = '%3s'  % idx_x
                            component_type_x = '%35s' % x['Type']
                            component_id_y   = '%3s'  % idx_y
                            component_type_y = '%35s' % y['Type']
                            output_signal    = '%35s' % x_output
                            LOG = 'Error: component[{}]({}) and component[{}]({}) output: {} are the same'.format(component_id_x, component_type_x, component_id_y, component_type_y, output_signal)
                            ERROR_MESSAGE(LOG)
                            CONTENTS.append(ERROR_LOG(LOG))
                            
    write_contents_to_file(CONTENTS, output_file_name, output_dir)      
    return PASS
    
def check_output_connection(components_info, output_file_name = 'check_output_connection.txt', output_dir = CHECK_LOG_DIR):
    PASS = True
    CONTENTS = []
    for idx, component_info in enumerate(components_info):
        if len(component_info['Outputs']) == 1 :
            output = component_info['Outputs'][0]
            Found = False
            for idx_y, y in enumerate(components_info):
                for input in y['Inputs']:
                    if input == output:
                        Found = True
                        break
            if not Found:
                PASS = False
                component_id   = '%3s'  % idx
                component_type = '%35s' % component_info['Type']
                output_signal  = '%35s' % output
                LOG = 'no_connection: output({}) of component[{}]({})'.format(output_signal, component_id, component_type)
                CONTENTS.append(ERROR_LOG(LOG))
                ERROR_MESSAGE(LOG)
        
    write_contents_to_file(CONTENTS, output_file_name, output_dir)
    return PASS
    
def check_input_connection(components_info, output_file_name = 'check_input_connection.txt', output_dir = CHECK_LOG_DIR):
    PASS = True
    CONTENTS = []
    input_signals = [SELECT_SIGNAL_RESERVED]
    
    for input_node in components_info:
        if input_node['Type'] == 'Input_Node':
            input_signals.append(input_node['Outputs'][0])
            
    for idx_y, y in enumerate(components_info):
        for input in y['Inputs']:
            if input not in input_signals:
                Found = False
                for idx_x, x in enumerate(components_info):
                    if len(x['Outputs']) == 1 :
                        output = x['Outputs'][0]
                        if input == output:
                            Found = True
                            break
                            
                if not Found:
                    PASS = False
                    component_id   = '%3s'  % idx_y
                    component_type = '%35s' % y['Type']
                    input_signal   = '%45s'  % input
                    LOG = 'no_connection: input({}) of component[{}]({})'.format(input_signal, component_id, component_type)
                    WARNING_MESSAGE(LOG)
                    CONTENTS.append(WARNING_LOG(LOG))
        
    write_contents_to_file(CONTENTS, output_file_name, output_dir)
    #return PASS
    return True
    
def check_select_and_input_num(components_info, output_file_name = 'check_select_and_input_num.txt', output_dir = CHECK_LOG_DIR):
    PASS = True
    CONTENTS = []
    
    for idx, component_info in enumerate(components_info):
        input_num  = len(component_info['Inputs'])
        select_num = len(component_info['Selects'])
        ## 要嘛數量相等 要嘛只有一個 mul-bit select siganl
        if (input_num != select_num) and not (input_num == 1 and select_num == 0):
            if select_num != 1:
                PASS = False
                component_id   = '%3s'  % idx
                component_type = '%35s' % component_info['Type']
                component_input_num  = '%3s' % input_num
                component_select_num = '%3s' % select_num
                LOG = 'INPUT NUM and SELECT NUM CONFLICT: component[{}]({}) input_num = {}, select_num = {}'.format(component_id, component_type, component_input_num, component_select_num)
                CONTENTS.append(LOG)
                print(LOG)
                
    write_contents_to_file(CONTENTS, output_file_name, output_dir)
    return PASS
    
def check_select_in_all_register_info(components_info, all_register_info, output_file_name = 'check_select_in_all_register_info.txt', output_dir = CHECK_LOG_DIR):
    PASS = True
    CONTENTS = []
    
    for idx, component_info in enumerate(components_info):
        for select_signal in component_info['Selects']:
            if select_signal != SELECT_SIGNAL_RESERVED and select_signal not in all_register_info:
                component_select_signal = '%35s' % select_signal
                PASS = False
                LOG = 'select signal({}) not found in all_register_info'.format(component_select_signal)
                CONTENTS.append(ERROR_LOG(LOG))
                ERROR_MESSAGE(LOG)  

    write_contents_to_file(CONTENTS, output_file_name, output_dir)
    return PASS
    
def check_select_distinct(components_info, output_file_name = 'check_select_distinct.txt', output_dir = CHECK_LOG_DIR):
    PASS = True
    CONTENTS = []
    for idx_x, x in enumerate(components_info):
        for idx_y, y in enumerate(components_info):
            if idx_x < idx_y:
                for x_select in x['Selects']:
                    for y_select in y['Selects']:
                        if x_select == y_select:
                            PASS = False
                            component_id_x   = '%3s'  % idx_x
                            component_type_x = '%35s' % x['Type']
                            component_id_y   = '%3s'  % idx_y
                            component_type_y = '%35s' % y['Type']
                            select_signal    = '%35s' % x_select
                            LOG = 'component[{}]({}) and component[{}]({}) select: {} are the same'.format(component_id_x, component_type_x, component_id_y, component_type_y, select_signal)
                            CONTENTS.append(WARNING_LOG(LOG))
                            #WARNING_MESSAGE(LOG)
                            
    write_contents_to_file(CONTENTS, output_file_name, output_dir)      
    return PASS
    
def check_pow_of_2(n):
    return n & (n-1) == 0
    
def check_components_info_and_all_register_info(components_info, all_register_info, output_file_name = 'check_components_info_and_all_register_info.txt', output_dir = CHECK_LOG_DIR):
    PASS = True
    CONTENTS = []
    
    for idx, component_info in enumerate(components_info):
        input_num  = len(component_info['Inputs'])
        select_num = len(component_info['Selects'])
        
        ## 確認 mul-bit select siganl
        if input_num != select_num and not (input_num == 1 and select_num == 0) and select_num == 1:
            select_signal = component_info['Selects'][0]
            component_select_signal = '%35s' % select_signal
            if select_signal in all_register_info:
                signal_width  = all_register_info[select_signal]['Length']
                component_id   = '%3s'  % idx
                component_type = '%35s' % component_info['Type']
                component_input_num    = '%3s' % input_num
                component_signal_width = '%3s' % signal_width

                LOG = 'input num and select signal({}) width conflict: component[{}]({}) input_num = {}, signal_width = {}'.format(component_select_signal, component_id, component_type, component_input_num, component_signal_width)
                
                if input_num > math.pow(2, signal_width):
                    PASS = False
                    CONTENTS.append(ERROR_LOG(LOG))
                    ERROR_MESSAGE(LOG)
                elif input_num != math.pow(2, signal_width) and check_pow_of_2(input_num):
                    CONTENTS.append(WARNING_LOG(LOG))
                    WARNING_MESSAGE(LOG)
            else:
                PASS = False
                LOG = 'select signal({}) not found in all_register_info'.format(component_select_signal)
                CONTENTS.append(ERROR_LOG(LOG))
                ERROR_MESSAGE(LOG)

    write_contents_to_file(CONTENTS, output_file_name, output_dir)
    return PASS
    
def get_select_signals_and_ports(components_info):
    ports   = []
    signals = []
    for component_info in components_info:
        input_num  = len(component_info['Inputs'])
        select_num = len(component_info['Selects'])
         
        if select_num > 0 and input_num > select_num:
            signal = component_info['Selects'][0]
            port_upper_bound = int(math.log(input_num, 2))-1 if check_pow_of_2(input_num) else int(math.log(input_num, 2))
            
            if port_upper_bound > 0:
                port   = 'logic [{}:0]{}'.format(port_upper_bound, signal)
            else:
                port   = 'logic {}'.format(signal)
                
            signals.append(signal)
            ports.append(port)
        else:
            for signal in component_info['Selects']:
                port = 'logic {}'.format(signal)
                signals.append(signal)
                ports.append(port)
                
    ports   = sorted(list(set(ports)))
    signals = sorted(list(set(signals)))
    
    return signals, ports
    
def get_nodes_by_type(components_info, type):
    nodes = []
    for component_info in components_info:
        if component_info['Type'] == type:
            nodes.append(component_info)
            
    return nodes
    
def gen_dut_wrapper(components_info, output_file_name = 'dut_wrapper.sv', output_dir = CONTENT_DIR):
    CONTENTS = []
    contents_append_endl(CONTENTS, SIGNATURE)
    signals, ports = get_select_signals_and_ports(components_info)
    
    contents_append_endl(CONTENTS, '// ****** audio data path VIP connection start ****** //')
    
    contents_append_endl(CONTENTS, '// select signals connection')
    for signal in signals:
        contents_append_endl(CONTENTS, '//assign audio_data_path_dump_mux_if_0.{}'.format(signal).ljust(70) + ' = ;')
        
    contents_append_endl(CONTENTS, '')
    contents_append_endl(CONTENTS, '')
    
    contents_append_endl(CONTENTS, '// output data signals connection')
    for idx, output_node in enumerate(get_nodes_by_type(components_info, 'Output_Node')):
        contents_append_endl(CONTENTS, '//output: {}'.format(output_node['Inputs'][0]))
        contents_append_endl(CONTENTS, '//assign audio_data_path_dump_data_if_0_{}.rreq'.format(idx).ljust(70) + ' = ;')
        contents_append_endl(CONTENTS, '//assign audio_data_path_dump_data_if_0_{}.data'.format(idx).ljust(70) + ' = ;')
        contents_append_endl(CONTENTS, '')
        
    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')
    
def gen_system_base_test(components_info, output_file_name = 'system_base_test.sv', output_dir = CONTENT_DIR):
    CONTENTS = []
    contents_append_endl(CONTENTS, SIGNATURE)
    
    contents_append_tab_endl(CONTENTS, '// ****** audio data path VIP source info start ****** //')
   
    for idx, input_node in enumerate(get_nodes_by_type(components_info, 'Input_Node')):
        contents_append_tab_endl(CONTENTS, '//input: {}'.format(input_node['Outputs'][0]))
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].add_perf_struct(%3s, );' % idx)
        contents_append_endl(CONTENTS, '')
    
    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')

def gen_content_of_cust_system_configuration(components_info, output_file_name = 'cust_system_configuration.sv', output_dir = CONTENT_DIR):
    CONTENTS = []
    contents_append_endl(CONTENTS, SIGNATURE)
    input_nodes  = get_nodes_by_type(components_info, 'Input_Node')
    output_nodes = get_nodes_by_type(components_info, 'Output_Node')
    
    contents_append_tab_endl(CONTENTS, '/************ audio data path settings begin ************/')
    contents_append_tab_endl(CONTENTS, 'this.audio_data_path_cfg[0].source_num ' + '%19s' % '= {};'.format(len(input_nodes)) + '// # of input node')
    contents_append_tab_endl(CONTENTS, 'this.audio_data_path_cfg[0].channel_num' + '%19s' % '= {};'.format(len(output_nodes)) + '// # of output node')
    contents_append_tab_endl(CONTENTS, 'this.audio_data_path_cfg[0].create_sub_cfgs();')
    contents_append_endl(CONTENTS, '')
    
    contents_append_tab_endl(CONTENTS, '// input nodes')
    for idx, input_node in enumerate(input_nodes):
        contents_append_tab_endl(CONTENTS, 'this.audio_data_path_cfg[0].source_name[%3s]' % idx + '%11s' % '= ' + '"{}";'.format(input_node['Outputs'][0]))
    contents_append_endl(CONTENTS, '')
    
    contents_append_tab_endl(CONTENTS, '// output nodes')
    for idx, output_node in enumerate(output_nodes):
        contents_append_tab_endl(CONTENTS, 'this.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].channel_name' % idx + ' = "{}";'.format(output_node['Inputs'][0]))
    contents_append_endl(CONTENTS, '')
    
    contents_append_tab_endl(CONTENTS, '/************* audio data path settings end *************/')
    
    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')
    
def gen_audio_data_path_golden_pattern(components_info, output_file_name = 'audio_data_path_golden.sv', output_dir = CONTENT_DIR):
    CONTENTS = []
    contents_append_endl(CONTENTS, SIGNATURE)
    output_nodes = get_nodes_by_type(components_info, 'Output_Node')
    
    contents_append_tab_endl(CONTENTS, '/************ audio data path settings begin ************/')
    contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_enable = 1;')
    contents_append_endl(CONTENTS, '')
    
    for idx, output_node in enumerate(output_nodes):
        contents_append_tab_endl(CONTENTS, '// performance check setting of output: {}'.format(output_node['Inputs'][0]))
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].channel_enable     = 0;' % idx)
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].is_dwa             = 0;' % idx)
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].sample_bit         = AUDIO_DATA_PATH_SAMPLE_BIT_16;' % idx)
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].sample_rate        = AUDIO_DATA_PATH_SAMPLE_RATE_48K;' % idx)
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].fs                 = 6144000;' % idx)
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].sample_num         = 320000;' % idx)
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].discard_sample_num = 128000;' % idx)
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].thd_threshold      = -90;' % idx)
        contents_append_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].amp_threshold      = -8.5;' % idx)
        contents_append_endl(CONTENTS, '')
    
    contents_append_tab_endl(CONTENTS, '/************* audio data path settings end *************/')
    
    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')

def gen_transition_model(components_info, output_file_name = 'cust_audio_data_path_transition_model.sv', output_dir = ENV_DIR, output_enable = True):
    CONTENTS = []
    contents_append_endl(CONTENTS, SIGNATURE)
    ###################################### class init ######################################
    contents_append_endl(CONTENTS, '`ifndef CUST_AUDIO_DATA_PATH_TRANSITION_MODEL__SV')
    contents_append_endl(CONTENTS, '`define CUST_AUDIO_DATA_PATH_TRANSITION_MODEL__SV')
    contents_append_endl(CONTENTS, 'class cust_audio_data_path_transition_model extends audio_data_path_transition_model #(cust_audio_data_path_dump_mux_transaction);')
    contents_append_tab_endl(CONTENTS, '`uvm_object_utils_begin(cust_audio_data_path_transition_model)')
    contents_append_tab_endl(CONTENTS, '`uvm_object_utils_end')
    contents_append_tab_endl(CONTENTS, 'extern function new(string name = "cust_audio_data_path_transition_model");')
    contents_append_tab_endl(CONTENTS, 'extern function int transition(ref cust_audio_data_path_dump_mux_transaction tr, int destination_id);')
    contents_append_tab_endl(CONTENTS, 'extern function int selection(ref cust_audio_data_path_dump_mux_transaction tr, int node_id);')
    contents_append_endl(CONTENTS, 'endclass: cust_audio_data_path_transition_model')
    ###################################### class init ######################################
    
    contents_append_endl(CONTENTS, "")
    
    ####################################### tree init #######################################
    contents_append_endl(CONTENTS, 'function cust_audio_data_path_transition_model::new(string name = "cust_audio_data_path_transition_model");')
    contents_append_tab_endl(CONTENTS, 'super.new(name);')
    
    contents_append_tab_endl(CONTENTS, 'select_tree = new[{}](select_tree);'.format(len(components_info)))
    for component_info in components_info:
        INPUT_NUM        = len(component_info['Inputs'])
        SELECT_TREE_NODE = 'select_tree[{}]'.format(component_info['NODE_ID'])
        
        contents_append_endl(CONTENTS, '\n' + TAB + '// Type:   {}'.format(component_info['Type']))
        for input in component_info['Inputs']:
            contents_append_tab_endl(CONTENTS, '// Input:  {}'.format(input))
        for output in component_info['Outputs']:
            contents_append_tab_endl(CONTENTS, '// Output: {}'.format(output))
        
        if INPUT_NUM > 0:
            contents_append_tab_endl(CONTENTS, '{}.select = new[{}];'.format(SELECT_TREE_NODE, INPUT_NUM))
            contents_append_tab_endl(CONTENTS, '{}.select_done = new[{}];'.format(SELECT_TREE_NODE, INPUT_NUM))
            for i in range(INPUT_NUM):
                contents_append_tab_endl(CONTENTS, '{}.select[{}] = -1;'.format(SELECT_TREE_NODE, str(i)))
            for i in range(INPUT_NUM):
                contents_append_tab_endl(CONTENTS, "{}.select_done[{}] = 1'b0;".format(SELECT_TREE_NODE, str(i)))
        else:
            contents_append_tab_endl(CONTENTS, '{}.select = new[{}];'.format(SELECT_TREE_NODE, 1))
            contents_append_tab_endl(CONTENTS, '{}.select_done = new[{}];'.format(SELECT_TREE_NODE, 1))
            contents_append_tab_endl(CONTENTS, '{}.select[{}] = -2;'.format(SELECT_TREE_NODE, 0))
            contents_append_tab_endl(CONTENTS, "{}.select_done[{}] = 1'b0;".format(SELECT_TREE_NODE, 0))
            
        contents_append_tab_endl(CONTENTS, '{}.source = -1;'.format(SELECT_TREE_NODE))
    ####################################### tree init #######################################

    contents_append_endl(CONTENTS, "\n")    
        
    #################################### tree connection ####################################
    for child in components_info:
        SELECT_TREE_NODE = 'select_tree[{}]'.format(child['NODE_ID'])

        child_select_parents_node_id = []
        child_input_cnt = 0
        for input in child['Inputs']:
            INPUT_FOUND = False
            for parent in components_info:
                if len(parent['Outputs']) > 0:
                    if input == parent['Outputs'][0]:
                        child_select_parents_node_id.append(int(parent['NODE_ID']))
                        contents_append_tab_endl(CONTENTS, '{}.select[{}] = {}; //connection: {}'.format(SELECT_TREE_NODE, str(child_input_cnt), parent['NODE_ID'], input))
                        INPUT_FOUND = True
            if not INPUT_FOUND:
                child_select_parents_node_id.append(NULL_NODE_ID)
                
            child_input_cnt += 1
        child.update({'select': child_select_parents_node_id})
    #################################### tree connection ####################################
    
    ################################### source connection ###################################
    NUM_INPUT_NODE = 0
    for component in components_info:
        if component['Type'] == 'Input_Node':
            SELECT_TREE_NODE = 'select_tree[{}]'.format(component['NODE_ID'])
            output = component['Outputs'][0]
            contents_append_tab_endl(CONTENTS, '{}.source = {}; //input: {}'.format(SELECT_TREE_NODE, NUM_INPUT_NODE, output))
            NUM_INPUT_NODE += 1
    ################################### source connection ###################################
    
    contents_append_endl(CONTENTS, "\nendfunction: new\n")
    
    ###################################### tree transition ######################################
    contents_append_endl(CONTENTS, "/** transition for cust_audio_data_path_transition_model */")
    contents_append_endl(CONTENTS, 'function int cust_audio_data_path_transition_model::transition(ref cust_audio_data_path_dump_mux_transaction tr, int destination_id);')
    contents_append_tab_endl(CONTENTS, 'int select, select_tmp;')
    contents_append_endl(CONTENTS, '')
    contents_append_tab_endl(CONTENTS, '`uvm_info("selection", $sformatf("destination id: %0d", destination_id), UVM_LOW)')
    contents_append_tab_endl(CONTENTS, '`uvm_info("AUDIO_DATA_PATH_DUMP_MUX", tr.sprint(), UVM_DEBUG)')
    contents_append_endl(CONTENTS, '')
    destination_id = 0
    for component in components_info:
        if component['Type'] == 'Output_Node':
            NODE_ID = component['NODE_ID']
            input = component['Inputs'][0]
            if destination_id == 0:
                contents_append_tab_endl(CONTENTS, 'if(destination_id == {})'.format(destination_id))
            else:
                contents_append_tab_endl(CONTENTS, 'else if(destination_id == {})'.format(destination_id))
            contents_append_tab_tab_endl(CONTENTS, 'select = {};//output: {}'.format(NODE_ID, input))

            destination_id += 1
    contents_append_tab_endl(CONTENTS, 'else')
    contents_append_tab_tab_endl(CONTENTS, 'select = -1;')
    contents_append_endl(CONTENTS, '')
    contents_append_tab_endl(CONTENTS, 'foreach(select_tree[i]) begin')
    contents_append_tab_tab_endl(CONTENTS, 'select_tree[i].done = 0;')
    contents_append_tab_endl(CONTENTS, 'end')
    contents_append_endl(CONTENTS, '')
    contents_append_tab_endl(CONTENTS, 'path_log = $sformatf("%0d", select);')
    contents_append_endl(CONTENTS, '')
    contents_append_tab_endl(CONTENTS, 'while((select != -1) && (select != -2)) begin')
    contents_append_tab_tab_endl(CONTENTS, 'select_tmp = select;')
    contents_append_tab_tab_endl(CONTENTS, 'select = selection(tr, select);')
    contents_append_tab_tab_endl(CONTENTS, 'if((select != -1) && (select != -2))')
    contents_append_tab_tab_tab_endl(CONTENTS, 'path_log = {path_log, $sformatf(" %0d", select)};')
    contents_append_tab_tab_endl(CONTENTS, '`uvm_info("selection", $sformatf("select node: %0d", select), UVM_LOW)')
    contents_append_tab_endl(CONTENTS, 'end')
    contents_append_endl(CONTENTS, '')
    contents_append_tab_endl(CONTENTS, 'if(select == -2) begin')
    contents_append_tab_tab_endl(CONTENTS, '`uvm_info("selection", $sformatf("select source node: %0d (%s)", select_tree[select_tmp].source, cfg.source_name[select_tree[select_tmp].source]), UVM_LOW)')
    contents_append_tab_tab_endl(CONTENTS, 'compare_path_log();')
    contents_append_tab_tab_endl(CONTENTS, 'return select_tree[select_tmp].source;')
    contents_append_tab_endl(CONTENTS, 'end')
    contents_append_endl(CONTENTS, '')
    contents_append_tab_endl(CONTENTS, 'return -1;')
    contents_append_endl(CONTENTS, 'endfunction: transition')
    ###################################### tree transition ######################################
    
    contents_append_endl(CONTENTS, '')
    
    ###################################### tree selection #######################################
    contents_append_endl(CONTENTS, "/** selection for cust_audio_data_path_transition_model */")
    contents_append_endl(CONTENTS, 'function int cust_audio_data_path_transition_model::selection(ref cust_audio_data_path_dump_mux_transaction tr, int node_id);')
    contents_append_tab_endl(CONTENTS, 'if(select_tree[node_id].done == 1)')
    contents_append_tab_tab_endl(CONTENTS, 'return -1;')
    contents_append_tab_endl(CONTENTS, 'select_tree[node_id].done = 1;')
    
    for component_info in components_info:
        node_id = component_info['NODE_ID']
        contents_append_endl(CONTENTS, "")
        contents_append_tab_endl(CONTENTS, "if(node_id == {}) begin".format(node_id))
        
        select_num = len(component_info['Selects'])
        input_num  = len(component_info['Inputs'])
        output_num = len(component_info['Outputs'])
        
        if select_num == 1:
            select    = component_info['Selects'][0]
            input_num = len(component_info['Inputs'])
            for i in range(input_num):
                if component_info['IS_REVERSE']:
                    contents_append_tab_tab_endl(CONTENTS, "if( !tr.{} == {} ) begin".format(select, i))
                else:
                    contents_append_tab_tab_endl(CONTENTS, "if( tr.{} == {} ) begin".format(select, i))
                    
                input_signal = component_info['Inputs'][i]
                contents_append_tab_tab_endl(CONTENTS, TAB + '`uvm_info("selection", $sformatf("{} is {}, node[%0d] -> node[%0d] through {}", node_id, select_tree[{}].select[{}]), UVM_LOW)'.format(select, i,  input_signal, node_id, i))
                    
                contents_append_tab_tab_endl(CONTENTS, TAB + "select_tree[{}].select_done[{}] = 1'b1;".format(node_id, i))
                contents_append_tab_tab_endl(CONTENTS, TAB + "return select_tree[{}].select[{}];".format(node_id, i))
                contents_append_tab_tab_endl(CONTENTS, "end")
                
        elif select_num > 1:
            selects = component_info['Selects']
            for i in range(select_num):
                IF_STATEMENT = "if( "
                FIRST = True
                for j in range(select_num):
                    if not FIRST:
                        IF_STATEMENT += " && "
                    else:
                        FIRST = not FIRST
                        
                    if component_info['IS_REVERSE']:
                        IF_STATEMENT += "(!"
                    else:
                        IF_STATEMENT += "("
                    
                    if i == j:
                        IF_STATEMENT += "tr.{} == 1)".format(selects[j])
                    else:
                        IF_STATEMENT += "tr.{} == 0)".format(selects[j])
                IF_STATEMENT += " ) begin"
                contents_append_tab_tab_endl(CONTENTS, IF_STATEMENT)
                
                input_signal = component_info['Inputs'][i]
                contents_append_tab_tab_endl(CONTENTS, TAB + '`uvm_info("selection", $sformatf("{} is {}, node[%0d] -> node[%0d] through {}", node_id, select_tree[{}].select[{}]), UVM_LOW)'.format(selects[j], i, input_signal, node_id, i))
                contents_append_tab_tab_endl(CONTENTS, TAB + "select_tree[{}].select_done[{}] = 1'b1;".format(node_id, i))
                contents_append_tab_tab_endl(CONTENTS, TAB + "return select_tree[{}].select[{}];".format(node_id, i))
                contents_append_tab_tab_endl(CONTENTS, "end")
                
        if select_num == 0:
            contents_append_tab_tab_endl(CONTENTS, '`uvm_info("selection", $sformatf("node[%0d] -> node[%0d]", node_id, select_tree[{}].select[0]), UVM_LOW)'.format(node_id))
            contents_append_tab_tab_endl(CONTENTS, "return select_tree[{}].select[0];".format(node_id))
        else:
            contents_append_tab_tab_endl(CONTENTS,  "return -1;")
        contents_append_tab_endl(CONTENTS, "end")
    contents_append_endl(CONTENTS, 'endfunction: selection')
    ###################################### tree selection #######################################
            
    contents_append_endl(CONTENTS, '')
    
    contents_append_endl(CONTENTS, '`endif // AUDIO_DATA_PATH_TRANSITION_MODEL__SV')
    
    if output_enable:
        write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')
    
    return components_info
    
def output_components_info(components_info, output_file_name = 'components_info.txt', output_dir = DATA_DIR):
    CONTENTS = []
    for idx, component_info in enumerate(components_info):
        contents_append_endl(CONTENTS, 'Component[%3s]: ' % str(idx) + json.dumps(component_info))
        
    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')
    
def output_mux_gentop(components_info, output_file_name = 'mux_gentop.v', output_dir = DATA_DIR):
    MUX_NAME_RE = r'^MUX_[1-9]*[0-9]to1'
    CONTENTS = []
    for idx, component_info in enumerate(components_info):
        if re.match(MUX_NAME_RE, component_info['Type']):
            lower_name = 'dv_' + component_info['Type'].lower()
            contents_append_endl(CONTENTS, '// {}'.format(lower_name))
            
            for idx, Input in enumerate(component_info['Inputs']):
                input_format = Input.ljust(60) if Input != SELECT_SIGNAL_RESERVED else "32'h0".ljust(60)
                contents_append_endl(CONTENTS, '// realtek conn ' + input_format + '{}.i{}'.format(lower_name, idx))
                
            contents_append_endl(CONTENTS, '// realtek conn ' + component_info['Selects'][0].ljust(60) + '{}.sel'.format(lower_name))
            contents_append_endl(CONTENTS, '// realtek conn ' + component_info['Outputs'][0].ljust(60) + '{}.out'.format(lower_name))
            
        
    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')

def construct_components_info_sheet(components_info, wb, sheet_name = ''):
    if not sheet_name:
        ws = wb.active
    else:
        wb.create_sheet(sheet_name)
        ws = wb[sheet_name]

    col_names = ['Node_id', 'Type']
    rows = []
    max_inputs_num  = -1
    max_outputs_num = -1
    max_selects_num = -1
    max_select_num  = -1

    for component_info in components_info:
        max_inputs_num  = len(component_info['Inputs'])  if max_inputs_num < len(component_info['Inputs'])  else max_inputs_num
        max_outputs_num = len(component_info['Outputs']) if max_outputs_num < len(component_info['Outputs']) else max_outputs_num
        max_selects_num = len(component_info['Selects']) if max_selects_num < len(component_info['Selects']) else max_selects_num
        max_select_num  = len(component_info['select'])  if max_select_num < len(component_info['select'])  else max_select_num
        
    for i in range(max_inputs_num):
        col_names.append('Input[{}]'.format(i))
    
    for i in range(max_outputs_num):
        col_names.append('Output[{}]'.format(i))
    
    for i in range(max_selects_num):
        col_names.append('Select[{}]'.format(i))
        
    for i in range(max_select_num):
        col_names.append('Connect[{}]'.format(i))
    
    col_names.append('Default_value_is_high')
        
    for component_info in components_info:
        row = []
        row.append(component_info['NODE_ID'])
        row.append(component_info['Type'])
        for i in range(max_inputs_num):
            try:
                row.append(component_info['Inputs'][i])
            except:
                row.append(' ')
                
        for i in range(max_outputs_num):
            try:
                row.append(component_info['Outputs'][i])
            except:
                row.append(' ')
                
        for i in range(max_selects_num):
            try:
                row.append(component_info['Selects'][i])
            except:
                row.append(' ')
                
        for i in range(max_select_num):
            try:
                row.append(component_info['select'][i])
            except:
                row.append(' ')                
                
        row.append(component_info['IS_REVERSE'])
        
        rows.append(row)
        
    ws = create_excel_table_title(ws, col_names)

    for row in rows:
        ws.append(row)
        
    ws = excel_auto_width(ws)
    
    return ws

def output_components_info_xlsx(components_info, output_file_name = 'components_info.xlsx', output_dir = DATA_DIR):
    wb = Workbook()
    construct_components_info_sheet(components_info, wb)
    
    output_file_name = file_with_dir_path(output_file_name, output_dir)
    wb.save(output_file_name)

def output_all_path(all_path, output_file_name = 'all_path.txt', IS_APPEND_MODE = False, output_dir = INPUT_DIR):
    CONTENTS = []

    for idx, path in enumerate(all_path):
        line = 'Path[%s]: ' % idx
        for node in path:
            line += str(node) + ' '
        contents_append_endl(CONTENTS, line)

    write_contents_to_file(CONTENTS, output_file_name, output_dir, IS_APPEND_MODE, ENDL = '')

def get_id_in_parentheses(s):
    try:
        value = int(re.search(r'\[*[0-9]+\]', s).group(0).replace('[','').replace(']', ''))
    except:
        print('error: ' + s)
        
    return value

def merge_all_path(output_file_name = 'all_path.txt', input_dir = INPUT_DIR):
    path_file_list = sorted([f for f in os.listdir(input_dir) if re.match(r'all_path\[[0-9]+\]\.txt', f)], key = get_id_in_parentheses)
    
    erase_file_contents(output_file_name, input_dir)
    last_path_id = 0
    chosen_path_idx_list = []
    for idx, path_file_name in enumerate(path_file_list):
        print('aggregate path num: {}, start merging {} ...'.format(last_path_id, path_file_name))

        f_in = open(file_with_dir_path(path_file_name, input_dir), "r+b")
        in_map_file = mmap.mmap(f_in.fileno(), 0)
        
        f_out = open(file_with_dir_path(output_file_name, input_dir), "a")
        
        max_nodes_num_in_path = 0
        max_nodes_path_idx    = -1
        for line in iter(in_map_file.readline, b""):
            if line.find(b':') != -1:
                path = 'Path[{}]:'.format(last_path_id) + line[line.find(b':')+1:].decode("utf-8")
                path = path.replace('\n', '')
                
                nodes_num_in_path = path.count(' ')
                if max_nodes_num_in_path < nodes_num_in_path:
                   max_nodes_num_in_path = nodes_num_in_path
                   max_nodes_path_idx    = last_path_id
                
                if(is_windows()):
                    f_out.write(path)
                else:
                    f_out.write(path + '\n')
                last_path_id += 1
        
        chosen_path_idx_list.append(max_nodes_path_idx)
        in_map_file.close()
        f_in.close()
        
        f_out.close()
        
    write_chosen_path_idx_list(chosen_path_idx_list)

def read_all_path(input_file_name = 'all_path.txt', input_dir = INPUT_DIR, IS_MMAP_MODE = True):
    input_file_name = file_with_dir_path(input_file_name, input_dir)
    
    if not IS_MMAP_MODE:
        all_path_file = open(input_file_name, 'r')
        
        all_path = []
        for line in all_path_file.readlines():
            path = (line[line.find(':')+1:]).split()
            all_path.append([int(node) for node in path])
    else:
        all_path = ALL_PATH(input_file_name)
        
    return all_path

def gen_interface(components_info, output_file_name = "audio_data_path_dump_mux_interface.sv", output_dir = ENV_DIR):
    CONTENTS  = []
    contents_append_endl(CONTENTS, SIGNATURE)

    tmp = '`ifndef AUDIO_DATA_PATH_DUMP_MUX_INTERFACE__SV\n`define AUDIO_DATA_PATH_DUMP_MUX_INTERFACE__SV'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')

    tmp = 'interface audio_data_path_dump_mux_interface (input logic clk);'
    contents_append_endl(CONTENTS, tmp)

    tmp = TAB + 'logic rst;'
    contents_append_endl(CONTENTS, tmp)

    signals, ports = get_select_signals_and_ports(components_info)
                
    for port in ports:
        contents_append_endl(CONTENTS, TAB + port + ';')
        
    contents_append_endl(CONTENTS, '')
    contents_append_endl(CONTENTS, '')

    tmp = TAB + "modport monitor("
    contents_append_endl(CONTENTS, tmp)

    for signal in signals:
        tmp = TAB + TAB + TAB + TAB + TAB + 'input {},'.format(signal)
        contents_append_endl(CONTENTS, tmp)
        
    CONTENTS[-1] = CONTENTS[-1].replace(',','')

    tmp = TAB + "              );"
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')

    tmp = 'endinterface: audio_data_path_dump_mux_interface'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')

    tmp = '`endif // AUDIO_DATA_PATH_DUMP_MUX_INTERFACE__SV'
    contents_append_endl(CONTENTS, tmp)

    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')

def gen_transaction(components_info, output_file_name = "cust_audio_data_path_dump_mux_transaction.sv", output_dir = ENV_DIR):
    CONTENTS  = []
    contents_append_endl(CONTENTS, SIGNATURE)

    tmp = '`ifndef CUST_AUDIO_DATA_PATH_DUMP_MUX_TRANSACTION__SV\n`define CUST_AUDIO_DATA_PATH_DUMP_MUX_TRANSACTION__SV'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')

    tmp = 'class cust_audio_data_path_dump_mux_transaction extends audio_data_path_dump_mux_transaction;'
    contents_append_endl(CONTENTS, tmp)

    signals, ports = get_select_signals_and_ports(components_info)
    
    for port in ports:
        tmp = TAB + port + ';'
        contents_append_endl(CONTENTS, tmp)
        
    contents_append_endl(CONTENTS, '')
    contents_append_endl(CONTENTS, '')

    tmp = TAB + "`uvm_object_utils_begin(cust_audio_data_path_dump_mux_transaction)"
    contents_append_endl(CONTENTS, tmp)

    for signal in signals:
        tmp = TAB + TAB + '`uvm_field_int({}, UVM_DEFAULT)'.format(signal)
        contents_append_endl(CONTENTS, tmp)
            
    tmp = TAB + "`uvm_object_utils_end"
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')

    tmp = TAB + 'extern function new(string name = "cust_audio_data_path_dump_mux_transaction");'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = 'endclass: cust_audio_data_path_dump_mux_transaction'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')
    
    tmp = 'function cust_audio_data_path_dump_mux_transaction::new(string name = "cust_audio_data_path_dump_mux_transaction");'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = TAB + "super.new(name);"
    contents_append_endl(CONTENTS, tmp)
    
    tmp = "endfunction: new"
    contents_append_endl(CONTENTS, tmp)

    tmp = '`endif // CUST_AUDIO_DATA_PATH_DUMP_MUX_TRANSACTION__SV'
    contents_append_endl(CONTENTS, tmp)

    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')

def gen_monitor(components_info, output_file_name = "cust_audio_data_path_dump_mux_monitor.sv", output_dir = ENV_DIR):
    CONTENTS  = []
    contents_append_endl(CONTENTS, SIGNATURE)

    tmp = '`ifndef CUST_AUDIO_DATA_PATH_DUMP_MUX_MONITOR__SV\n`define CUST_AUDIO_DATA_PATH_DUMP_MUX_MONITOR__SV'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')

    tmp = 'class cust_audio_data_path_dump_mux_monitor extends audio_data_path_dump_mux_monitor #(cust_audio_data_path_dump_mux_transaction);'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')
    
    tmp = TAB + 'virtual audio_data_path_dump_mux_interface audio_data_path_dump_mux_if;'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')
    
    tmp = TAB + '`uvm_component_utils(cust_audio_data_path_dump_mux_monitor)'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')
    
    tmp = TAB + 'extern function new(string name = "cust_audio_data_path_dump_mux_monitor", uvm_component parent);'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = TAB + 'extern virtual function void build_phase(uvm_phase phase);'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = TAB + 'extern protected virtual task sample_mux(ref cust_audio_data_path_dump_mux_transaction tr);'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')
    
    tmp = 'endclass: cust_audio_data_path_dump_mux_monitor'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')
    
    tmp = 'function cust_audio_data_path_dump_mux_monitor::new(string name = "cust_audio_data_path_dump_mux_monitor", uvm_component parent);'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = TAB + 'super.new(name, parent);'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = 'endfunction: new'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')
    
    tmp = 'function void cust_audio_data_path_dump_mux_monitor::build_phase(uvm_phase phase);'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = TAB + 'super.build_phase(phase);'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = TAB + 'if (!uvm_config_db#(virtual audio_data_path_dump_mux_interface)::get(this, "", "audio_data_path_dump_mux_if", audio_data_path_dump_mux_if))'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = TAB + TAB + '`uvm_fatal("NOVIF", {"audio_data_path_dump_mux_if must be set for ", get_full_name()})'
    contents_append_endl(CONTENTS, tmp)
    
    tmp = 'endfunction: build_phase'
    contents_append_endl(CONTENTS, tmp)
    contents_append_endl(CONTENTS, '')
    
    tmp = 'task cust_audio_data_path_dump_mux_monitor::sample_mux(ref cust_audio_data_path_dump_mux_transaction tr);'
    contents_append_endl(CONTENTS, tmp)
        
    signals, ports = get_select_signals_and_ports(components_info)
        
    for signal in signals:
        tmp = TAB + 'tr.{} = audio_data_path_dump_mux_if.{};'.format(signal, signal)
        contents_append_endl(CONTENTS, tmp)
    
    tmp = 'endtask: sample_mux'
    contents_append_endl(CONTENTS, tmp)

    tmp = '`endif // CUST_AUDIO_DATA_PATH_DUMP_MUX_MONITOR__SV'
    contents_append_endl(CONTENTS, tmp)

    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')
    
def gen_coverage(components_info, output_file_name = 'cust_audio_data_path_coverage_model.sv', output_dir = ENV_DIR):
    CONTENTS  = []
    contents_append_endl(CONTENTS, SIGNATURE) 
    contents_append_endl(CONTENTS, '`ifndef CUST_AUDIO_DATA_PATH_COVERAGE_MODEL__SV')
    contents_append_endl(CONTENTS, '`define CUST_AUDIO_DATA_PATH_COVERAGE_MODEL__SV')
    contents_append_endl(CONTENTS, '')
    contents_append_endl(CONTENTS, 'class cust_audio_data_path_coverage_model extends audio_data_path_coverage_model #(cust_audio_data_path_dump_mux_transaction, cust_audio_data_path_transition_model);')
    contents_append_endl(CONTENTS, '')
    contents_append_tab_endl(CONTENTS, '`uvm_component_utils(cust_audio_data_path_coverage_model)')
    contents_append_endl(CONTENTS, '')
    contents_append_tab_endl(CONTENTS, 'covergroup cg_components;')
    contents_append_tab_tab_endl(CONTENTS, 'option.per_instance = 1;')
    
    for component_info in components_info:
        if component_info['Type'] != 'Input_Node' and len(component_info['Selects']) > 0:
            NODE_ID = component_info['NODE_ID']
            coverpoint_name = '{}_COMPONENT_{}'.format(component_info['Type'].replace('/','_'), NODE_ID)
            contents_append_tab_tab_endl(CONTENTS, coverpoint_name + ':')
            COVERPOINT  = TAB + 'coverpoint '
            COVERPOINT += ' {\n'
            for idx, input in enumerate(component_info['Inputs']):
                COVERPOINT += TAB + TAB + TAB + TAB + TAB + TAB + TAB + 'transition.select_tree[{}].select_done[{}]'.format(NODE_ID, idx)
                if idx == len(component_info['Inputs']) -1:
                    COVERPOINT += '\n' + TAB + TAB + TAB + TAB + TAB + TAB + '}'
                else:
                    COVERPOINT += ',\n'
            
            COVERPOINT += '\n' + TAB + TAB + TAB + TAB + TAB + TAB + '{\n'
            for idx, input in enumerate(component_info['Inputs']):
                COVERPOINT += TAB + TAB + TAB + TAB + TAB + TAB + TAB + 'bins {}_Output_select_{} = '.format(coverpoint_name, idx)
                COVERPOINT += '{'
                COVERPOINT += "{}'b".format(len(component_info['Inputs']))
                for i in range(len(component_info['Inputs'])):
                    if i == idx:
                        COVERPOINT += '1'
                    else:
                        COVERPOINT += '0'
                COVERPOINT += '};\n'
            COVERPOINT += TAB + TAB + TAB + TAB + TAB + TAB + '}'
            contents_append_tab_tab_endl(CONTENTS, COVERPOINT)
    contents_append_tab_endl(CONTENTS, 'endgroup')
    contents_append_endl(CONTENTS, '')
        
    contents_append_tab_endl(CONTENTS, 'extern function new(string name = "cust_audio_data_path_coverage_model", uvm_component parent);')
    contents_append_tab_endl(CONTENTS, 'extern virtual function void sample_cov();')
    contents_append_tab_endl(CONTENTS, 'extern virtual function real get_cov();')
    contents_append_endl(CONTENTS, 'endclass: cust_audio_data_path_coverage_model')
    
    contents_append_endl(CONTENTS, '')
    contents_append_endl(CONTENTS, '/** new function for cust_audio_data_path_coverage_model */')
    contents_append_endl(CONTENTS, 'function cust_audio_data_path_coverage_model::new(string name = "cust_audio_data_path_coverage_model", uvm_component parent);')
    contents_append_tab_endl(CONTENTS, 'super.new(name, parent);')
    contents_append_tab_endl(CONTENTS, 'cg_components = new();')
    contents_append_endl(CONTENTS, 'endfunction: new')
    
    contents_append_endl(CONTENTS, '')
    contents_append_endl(CONTENTS, '/** sample_cov for cust_audio_data_path_coverage_model */')
    contents_append_endl(CONTENTS, 'function void cust_audio_data_path_coverage_model::sample_cov();')
    contents_append_tab_endl(CONTENTS, 'cg_components.sample();')
    contents_append_endl(CONTENTS, 'endfunction: sample_cov')
    
    contents_append_endl(CONTENTS, '')
    contents_append_endl(CONTENTS, '/** get_cov for cust_audio_data_path_coverage_model */')
    contents_append_endl(CONTENTS, 'function real cust_audio_data_path_coverage_model::get_cov();')
    contents_append_tab_endl(CONTENTS, 'get_cov = cg_components.get_inst_coverage();')
    contents_append_endl(CONTENTS, 'endfunction: get_cov')
    
    contents_append_endl(CONTENTS, '')
    contents_append_endl(CONTENTS, '`endif // CUST_AUDIO_DATA_PATH_COVERAGE_MODEL__SV')
    
    write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')

def gen_grapth(components_info):
    color_map = []
    G = nx.DiGraph()
    edge_labels = {}
    
    for component_info in components_info:
        G.add_node(int(component_info['NODE_ID']))
        if component_info['Type'] == 'Input_Node':
            color_map.append('green')
        elif component_info['Type'] == 'Output_Node':
            color_map.append('pink')
        else:
            color_map.append('gray')
        
    for component_info in components_info:
        node_id = int(component_info['NODE_ID'])
        for idx, select in enumerate(component_info['select']):
            if select != NULL_NODE_ID:
                G.add_edge(node_id, select, label = component_info['Inputs'][idx])
                edge_labels.update({(node_id, select): component_info['Inputs'][idx]})
            
            
    return G, color_map, edge_labels
    
def recursive_dfs(graph, source, path = []):
       if source not in path:
           path.append(source)
           if source not in graph:
               # leaf node, backtrack
               return path
           for neighbor in graph[source]:
               path = recursive_dfs(graph, neighbor, path)
       return path
    
def get_edges_from_path(path):
    edges = []
    for idx in range(len(path)-1):
        edges.append((path[idx], path[idx+1]))
    return edges

def path_list_to_string(path):
    expect_path_log = ""
    for node_id in path:
        expect_path_log += ' {}'.format(node_id)
    expect_path_log = expect_path_log[1:]
    
    return expect_path_log

def make_legal_path_list(path_list, components_info):
    legal_path_list = []
    
    for path in path_list:
        LEGAL_FLAG = True
        for idx_x, x in enumerate(path):
            if not LEGAL_FLAG:
                break
            for idx_y in range(idx_x+1, len(path)):
                y = path[idx_y]
                if not LEGAL_FLAG:
                    break
                components_x = components_info[x]
                components_y = components_info[y]
                
                if len(components_x['Selects']) == 1 and len(components_y['Selects']) == 1:
                    if components_x['Selects'][0] == components_y['Selects'][0]:
                        if idx_x+1 < len(path):
                            x_input = path[idx_x+1]
                            
                        if idx_y+1 < len(path):
                            y_input = path[idx_y+1]
                        
                        x_idx_connect = -1
                        y_idx_connect = -1
                        for idx_connect, connect in enumerate(components_info[x]['select']):
                            if connect == x_input:
                                x_idx_connect = idx_connect
                                break
                                
                        for idx_connect, connect in enumerate(components_info[y]['select']):
                            if connect == y_input:
                                y_idx_connect = idx_connect
                                break
                        
                        if not x_idx_connect == y_idx_connect:
                            #print('x: {}, y: {}'.format(x, y))
                            #print('x_input: {}, y_input: {}, x_idx_connect: {}, y_idx_connect: {}'.format(x_input, y_input, x_idx_connect, y_idx_connect))
                            LEGAL_FLAG = False

                '''else:
                    try:
                        x_input = path[idx_x+1]
                        y_input = path[idx_y+1]
                        x_idx_connect = -1
                        y_idx_connect = -1
                        for idx_connect, connect in enumerate(components_info[x]['select']):
                            if connect == x_input:
                                x_idx_connect = idx_connect
                                break
                                
                        for idx_connect, connect in enumerate(components_info[y]['select']):
                            if connect == y_input:
                                y_idx_connect = idx_connect
                                break
                        
                        for x_select_idx, x_select in enumerate(components_x['Selects']):
                            for y_select_idx, y_select in enumerate(components_y['Selects']):
                                if x_select == y_select:
                                    # 要嘛都選 要嘛都不能選
                                    if not ((x_select_idx == x_idx_connect and y_select_idx == y_idx_connect) or (x_select_idx != x_idx_connect and y_select_idx != y_idx_connect)):
                                        LEGAL_FLAG = False
                                        break
                                        
                    except:
                        traceback.print_exc()
                        'do nothing'
                '''    
                    
        if LEGAL_FLAG:
            legal_path_list.append(path)
        #else:
        #    print('remove illegal path: {}'.format(path_list_to_string(path)))
    
    return legal_path_list

def write_split_idx_file(split_idx, output_file_name = 'split_idx.txt', IS_APPEND_MODE = False, output_dir = DATA_DIR):   
    CONTENTS = [split_idx]
    write_contents_to_file(CONTENTS, output_file_name, output_dir, IS_APPEND_MODE, ENDL = '\n')
    
def open_process_path(idx):
    print('start {}'.format(mp.current_process().name))
    print(idx)
    os.system('python process_path.py {}'.format(idx))
    print('end {}'.format(mp.current_process().name))
    
def process_path(output_file_name = 'split_idx.txt', output_dir = DATA_DIR, input_file_name = 'all_path.txt', input_dir = INPUT_DIR, log_file_name = 'process_path_log.txt', log_dir = CHECK_LOG_DIR):
    BATCH_LIMIT = 30
    split_idx_list = [int(node['NODE_ID']) for node in components_info if node['Type'] == 'Output_Node']
    input_node_num = len([node for node in components_info if node['Type'] == 'Input_Node'])
    BATCH_OUTPUT_NUM = BATCH_LIMIT // input_node_num if (BATCH_LIMIT // input_node_num) > 0 else 1
    BATCH_NUM        = len(split_idx_list) // BATCH_OUTPUT_NUM if (len(split_idx_list) // BATCH_OUTPUT_NUM) > 0 else 1
    
    erase_file_contents(output_file_name, output_dir)
    erase_file_contents(input_file_name, input_dir)
    erase_file_contents(log_file_name, log_dir)

    split_idx_list_list = split_list(split_idx_list, BATCH_NUM)
    line_cnt = 0
    for idx, split_idx_list in enumerate(split_idx_list_list):
        line = ''
        for split_idx in split_idx_list:
            line += '{} '.format(split_idx)
        write_split_idx_file(line, IS_APPEND_MODE = True)
        line_cnt += 1
        
    pool = mp.Pool(2)
    process_arr = [*range(line_cnt)]
    print(process_arr)
    pool.map(open_process_path, process_arr)
    
    '''
    for idx in range(line_cnt):
        # if os.path.isfile('process_path.py'):
        #     os.system('python process_path.py {}'.format(idx))
        # else:
        #     os.system('process_path.exe {}'.format(idx))
    '''

    
def get_coverd_map(G, all_path, chosen_path_idx_list, IS_MMAP_MODE = True):
    edge_covered_map = {}
    for edge in G.edges():
        edge_covered_map.update({edge: False})
        
    if not IS_MMAP_MODE:
        for path_idx in chosen_path_idx_list:
            path = all_path[path_idx]
            for edge in get_edges_from_path(path):
                edge_covered_map.update({edge: True})
    else:
        for path_idx in chosen_path_idx_list:
            for edge in all_path.get_edges_by_path_id(path_idx):
                edge_covered_map.update({edge: True})
            
    return edge_covered_map
    
def get_unvocered_edge(edge_covered_map):
    unvocered_edges = []
    for k in edge_covered_map:
        if edge_covered_map[k] == False:
            unvocered_edges.append(k)
    return unvocered_edges
    
def auto_add_chosen_path(G, all_path, chosen_path_idx_list, edge_covered_map):
    for k in edge_covered_map:
        if edge_covered_map[k] == False:
            Found = False
            for idx, path in enumerate(all_path):
                if Found:
                    break
                for edge in get_edges_from_path(path):
                    if edge == k:
                        chosen_path_idx_list.append(idx)
                        Found = True
                        for edge_check in get_edges_from_path(path):
                            edge_covered_map.update({edge: True})
                    
    return list(set(chosen_path_idx_list))
    
def auto_add_chosen_path_greedy(G, all_path, chosen_path_idx_list, edge_covered_map, IS_MMAP_MODE = True, LOOKUP_NUM = 10240):

    not_found_cnt = 0
    not_found_th  = 1
    
    not_covered_edges = []
    not_covered_edges_last_round = []
    
    while(True):
        not_covered_edges_last_round = not_covered_edges.copy()
        not_covered_edges = [ k for k in edge_covered_map if edge_covered_map[k] == False ]
        
        if not_covered_edges_last_round == not_covered_edges:
            print('not_found_cnt: {}, not_found_th: {}'.format(not_found_cnt, not_found_th))
            not_found_cnt += 1
        else:
            not_found_cnt = 0
            
        if not_found_cnt >= not_found_th:
            ERROR_MESSAGE("there are {} edges not covered, please check visio".format(len(not_covered_edges)))
            break
        
        if not not_covered_edges:
            break
            
        print('num of not-covered edges: {}'.format(len(not_covered_edges)))
        
        max_gain = -1
        max_gain_path_idx  = -1
        max_gain_gain_list = []
        
        if not IS_MMAP_MODE:
            path_chosen = all_path
            path_chosen_indices = range(len(all_path))
        else:
            path_chosen, path_chosen_indices = all_path.get_random_path_list(LOOKUP_NUM)
            
        for idx, path in zip(path_chosen_indices, path_chosen):
            gain_list = []
            for edge in get_edges_from_path(path):
                if edge in not_covered_edges:
                    gain_list.append(edge)
                    
            gain = len(gain_list)
            
            if gain > max_gain:
                max_gain_path_idx = idx
                max_gain = gain
                max_gain_gain_list = gain_list.copy()
        
        if max_gain != -1 and max_gain_path_idx != -1 and max_gain_gain_list:
            print('auto_add_chosen_path_greedy, choose path[{}], gain edges: {}'.format(max_gain_path_idx, list_to_string(max_gain_gain_list)))
            chosen_path_idx_list.append(max_gain_path_idx)
            for edge in max_gain_gain_list:
                edge_covered_map.update({edge: True})

    return list(set(chosen_path_idx_list))
    
def auto_add_chosen_path_search(G, all_path, chosen_path_idx_list, edge_covered_map, IS_MMAP_MODE = True):
    not_found_cnt = 0
    not_found_th  = 1
    
    not_covered_edges = []
    
    not_covered_edges = [ k for k in edge_covered_map if edge_covered_map[k] == False ]
    for not_covered_edge in not_covered_edges:
        find_pattern = ' {} {} '.format(not_covered_edge[0], not_covered_edge[1])
        find_pattern = find_pattern.encode()
        pos = all_path.find(find_pattern)
        
        if pos != -1:
            path_idx, path = all_path.get_path_by_pos(pos)
            gain_list = []
            for edge in get_edges_from_path(path):
                if edge in not_covered_edges:
                    gain_list.append(edge)
                    
            gain = len(gain_list)
            
            print('auto_add_chosen_path_search, choose path[{}], gain edges: {}'.format(path_idx, list_to_string(gain_list)))
            chosen_path_idx_list.append(path_idx)
            for edge in gain_list:
                edge_covered_map.update({edge: True})

    return list(set(chosen_path_idx_list))

def reduce_chosen_path_idx_list(chosen_path_idx_list, all_path):
    reduced_chosen_path_idx_list = []
    
    for chosen_path_idx in chosen_path_idx_list:
        COVERED_BY_OTHERS = False
        chosen_path = all_path[chosen_path_idx]
        path_edge_covered_map = {}
        for edge in get_edges_from_path(chosen_path):
            path_edge_covered_map.update({edge: False})
            
        for other_path_idx in chosen_path_idx_list:
            if chosen_path_idx != other_path_idx:
                other_path = all_path[other_path_idx]
                for edge in get_edges_from_path(other_path):
                    path_edge_covered_map.update({edge: True})
        
        for k in path_edge_covered_map:
            if path_edge_covered_map[k] == False:
                COVERED_BY_OTHERS = False
                break
        
        if not COVERED_BY_OTHERS:
            reduced_chosen_path_idx_list.append(chosen_path_idx)
            
    return reduced_chosen_path_idx_list

def excel_auto_width(ws):
    EXTENSION = 2
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        ws.column_dimensions[get_column_letter(column_cells[0].column)].width = length + EXTENSION
    return ws

def construct_path_sheet(all_path, chosen_path_idx_list, components_info, wb, sheet_name = '', DETAIL = True):
    if not sheet_name:
        ws = wb.active
    else:
        wb.create_sheet(sheet_name)
        ws = wb[sheet_name]
    
    rows = []
    for path in all_path:
        row = []
        for node in path:
            component = components_info[node]
            if not DETAIL:
                row.append('%5s' % node)
            else:
                if component['Type'] == 'Output_Node':
                    row.append('{}({})-{}'.format(node, component['Type'], components_info[node]['Inputs'][0]))
                else:
                    row.append('{}({})-{}'.format(node, component['Type'], components_info[node]['Outputs'][0]))
        rows.append(row)
        
    
    
    for row in rows:
        ws.append(row)
        
    for idx in chosen_path_idx_list:
        for cell in ws[str(idx+1)]:
            if cell.value:
                cell.fill = PatternFill(start_color="FFA500", fill_type = "solid")
                
    ws = excel_auto_width(ws)
    return ws
    
def write_path_to_excel(all_path, chosen_path_idx_list, components_info, output_file_name = 'all_path.xlsx', output_dir = INPUT_DIR):

    wb = Workbook()
    construct_path_sheet(all_path, chosen_path_idx_list, components_info, wb)

    output_file_name = file_with_dir_path(output_file_name, output_dir)
    backup_file(output_file_name)
    wb.save(output_file_name)
    
def read_path_from_excel(input_file_name = 'all_path.xlsx', input_dir = INPUT_DIR):
    read_path_idx_list = []
    input_file_name = file_with_dir_path(input_file_name, input_dir)
    wb = load_workbook(input_file_name)
    ws = wb.active
    for idx, row in enumerate(ws):
        cell = row[0]
        if cell.value:
            if cell.fill.fgColor.type == 'rgb' and cell.fill.fgColor.rgb != "00000000":
                read_path_idx_list.append(idx)
    
    return read_path_idx_list
    
def write_chosen_path_idx_list(read_path_idx_list, output_file_name = 'chosen_path_idx_list.txt', output_dir = INPUT_DIR):
    CONTENTS = []
    for idx in read_path_idx_list:
        CONTENTS.append(str(idx))
    
    write_contents_to_file(CONTENTS, output_file_name, output_dir)  
    
def read_chosen_path_idx_list(input_file_name = 'chosen_path_idx_list.txt', input_dir = INPUT_DIR):
    read_path_idx_list = []
    input_file_name = file_with_dir_path(input_file_name, input_dir)
    chosen_path_idx_list_file = open(input_file_name, 'r')
    
    for line in chosen_path_idx_list_file.readlines():
        read_path_idx_list.append(int(line))
        
    return read_path_idx_list
    
def check_path_equal(all_path, chosen_path_idx_list, read_path_idx_list):
    user_choose_path_list = []
    for read_path_idx in read_path_idx_list:
        read_path = all_path[read_path_idx]
        Found = False
        for chosen_path_idx in chosen_path_idx_list:
            chosen_path = all_path[chosen_path_idx]
            if read_path_idx == chosen_path_idx:
                if len(read_path) == len(chosen_path):
                    Found = True
                    for read_node, chosen_node in zip(read_path, chosen_path):
                        if read_node != chosen_node:
                            Found = False
                            break
                        
        if not Found:
            user_choose_path_list.append(read_path)
    return user_choose_path_list
    
def create_excel_table_title(ws, col_names, color = "EBBA34", with_border = True):
    thin_border = Border(left=Side(style='thin'), 
                     right=Side(style='thin'), 
                     top=Side(style='thin'), 
                     bottom=Side(style='thin'))
    ## the col names
    ws.append(col_names)
    for cell in ws[1]:
        cell.fill = PatternFill(start_color="EBBA34", fill_type = "solid")
        #cell.font = Font(bold=True)
        cell.border = thin_border
        
    return ws
    
def parse_register_file(input_file_name = 'all_register_dump_for_dv.txt', input_dir = INPUT_DIR):
    all_register_info = {}
    input_file_name = file_with_dir_path(input_file_name, input_dir)
    
    try:
        all_register_dump_for_dv_file = open(input_file_name, 'r')
    except:
        ERROR_MESSAGE('all_register_dump_for_dv.txt not found')
        control = input("Please prepare all_register_dump_for_dv.txt in the input directory, and press C(continue)")
        if control.lower() != 'c':
            return all_register_info
    
    for idx, line in enumerate(all_register_dump_for_dv_file.readlines()):
        if idx != 0:
            split_result = re.split('\s+', line)
            Signal = split_result[0]
            Addr   = split_result[1]
            Bits_Indices = split_result[2]
            
            delta = -1
            if Bits_Indices.find(':') != -1:
                start = int(Bits_Indices[:Bits_Indices.find(':')])
                end   = int(Bits_Indices[Bits_Indices.find(':')+1:])
                delta = int(abs(end-start))+1
            else:
                delta = 1
            
            all_register_info.update({ Signal: {'Addr': Addr, 'Bits_Indices': Bits_Indices, 'Length': delta}})
    
    return all_register_info
    
def construct_registed_info_sheet(all_register_info, wb, sheet_name=''):
    if not sheet_name:
        ws = wb.active
    else:
        wb.create_sheet(sheet_name)
        ws = wb[sheet_name]

    col_names = ['Signal', 'Addr', 'Bits_Indices', 'Length']
    rows = []

    for Signal in all_register_info:
        register = all_register_info[Signal]
        row = []
        row.append(Signal)
        for col_name in col_names[1:]:
            row.append(register[col_name])

        rows.append(row)
        
    
    ws = create_excel_table_title(ws, col_names)

    for row in rows:
        ws.append(row)
        
    ws = excel_auto_width(ws)
    
def output_register_info(all_register_info, output_file_name = 'all_register_info.xlsx', output_dir = DATA_DIR):
    wb = Workbook()
    
    construct_registed_info_sheet(all_register_info, wb)
    
    output_file_name = file_with_dir_path(output_file_name, output_dir)
    wb.save(output_file_name)
    
def gen_register_info(components_info, all_register_info, WITH_ALL_REGISTER_INFO, output_file_name = 'reg_info.xlsx', output_dir = INPUT_DIR):
    col_names = ['signal', 'address', 'bit(s) index', 'read command of the UVM environment', 'write command of the UVM environment']
    rows = []
    #signals, ports = get_select_signals_and_ports(components_info)
     
    for component_info in components_info:
        for signal in component_info['Selects']:
            if signal != SELECT_SIGNAL_RESERVED:
                row = []
                row.append(signal)
                if WITH_ALL_REGISTER_INFO:
                    row.append(all_register_info[signal]['Addr'])
                    row.append(all_register_info[signal]['Bits_Indices'])
                    row.append(' ')
                    row.append(' ')
                rows.append(row)
        
    wb = Workbook()
    ws = wb.active
    ws = create_excel_table_title(ws, col_names)
        
    for row in rows:
        ws.append(row)
        
    ws = excel_auto_width(ws)
    
    output_file_name = file_with_dir_path(output_file_name, output_dir)
    backup_file(output_file_name)
    wb.save(output_file_name)
    
def set_value_reverse(set_value, IS_REVERSE):
    return_value = ''
    
    for value in set_value:
        if value == '1':
            if IS_REVERSE:
                return_value += '0'
            else:
                return_value += '1'
        else:
            if IS_REVERSE:
                return_value += '1'
            else:
                return_value += '0'
                
    return return_value

def gen_inout_info(components_info, output_file_name = 'inout_info.xlsx', output_dir = INPUT_DIR):
    SPACES = '                                                                          '
    col_names = ['input', 'output', SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES]
    rows = []
    input_component_info  = []
    output_component_info = []
    for component_info in components_info:
        if component_info['Type'] == 'Input_Node':
            input_component_info.append(component_info)
        elif component_info['Type'] == 'Output_Node':
            output_component_info.append(component_info)
    
    for input in input_component_info:
        for output in output_component_info:
            row = []
            row.append(input['Outputs'][0])
            row.append(output['Inputs'][0])
            rows.append(row)
        
    wb = Workbook()
    ws = wb.active
    ws = create_excel_table_title(ws, col_names)
    for row in rows:
        ws.append(row)
        
    ws = excel_auto_width(ws)
    
    output_file_name = file_with_dir_path(output_file_name, output_dir)
    backup_file(output_file_name)
    wb.save(output_file_name)
    
def gen_in_and_out_info(components_info, output_file_names = ['in_info.xlsx', 'out_info.xlsx'], col_name_list = ['input', 'output'], output_dir = INPUT_DIR):
    SPACES = '                                                                          '
    input_component_info  = get_nodes_by_type(components_info, 'Input_Node')
    output_component_info = get_nodes_by_type(components_info, 'Output_Node')
    
    for idx, output_file_name in enumerate(output_file_names):
        col_names = [col_name_list[idx], SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES, SPACES]
        rows = []
        
        if idx == 0:
            for input in input_component_info:
                row = []
                row.append(input['Outputs'][0])
                rows.append(row)
        else:
            for output in output_component_info:
                row = []
                row.append(output['Inputs'][0])
                rows.append(row)

        wb = Workbook()
        ws = wb.active
        ws = create_excel_table_title(ws, col_names)
        for row in rows:
            ws.append(row)
            
        ws = excel_auto_width(ws)
        
        output_file_name = file_with_dir_path(output_file_name, output_dir)
        backup_file(output_file_name)
        wb.save(output_file_name)
    
def add_signal_settings(CONTENTS, select_signal, set_value, signal_setting, node_id = -1, select_node_id = -1, IS_DEFAULT_SETTING = False):
    signal_setting = signal_setting.replace('set_value', set_value)
    
    if signal_setting and select_signal:
        if not IS_DEFAULT_SETTING:
            information = 'signal: {}, write value: {}, node[{}]({}) -> node[{}]({}) through {}'.format(select_signal, set_value, node_id, components_info[node_id]['Type'], select_node_id, components_info[select_node_id]['Type'], components_info[select_node_id]['Outputs'][0])
        else:
            information = 'signal: {}, write default value: {}'.format(select_signal, set_value)
            
        contents_append_tab_tab_endl(CONTENTS, '`uvm_info("audio_data_path_reg_config", "{}", UVM_LOW)'.format(information))
        
        for line in signal_setting.splitlines():
            contents_append_tab_tab_endl(CONTENTS, line)
            
        contents_append_endl(CONTENTS, '')
        
    return CONTENTS
    
def get_signal_default_settings(CONTENTS, node, SIGNAL_SETTINGS):

    select_signal = ''
    set_value = ''  
    signal_setting = ''
    

    ## 多個 selects -> 意味著 # of selects = # of inputs 且 selects 都為 1 bit
    if len(node['Selects']) > 1:

        for idx, select_signal in enumerate(node['Selects']):
            if select_signal != SELECT_SIGNAL_RESERVED:
                signal_setting = SIGNAL_SETTINGS[select_signal]['cmd_combo']
                set_value = set_value_reverse('0', node['IS_REVERSE'])
                signal_setting = signal_setting.replace('set_value', set_value)
                CONTENTS = add_signal_settings(CONTENTS, select_signal, set_value, signal_setting, IS_DEFAULT_SETTING = True)

    ## 單一 select
    ## case 1: 多 bits select (mul inputs)
    ## case 2:  1 bit  select (2   inputs)
    elif len(node['Selects']) == 1:
        select_signal = str(node['Selects'][0])
        if select_signal != SELECT_SIGNAL_RESERVED:
            signal_setting = SIGNAL_SETTINGS[select_signal]['cmd_combo']
            
            ## 多 bits select (mul inputs)
            if SIGNAL_SETTINGS[select_signal]['length'] > 1:
                set_value = ''
                bit_num = SIGNAL_SETTINGS[select_signal]['length']
                for i in range( bit_num - len(set_value)):
                    set_value += '0'
                set_value = set_value

                set_value = set_value_reverse( set_value, node['IS_REVERSE'])
                
            ## 1 bit  select
            else:
                set_value = set_value_reverse('0', node['IS_REVERSE'])
                
            CONTENTS = add_signal_settings(CONTENTS, select_signal, set_value, signal_setting, IS_DEFAULT_SETTING = True)
                
    return CONTENTS
    
def get_signal_setting(node_id, select_node_id, idx, components_info, SIGNAL_SETTINGS):
    
    node = components_info[node_id]
    select_node = components_info[select_node_id]
    
    select_signal = ''
    set_value = ''
    signal_setting = ''

    ## 多個 selects -> 意味著 # of selects = # of inputs 且 selects 都為 1 bit
    if len(node['Selects']) > 1:
        select_signal = str(node['Selects'][idx])
        if select_signal != SELECT_SIGNAL_RESERVED:
            signal_setting = SIGNAL_SETTINGS[select_signal]['cmd_combo']
            
            for i in range(len(node['Inputs'])):
                if i == idx:
                    set_value = set_value_reverse('1', node['IS_REVERSE'])
                    break
    
    ## 單一 selects
    ## case 1: 多 bits select (mul inputs)
    ## case 2:  1 bit  select (2   inputs)
    elif len(node['Selects']) == 1:
        select_signal = str(node['Selects'][0])
        if select_signal != SELECT_SIGNAL_RESERVED:
            signal_setting = SIGNAL_SETTINGS[select_signal]['cmd_combo']
            
            ## 多 bits select (mul inputs)
            if SIGNAL_SETTINGS[select_signal]['length'] > 1:
                for i in range(len(node['Inputs'])):
                    if idx == i:
                        dec_val = i
                        break
                        
                bit_num = SIGNAL_SETTINGS[select_signal]['length']
                set_value = bin(dec_val).replace('0b', '')
                padding_zero = ''
                for i in range( bit_num - len(set_value)):
                    padding_zero += '0'
                set_value = padding_zero + set_value

                set_value = set_value_reverse( set_value, node['IS_REVERSE'])
                
            ## 1 bit  select
            else:
                if idx == 1:
                    set_value = set_value_reverse('1', node['IS_REVERSE'])
                else:
                    set_value = set_value_reverse('0', node['IS_REVERSE'])
                
    return select_signal, set_value, signal_setting
    
def get_path_from_xlsx(read_path_idx, all_path_file = 'all_path.xlsx', input_dir = INPUT_DIR):
    path = []
    all_path_file = file_with_dir_path(all_path_file, input_dir)
    wb = load_workbook(all_path_file)
    ws = wb.active
    idx = ws[read_path_idx+1][0]
    for cell in ws[read_path_idx+1][1:]:
        path.append(cell[:cell.find('(')])
        
    return path
    
def get_path_from_txt(read_path_idx, all_path_file = 'all_path.txt', input_dir = INPUT_DIR):
    path = []

    all_path_file = file_with_dir_path(all_path_file, input_dir)
    all_path_file = open(all_path_file, 'r')
    
    line = all_path_file.readlines()[read_path_idx]
    line = line[line.find(': ')+2:]
    
    for node in line.split():
        path.append(int(node))
        
    print(path)
        
    return path

def parse_inout_info(inout_info_file, input_dir):
    VIP_DEFINE_SETTINGS = {}
    VIP_ENABLE_SETTINGS = {}
    
    inout_info_file = file_with_dir_path(inout_info_file, input_dir)
    wb = load_workbook(inout_info_file)
    ws = wb.active
    col_names = []
    for cell in ws[1]:
        cell_value = cell.value
        if cell_value.replace(' ', '') != '':
            col_names.append(cell_value)
    col_names = col_names[2:]
    
    for row_idx, row in enumerate(ws):
        if row_idx != 0:
            VIP_DEFINE_SETTING = ''
            VIP_ENABLE_SETTING = ''
            for cell_idx, cell in enumerate(row[2:]):
                if cell.value and cell.value == 1:
                    if col_names[cell_idx].find('pattern_define') != -1:
                        VIP_DEFINE_SETTING += (col_names[cell_idx] + '\n')
                        VIP_DEFINE_SETTINGS.update({ row[0].value + ' ' + row[1].value : VIP_DEFINE_SETTING })
                    else:
                        VIP_ENABLE_SETTING += (col_names[cell_idx] + '\n')
                        VIP_ENABLE_SETTINGS.update({ row[0].value + ' ' + row[1].value : VIP_ENABLE_SETTING })
    
    return VIP_DEFINE_SETTINGS, VIP_ENABLE_SETTINGS
    
def parse_in_and_out_info(info_files, input_dir):
    VIP_DEFINE_SETTINGS = {}
    VIP_ENABLE_SETTINGS = {}
    
    for info_file in info_files:
        info_file = file_with_dir_path(info_file, input_dir)
        wb = load_workbook(info_file)
        ws = wb.active
        col_names = []
        for cell in ws[1]:
            cell_value = cell.value
            if cell_value.replace(' ', '') != '':
                col_names.append(cell_value)
        col_names = col_names[1:]
        
        for row_idx, row in enumerate(ws):
            if row_idx != 0:
                VIP_DEFINE_SETTING = ''
                VIP_ENABLE_SETTING = ''
                for cell_idx, cell in enumerate(row[1:]):
                    if cell.value and cell.value == 1:
                        if col_names[cell_idx].find('pattern_define') != -1:
                            VIP_DEFINE_SETTING += (col_names[cell_idx] + '\n')
                            VIP_DEFINE_SETTINGS.update({ row[0].value : VIP_DEFINE_SETTING })
                        else:
                            VIP_ENABLE_SETTING += (col_names[cell_idx] + '\n')
                            VIP_ENABLE_SETTINGS.update({ row[0].value : VIP_ENABLE_SETTING })
    
    return VIP_DEFINE_SETTINGS, VIP_ENABLE_SETTINGS
    
def parse_reg_info(reg_info_file, input_dir):
    SIGNAL_SETTINGS = {}
    
    reg_info_file = file_with_dir_path(reg_info_file, input_dir)
    wb = load_workbook(reg_info_file)
    ws = wb.active
    #read_cmd_reg = REG_READ_WRITE_VARIABLE_NAME
    col_names = []
    for cell in ws[1]:
        cell_value = cell.value
        if cell_value.replace(' ', '') != '':
            col_names.append(cell_value)
            
    for row_idx, row in enumerate(ws):
        if row_idx != 0 and row[0].value and row[1].value and row[2].value and row[3].value and row[4].value:
            signal    = row[0].value
            address   = row[1].value
            bits      = row[2].value
            read_cmd  = row[3].value
            write_cmd = row[4].value
            cmd_combo = ''
            
            address = "{}'h{}".format(len(address)*4, address)
            #cmd_combo  = read_cmd + ', {}, {});\n'.format(address, read_cmd_reg)
            cmd_combo  = read_cmd.replace(REG_READ_WRITE_CMD_ADDR, address).replace(REG_READ_WRITE_VARIABLE, REG_READ_WRITE_VARIABLE_NAME) + '\n'
            cmd_combo += REG_READ_WRITE_VARIABLE_NAME + '[{}]'.format(bits)
            
            delta = -1
            if bits.find(':') != -1:
                start = int(bits[:bits.find(':')])
                end   = int(bits[bits.find(':')+1:])
                delta = int(abs(end-start))+1

                cmd_combo += " = {}'b".format(delta)
                cmd_combo += 'set_value;\n'
            else:
                cmd_combo += " = 1'b"
                cmd_combo += 'set_value;\n'
                delta = 1
                
            cmd_combo += write_cmd.replace(REG_READ_WRITE_CMD_ADDR, address).replace(REG_READ_WRITE_VARIABLE, REG_READ_WRITE_VARIABLE_NAME) + '\n'
            SIGNAL_SETTINGS.update( {signal : {'cmd_combo': cmd_combo, 'length': delta}} )
            
    return SIGNAL_SETTINGS
    
    
def cnt_SRC_in_path(path, components_info):
    SRC_NAME = 'SRC'
    SRC_cnt = 0.0
    
    for node in path:
        if components_info[int(node)]['Type'] == SRC_NAME:
            SRC_cnt += 1.0
    
    return math.ceil(SRC_cnt / 2.0)
        
    

def pattern_auto_gen(read_path_idx_list, components_info, all_path, in_and_out_info_files = ['in_info.xlsx', 'out_info.xlsx'], reg_info_file = 'reg_info.xlsx', output_dir = PATTERN_DIR, input_dir = INPUT_DIR):
    VIP_DEFINE_SETTINGS, VIP_ENABLE_SETTINGS = parse_in_and_out_info(in_and_out_info_files, input_dir)
    SIGNAL_SETTINGS = parse_reg_info(reg_info_file, input_dir)
        
    for read_path_idx in read_path_idx_list:
        CONTENTS = []
        contents_append_endl(CONTENTS, SIGNATURE)
        
        class_name = 'audio_data_path_auto_gen_pattern_path_{}'.format(read_path_idx)
        path   = all_path.get_path_by_id(read_path_idx)
        input  = int(path[-1])
        output = int(path[0])
        input_signal  = components_info[input]['Outputs'][0]
        output_signal = components_info[output]['Inputs'][0]
        
        ## class init
        if input_signal in VIP_DEFINE_SETTINGS:
            contents_append_endl(CONTENTS, VIP_DEFINE_SETTINGS[input_signal])
        if output_signal in VIP_DEFINE_SETTINGS:
            contents_append_endl(CONTENTS, VIP_DEFINE_SETTINGS[output_signal])
            
        contents_append_endl(CONTENTS, 'class {} extends audio_data_path_golden;'.format(class_name))
        contents_append_tab_endl(CONTENTS, '`uvm_component_utils({})'.format(class_name))
        
        contents_append_endl(CONTENTS, '')
        
        ## new function
        contents_append_tab_endl(CONTENTS, 'function new(string name, uvm_component parent);')
        contents_append_tab_tab_endl(CONTENTS, 'super.new(name, parent);')
        contents_append_tab_endl(CONTENTS, 'endfunction')
        
        contents_append_endl(CONTENTS, '')

        ## build phase
        contents_append_tab_endl(CONTENTS, 'virtual function void build_phase(uvm_phase phase);')
        contents_append_tab_tab_endl(CONTENTS, 'super.build_phase(phase);')
        if input_signal in VIP_ENABLE_SETTINGS:
            for line in VIP_ENABLE_SETTINGS[input_signal].splitlines():
                contents_append_tab_tab_endl(CONTENTS, line)
                
        if output_signal in VIP_ENABLE_SETTINGS:
            for line in VIP_ENABLE_SETTINGS[output_signal].splitlines():
                contents_append_tab_tab_endl(CONTENTS, line)
                
            # audo gen channel_enable
        for idx, output_node in enumerate(get_nodes_by_type(components_info, 'Output_Node')):
            if output_node['NODE_ID'] == components_info[output]['NODE_ID']:
                contents_append_tab_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].channel_enable = 1;' % idx)

        # expect log
        expect_path_log = path_list_to_string(path)
        contents_append_tab_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].expect_path_log = "{}";'.format(expect_path_log))
        
        # amp adjustment
        SRC_cnt   = cnt_SRC_in_path(path, components_info)
        SRC_decay = 1.5
        contents_append_tab_tab_endl(CONTENTS, 'sys_cfg.audio_data_path_cfg[0].audio_data_path_channel_cfg[%3s].amp_threshold -= %d;' % (idx, SRC_cnt * SRC_decay))
        
        contents_append_tab_endl(CONTENTS, 'endfunction')
        
        contents_append_endl(CONTENTS, '')
        
        ## reset_phase
        contents_append_tab_endl(CONTENTS, 'virtual task reset_phase(uvm_phase phase);')
        contents_append_tab_tab_endl(CONTENTS, 'super.reset_phase(phase);')
        contents_append_tab_endl(CONTENTS, 'endtask')
        
        contents_append_endl(CONTENTS, '')
        
        ## audio_data_path_default_reg_config
        contents_append_tab_endl(CONTENTS, 'virtual task audio_data_path_default_reg_config();')
        contents_append_endl(CONTENTS, '')
        for component_info in components_info:
            CONTENTS = get_signal_default_settings(CONTENTS, component_info, SIGNAL_SETTINGS)
                
        contents_append_tab_endl(CONTENTS, 'endtask')
        contents_append_endl(CONTENTS, '')
        
        ## audio_data_path_reg_config
        contents_append_tab_endl(CONTENTS, 'virtual task audio_data_path_reg_config();')
        contents_append_endl(CONTENTS, '')
        
        edges  = get_edges_from_path(path)
        for edge in edges:
            node   = components_info[edge[0]]
            select = edge[1]

            for idx, select_node in enumerate(node['select']):
                if select == select_node:
                    select_signal, set_value, signal_setting = get_signal_setting(edge[0], edge[1], idx, components_info, SIGNAL_SETTINGS)
                    CONTENTS = add_signal_settings(CONTENTS, select_signal, set_value, signal_setting, edge[0], edge[1])
                    break
                        
        contents_append_tab_endl(CONTENTS, 'endtask')
        
        contents_append_endl(CONTENTS, '')
        
        ## main_phase
        contents_append_tab_endl(CONTENTS, 'virtual task main_phase(uvm_phase phase);')
        path_string = ''
        for idx, node_id in enumerate(reversed(path)):
            path_string += '{}'.format(node_id)
            if idx == 0:
                path_string += '(Input) '
            elif idx == (len(path)-1) :
                path_string += '(Output) '
            else:
                path_string += ' '

        contents_append_tab_tab_endl(CONTENTS, '`uvm_info("audio_data_path_pattern", "Path[{}]: {}", UVM_LOW)'.format(read_path_idx, path_string))
        for idx, node_id in enumerate(path):
            node = components_info[node_id]
            temp_content  = '`uvm_info("audio_data_path_pattern", "Node['
            temp_content += '%3s' % node_id
            temp_content += ']('
            temp_content += '%35s' % node['Type']
            
            if node['Type'] == 'Output_Node':
                sig_info = node['Inputs'][0]
                temp_content += '),  input signal: '
                temp_content += '%35s' % sig_info
                temp_content += '", UVM_LOW)'
                contents_append_tab_tab_endl(CONTENTS, temp_content)
            else:
                sig_info = node['Outputs'][0]
                temp_content += '), output signal: '
                temp_content += '%35s' % sig_info
                temp_content += '", UVM_LOW)'
                contents_append_tab_tab_endl(CONTENTS, temp_content)
            
        contents_append_tab_tab_endl(CONTENTS, 'super.main_phase(phase);')
        contents_append_tab_endl(CONTENTS, 'endtask')
        
        contents_append_endl(CONTENTS, '')
        
        ## end class
        contents_append_endl(CONTENTS, 'endclass: {}'.format(class_name))
        
        output_file_name = class_name + '.sv'
        write_contents_to_file(CONTENTS, output_file_name, output_dir, ENDL = '')

def save_json(G, fname):
    json.dump(dict(nodes=[[n, G.node[n]] for n in G.nodes()],
                   edges=[[u, v, G.edge[u][v]] for u,v in G.edges()]),
              open(fname, 'w'), indent=2)
         
def check_merge(CHECK_ALL_PASS, CHECK_PASS):
    if CHECK_PASS:
        PASS_MESSAGE()
    else:
        FAIL_MESSAGE()
    return CHECK_PASS and CHECK_ALL_PASS

def construct_edge_sheet(edge_covered_map, wb, sheet_name = ''):
    if not sheet_name:
        ws = wb.active
    else:
        wb.create_sheet(sheet_name)
        ws = wb[sheet_name]
    
    
    not_covered_edges = [ k for k in edge_covered_map if edge_covered_map[k] == False ]
    covered_edges     = [ k for k in edge_covered_map if edge_covered_map[k] == True  ]
    
    for edge in not_covered_edges:
        row = ['{}'.format(edge), 'not covered']
        ws.append(row)
        
    for edge in covered_edges:
        row = ['{}'.format(edge), 'covered']
        ws.append(row)

    for idx in range(len(not_covered_edges)):
        for cell in ws[str(idx+1)]:
            if cell.value:
                cell.fill = PatternFill(start_color="8B0000", fill_type = "solid")
                
    ws = excel_auto_width(ws)
    return ws
    
def construct_chosen_path_sheet(all_path, chosen_path_idx_list, components_info, wb, sheet_name = '', DETAIL = False):
    if not sheet_name:
        ws = wb.active
    else:
        wb.create_sheet(sheet_name)
        ws = wb[sheet_name]
        
    for idx in chosen_path_idx_list:
        row = ['Path[%7s]' % idx]
        
        for node in all_path[idx]:
            component = components_info[node]
            if not DETAIL:
                    row.append('%5s' % format(node))
            else:
                if component['Type'] == 'Output_Node':
                    row.append('{}({})-{}'.format(node, component['Type'], components_info[node]['Inputs'][0]))
                else:
                    row.append('{}({})-{}'.format(node, component['Type'], components_info[node]['Outputs'][0]))
        ws.append(row)
        
    ws = excel_auto_width(ws)
    return ws
    
def get_sorted_components_info_type(components_info):
    result = []
    for type in sorted(list(set([component['Type'] for component in components_info]))):
        if type == 'Input_Node':
            result.insert(0, type)
        elif type == 'Output_Node':
            result.insert(1, type)
        else:
            result.append(type)
            
    return result

def edge_coverage_evaluation(all_path, chosen_path_idx_list):
    edge_coverage_dict = {}
    for chosen_path_idx in chosen_path_idx_list:
        for edge in get_edges_from_path(all_path[chosen_path_idx]):
            if edge in edge_coverage_dict:
                edge_coverage_dict.update( {edge: edge_coverage_dict[edge] + 1 } )
            else:
                edge_coverage_dict.update( {edge: 1} )
                
    return edge_coverage_dict
    
def input_output_evaluation(all_path, chosen_path_idx_list, components_info, IS_MMAP_MODE = True):
    input_node_list  = []
    output_node_list = []
    
    for chosen_path_idx in chosen_path_idx_list:
        if not IS_MMAP_MODE:
            input_node  = components_info[all_path[chosen_path_idx][-1]]
            output_node = components_info[all_path[chosen_path_idx][0]]
        else:
            chosen_path = all_path.get_path_by_id(chosen_path_idx)
            input_node  = components_info[chosen_path[-1]]
            output_node = components_info[chosen_path[0]]
            
        input_node_list.append(input_node['Outputs'][0])
        output_node_list.append(output_node['Inputs'][0])
        
    input_node_list = sorted(list(set(input_node_list)))
    output_node_list = sorted(list(set(output_node_list)))
    
    return input_node_list, output_node_list
                
def gen_coverage_report(components_parsing_rule, edge_covered_map, all_path, chosen_path_idx_list, components_info, all_register_info, output_file_name = 'coverage_report.xlsx', output_dir = REPORT_DIR, IS_MMAP_MODE = True):
    wb = Workbook()
    BLANK_CELL = '            '
    col_names  = ['input node covered', 'output node covered', BLANK_CELL,
                  'component name', 'component covered amount', BLANK_CELL,
                  'edge coverage', 'DD waved edge', '[WARNING]not covered input', '[WARNING]not covered mute', BLANK_CELL,
                  'path chosen']
    wb.create_sheet('coverage overview')
    ws = wb['coverage overview']
    ws = create_excel_table_title(ws, col_names)

    # input/output overview
    input_list, output_list = input_output_evaluation(all_path, chosen_path_idx_list, components_info)
    for idx, input in enumerate(input_list):
        ws.cell(row = (2 + idx),  column = 1).value = input
        
    for idx, output in enumerate(output_list):
        ws.cell(row = (2 + idx),  column = 2).value = output
    #input_cnt  = 0
    #output_cnt = 0
    #for component in components_info:
    #    if component['Type'] == 'Input_Node':
    #        ws.cell(row = (2 + input_cnt),  column = 1).value = component['Outputs'][0]
    #        input_cnt += 1
    #    elif component['Type'] == 'Output_Node':
    #        ws.cell(row = (2 + output_cnt), column = 2).value = component['Inputs'][0]
    #        output_cnt += 1
          
    # component overview
    component_type_cnt = 0
    component_cnt      = 0
    for type in get_sorted_components_info_type(components_info):
        ws.cell(row = (2 + component_type_cnt),  column = 4).value = type
        ws.cell(row = (2 + component_type_cnt),  column = 5).value = len([ component for component in components_info if component['Type'] == type])
        component_type_cnt += 1
        component_cnt += len([ component for component in components_info if component['Type'] == type])
    
    ws.cell(row = (2 + component_type_cnt),  column = 4).value = 'Total'
    ws.cell(row = (2 + component_type_cnt),  column = 4).font = Font(bold=True)
    ws.cell(row = (2 + component_type_cnt),  column = 4).fill = PatternFill(start_color="03CAFC", fill_type = "solid")
    ws.cell(row = (2 + component_type_cnt),  column = 5).value = component_cnt
    ws.cell(row = (2 + component_type_cnt),  column = 5).font = Font(bold=True)
    ws.cell(row = (2 + component_type_cnt),  column = 5).fill = PatternFill(start_color="03CAFC", fill_type = "solid")
    
        
    # coverage overview
    covered_edge_num = len([ k for k in edge_covered_map if edge_covered_map[k] == True ])
    total_edge_num   = len(edge_covered_map)
    edge_coverage = '{} / {} ({:.2%})'.format( covered_edge_num, total_edge_num, float(covered_edge_num) / float(total_edge_num))
    
    if not IS_MMAP_MODE:
        num_path = len(all_path)
    else:
        num_path = all_path.num_path
        
    path_coverage = '{} / {} ({:.5%})'.format( len(chosen_path_idx_list), num_path, float(len(chosen_path_idx_list)) / float(num_path))
    EDGE_COVERAGE_CELL = ws.cell(row = 2,  column = 7)
    EDGE_COVERAGE_CELL.value = edge_coverage
    EDGE_COVERAGE_CELL.font  = Font(bold=True)
    if covered_edge_num < total_edge_num:
        EDGE_COVERAGE_CELL.fill = PatternFill(start_color="C9463C", fill_type = "solid")
    else:
        EDGE_COVERAGE_CELL.fill = PatternFill(start_color="65CC62", fill_type = "solid")

    ws.cell(row = 2,  column = 12).value = path_coverage
    
    # waved edge
    ignored_switch_count = 0
    for component in components_info:
        for idx, connect in enumerate(component['select']):
            if connect == NULL_NODE_ID:
                ws.cell(row = 2 + ignored_switch_count, column = 8).value = 'input[{}] of component[{}]: {}'.format(idx, component['NODE_ID'], component['Inputs'][idx])
                ws.cell(row = 2 + ignored_switch_count, column = 8).fill = PatternFill(start_color="C4540E", fill_type = "solid")
                ignored_switch_count += 1
                
    # Not_Covered_Inputs
    not_covered_inputs_count = 0
    for component in components_info:
        if 'Not_Covered_Inputs' in component:
            for idx, input in enumerate(component['Not_Covered_Inputs']): 
                ws.cell(row = 2 + not_covered_inputs_count, column = 9).value = '{} of component[{}]'.format(input, component['NODE_ID'])
                ws.cell(row = 2 + not_covered_inputs_count, column = 9).fill = PatternFill(start_color="C4540E", fill_type = "solid")
                not_covered_inputs_count += 1
    
    # Not_Covered_Select
    not_covered_select_count = 0
    for component in components_info:
        if 'Not_Covered_Select' in component:
            for idx, select in enumerate(component['Not_Covered_Select']): 
                ws.cell(row = 2 + not_covered_select_count, column = 10).value = '{} of component[{}]'.format(select, component['NODE_ID'])
                ws.cell(row = 2 + not_covered_select_count, column = 10).fill = PatternFill(start_color="C4540E", fill_type = "solid")
                not_covered_select_count += 1

    ws = excel_auto_width(ws)
    
    # all edge
    #construct_edge_sheet(edge_covered_map, wb, 'edges info')
    
    # chosen path
    #construct_chosen_path_sheet(all_path, chosen_path_idx_list, components_info, wb, 'chosen_path', False)
    
    # chosen path in detail
    #construct_chosen_path_sheet(all_path, chosen_path_idx_list, components_info, wb, 'chosen_path_detail', True)
    
    # all path
    #construct_path_sheet(all_path, chosen_path_idx_list, components_info, wb, 'all_path', False)
    
    # all path in detail
    #construct_path_sheet(all_path, chosen_path_idx_list, components_info, wb, 'all_path_detail', True)
    
    # components_info
    #construct_components_info_sheet(components_info, wb, 'components_info')
    
    # registed_info
    #construct_registed_info_sheet(all_register_info, wb, 'register_info')
    
    
    output_file_name = file_with_dir_path(output_file_name, output_dir)
    backup_file(output_file_name)
    wb.remove(wb['Sheet'])
    wb.save(output_file_name)











def gen_stereo_componenet_dict():
    stereo_component_dict = dict()
    stereo_component_dict['if1_out_0'] = 'if1_out_1'
    stereo_component_dict['if1_out_1'] = 'if1_out_0'
    stereo_component_dict['if1_out_2'] = 'if1_out_3'
    stereo_component_dict['if1_out_3'] = 'if1_out_2'
    stereo_component_dict['if1_out_4'] = 'if1_out_5'
    stereo_component_dict['if1_out_5'] = 'if1_out_4'
    stereo_component_dict['if1_out_6'] = 'if1_out_7'
    stereo_component_dict['if1_out_7'] = 'if1_out_6'
    stereo_component_dict['if2_out_0'] = 'if2_out_1'
    stereo_component_dict['if2_out_1'] = 'if2_out_0'
    stereo_component_dict['if2_out_2'] = 'if2_out_3'
    stereo_component_dict['if2_out_3'] = 'if2_out_2'
    stereo_component_dict['if2_out_4'] = 'if2_out_5'
    stereo_component_dict['if2_out_5'] = 'if2_out_4'
    stereo_component_dict['if2_out_6'] = 'if2_out_7'
    stereo_component_dict['if2_out_7'] = 'if2_out_6'
    stereo_component_dict['if3_out_0'] = 'if3_out_1'
    stereo_component_dict['if3_out_1'] = 'if3_out_0'
    stereo_component_dict['if3_out_2'] = 'if3_out_3'
    stereo_component_dict['if3_out_3'] = 'if3_out_2'
    stereo_component_dict['if3_out_4'] = 'if3_out_5'
    stereo_component_dict['if3_out_5'] = 'if3_out_4'
    stereo_component_dict['if3_out_6'] = 'if3_out_7'
    stereo_component_dict['if3_out_7'] = 'if3_out_6'
    stereo_component_dict['if4_out_r'] = 'if4_out_l'
    stereo_component_dict['if4_out_l'] = 'if4_out_r'
    stereo_component_dict['pdm1_dato_ri'] = 'pdm1_dato_fa'
    stereo_component_dict['pdm1_dato_fa'] = 'pdm1_dato_ri'
    stereo_component_dict['pdm2_dato_ri'] = 'pdm2_dato_fa'
    stereo_component_dict['pdm2_dato_fa'] = 'pdm2_dato_ri'
    stereo_component_dict['dp6_fifo_in0'] = 'dp6_fifo_in1'
    stereo_component_dict['dp6_fifo_in1'] = 'dp6_fifo_in0'
    stereo_component_dict['dp6_fifo_in2'] = 'dp6_fifo_in3'
    stereo_component_dict['dp6_fifo_in3'] = 'dp6_fifo_in2'
    stereo_component_dict['dp6_fifo_in4'] = 'dp6_fifo_in5'
    stereo_component_dict['dp6_fifo_in5'] = 'dp6_fifo_in4'
    stereo_component_dict['dp6_fifo_in6'] = 'dp6_fifo_in7'
    stereo_component_dict['dp6_fifo_in7'] = 'dp6_fifo_in6'
    stereo_component_dict['dp4_fifo_in0'] = 'dp4_fifo_in1'
    stereo_component_dict['dp4_fifo_in1'] = 'dp4_fifo_in0'
    stereo_component_dict['dp4_fifo_in2'] = 'dp4_fifo_in3'
    stereo_component_dict['dp4_fifo_in3'] = 'dp4_fifo_in2'
    stereo_component_dict['dp2_fifo_in0'] = 'dp2_fifo_in1'
    stereo_component_dict['dp2_fifo_in1'] = 'dp2_fifo_in0'
    stereo_component_dict['dp10_fifo_in0'] = 'dp10_fifo_in1'
    stereo_component_dict['dp10_fifo_in1'] = 'dp10_fifo_in0'
    stereo_component_dict['dp08_fifo_in0'] = 'dp08_fifo_in1'
    stereo_component_dict['dp08_fifo_in1'] = 'dp08_fifo_in0'
    stereo_component_dict['dp12_fifo_in0'] = 'dp12_fifo_in1'
    stereo_component_dict['dp12_fifo_in1'] = 'dp12_fifo_in0'

    stereo_component_dict['i2s1_in_ch0'] = 'i2s1_in_ch1'
    stereo_component_dict['i2s1_in_ch1'] = 'i2s1_in_ch0'
    stereo_component_dict['i2s1_in_ch2'] = 'i2s1_in_ch3'
    stereo_component_dict['i2s1_in_ch3'] = 'i2s1_in_ch2'
    stereo_component_dict['i2s1_in_ch4'] = 'i2s1_in_ch5'
    stereo_component_dict['i2s1_in_ch5'] = 'i2s1_in_ch4'
    stereo_component_dict['i2s1_in_ch6'] = 'i2s1_in_ch7'
    stereo_component_dict['i2s1_in_ch7'] = 'i2s1_in_ch6'
    stereo_component_dict['i2s2_in_ch0'] = 'i2s2_in_ch1'
    stereo_component_dict['i2s2_in_ch1'] = 'i2s2_in_ch0'
    stereo_component_dict['i2s2_in_ch2'] = 'i2s2_in_ch3'
    stereo_component_dict['i2s2_in_ch3'] = 'i2s2_in_ch2'
    stereo_component_dict['dmic12_dati_ri'] = 'dmic12_dati_fa'
    stereo_component_dict['dmic12_dati_fa'] = 'dmic12_dati_ri'
    stereo_component_dict['dmic34_dati_ri'] = 'dmic34_dati_fa'
    stereo_component_dict['dmic34_dati_fa'] = 'dmic34_dati_ri'
    stereo_component_dict['dmic56_dati_ri'] = 'dmic56_dati_fa'
    stereo_component_dict['dmic56_dati_fa'] = 'dmic56_dati_ri'
    stereo_component_dict['dmic78_dati_ri'] = 'dmic78_dati_fa'
    stereo_component_dict['dmic78_dati_fa'] = 'dmic78_dati_ri'
    stereo_component_dict['i2s3_in_ch0'] = 'i2s3_in_ch1'
    stereo_component_dict['i2s3_in_ch1'] = 'i2s3_in_ch0'
    stereo_component_dict['i2s4_in_ch0'] = 'i2s4_in_ch1'
    stereo_component_dict['i2s4_in_ch1'] = 'i2s4_in_ch0'
    stereo_component_dict['sdm_09_l'] = 'sdm_09_r'
    stereo_component_dict['sdm_09_r'] = 'sdm_09_l'
    stereo_component_dict['sdm_08_l'] = 'sdm_08_r'
    stereo_component_dict['sdm_08_r'] = 'sdm_08_l'
    stereo_component_dict['sdw_dp_1_ch0'] = 'sdw_dp_1_ch1'
    stereo_component_dict['sdw_dp_1_ch1'] = 'sdw_dp_1_ch0'
    stereo_component_dict['sdw_dp_1_ch2'] = 'sdw_dp_1_ch3'
    stereo_component_dict['sdw_dp_1_ch3'] = 'sdw_dp_1_ch2'
    
    return stereo_component_dict

def only_direct_edge(G, node_0, node_1):
    if  (node_0, node_1) in G.edges and (node_1, node_0) not in G.edges:
        return True
    else:
        return False


def find_stereo_path(G, components_info, input_node_index, stereo_component_dict, mono):
    stereo_path = []
    path_len = 0
    success_flag = True
    stereo_output_name = stereo_component_dict[components_info[mono[0]]['Inputs'][0]]   # find stereo output node name
    for i in range(len(components_info)):
        if components_info[i]['Inputs'] == [stereo_output_name]:
            stereo_path.append(i)                                                       # append stereo output node index
            path_len += 1
            break

    while(path_len != len(mono)):
        try:
            #print(stereo_path)
            if components_info[stereo_path[-1]]['Type'].find('MUX') != -1:
                mono_component_selects = components_info[mono[path_len-1]]['Selects'][0]
                next_component_selects = components_info[stereo_path[-1]]['Selects'][0]
                if mono_component_selects != next_component_selects:
                    # print(mono_component_selects, next_component_selects)
                    # print('MUX sel diff !')
                    next_sel_index = components_info[mono[path_len-1]]['select'].index(mono[path_len])
                    next_node_index = components_info[stereo_path[-1]]['select'][next_sel_index]
                    if next_node_index in input_node_index:            # this node is end of path -> break while loop
                        stereo_path.append(components_info[stereo_path[-1]]['select'][next_sel_index])
                        break
                    else:
                        print('illegal :  MUX sel diff !!!!!!!!!!!!!!')
                        success_flag = False
                        break
            next_sel_index = components_info[mono[path_len-1]]['select'].index(mono[path_len])
            # mono_component_name = components_info[mono[path_len-1]]['Inputs'][next_sel_index]
            # next_component_name = components_info[stereo_path[-1]]['Inputs'][next_sel_index]
            stereo_path.append(components_info[stereo_path[-1]]['select'][next_sel_index])
            path_len += 1
        except:
            success_flag = False
            print('find stereo path ERROR')
            break

    if success_flag == False:
        print(stereo_path)
        #exit()

    if len(set(mono+stereo_path)) != len(mono+stereo_path):
        for item in (set(mono) & set(stereo_path)):
            if item not in input_node_index:
                print('Stereo path found repeated node not in input_node list !!!!')
                success_flag = False
                #exit()
        #exit()

    print(stereo_path)
    return success_flag, stereo_path


def check_per_path(G, node_0, node_1, node_2, node_3=None):
    success_flag = True
    arr = []
    arr.append(node_0)
    arr.append(node_1)
    arr.append(node_2)
    if node_3 != None:
        arr.append(node_3)

    for i in range(len(arr)-1):
        for j in range(i+1, len(arr)):
            if nx.has_path(G, arr[i], arr[j]):
                pass
            else:
                success_flag = False
                break
        if success_flag == False:
            break
    return success_flag

def permutation_find_path(G, node_0, node_1, node_2, node_3=None):
    if node_3==None:
        PATH_A = [node_0, node_1]
        PATH_B = [node_1, node_2]
        path_list = [PATH_A, PATH_B]
        per_list = permutations(path_list)
    else:
        PATH_A = [node_0, node_1]
        PATH_B = [node_1, node_2]
        PATH_C = [node_2, node_3]
        path_list = [PATH_A, PATH_B, PATH_C]
        per_list = permutations(path_list)
    
    mix = []
    success_flag = False

    per = permutations(range(2))
    per_table_sort_2 = np.argsort([i for i in per])
    per = permutations(range(3))
    per_table_sort_3 = np.argsort([i for i in per])

    for i, item in enumerate(per_list):
        #print(item)
        #print(item[per_table_sort[i][0]], item[per_table_sort[i][1]], item[per_table_sort[i][2]])

        per_pick_nodes = set([y for x in item for y in x])

        remove_node = per_pick_nodes - set([x for x in item[0]])
        G_tmp = G.copy()
        for node in remove_node:
            G_tmp.remove_node(node)
        if nx.has_path(G_tmp, item[0][0], item[0][1]):
            all_path_a = nx.all_shortest_paths(G_tmp, item[0][0], item[0][1])
        else:
            continue

        for a in all_path_a:
            remove_node = (per_pick_nodes | set(a)) - set([x for x in item[1]])
            G_tmp = G.copy()
            for node in remove_node:
                G_tmp.remove_node(node)
            if nx.has_path(G_tmp, item[1][0], item[1][1]):
                all_path_b = nx.all_shortest_paths(G_tmp, item[1][0], item[1][1])
            else:
                continue

            for b in all_path_b:
                if node_3==None:
                    combine_path = [a, b]
                    mix = combine_path[per_table_sort_2[i][0]] + combine_path[per_table_sort_2[i][1]][1:]
                    success_flag = True
                    break
                remove_node = (per_pick_nodes | set(a) | set(b)) - set([x for x in item[2]])
                G_tmp = G.copy()
                for node in remove_node:
                    G_tmp.remove_node(node)
                if nx.has_path(G_tmp, item[2][0], item[2][1]):
                    c = nx.shortest_path(G_tmp, item[2][0], item[2][1])
                    combine_path = [a, b, c]
                    mix = combine_path[per_table_sort_3[i][0]] + combine_path[per_table_sort_3[i][1]][1:] + combine_path[per_table_sort_3[i][2]][1:]
                    success_flag = True
                    break
            if success_flag == True:
                    break

    # if cou > 1:
    #     print('OMG')
    #     print(cou)
    # if success_flag == False or len(set(mix)) != len(mix):
    #     print('SECOND METHOD NOT FOUND')
    
    return success_flag, mix

def gen_find_path(pn2_has_edge):
    find_path_flag = False
    find_path = []
    not_found_path_node = []
    illegal_stereo_path_node = []
    
    for i in range(len(pn2_has_edge)):
        find_path_flag = False
        print('{:>4d}->{:<4d}: '.format(pn2_has_edge[i][0], pn2_has_edge[i][1]))
        if components_info[pn2_has_edge[i][1]]['Type'] == 'Input_Node':
            for output_node in output_node_index:
                if check_per_path(G, output_node, pn2_has_edge[i][0], pn2_has_edge[i][1]):
                    tmp_a = nx.shortest_path(G, output_node, pn2_has_edge[i][0])
                    tmp_b = nx.shortest_path(G, pn2_has_edge[i][0], pn2_has_edge[i][1])
                    tmp_mix = tmp_a + tmp_b[1:]
                    
                    if len(set(tmp_mix)) != len(tmp_mix):
                        #print(tmp_mix)
                        # print('GG')
                        find_path_flag, tmp_mix = permutation_find_path(G, output_node, pn2_has_edge[i][0], pn2_has_edge[i][1])
                        if find_path_flag == False:
                            continue
                        
                    print(tmp_mix)
                    find_path_flag, tmp_mix_stereo = find_stereo_path(G, components_info, input_node_index, stereo_component_dict, tmp_mix)
                    if find_path_flag == False and [pn2_has_edge[i][0], pn2_has_edge[i][1]] not in illegal_stereo_path_node:
                        illegal_stereo_path_node.append([pn2_has_edge[i][0], pn2_has_edge[i][1]])
                        continue
                    find_path.append([tmp_mix, tmp_mix_stereo])
                    find_path_flag = True
                    break
        else:
            for output_node in output_node_index:
                for input_node in input_node_index:
                    #print('Try ', output_node, input_node)
                    if check_per_path(G, output_node, pn2_has_edge[i][0], pn2_has_edge[i][1], input_node):
                        tmp_a = nx.shortest_path(G, output_node, pn2_has_edge[i][0])
                        tmp_b = nx.shortest_path(G, pn2_has_edge[i][0], pn2_has_edge[i][1])
                        tmp_c = nx.shortest_path(G, pn2_has_edge[i][1], input_node)
                        tmp_mix = tmp_a + tmp_b[1:] + tmp_c[1:]

                        if len(set(tmp_mix)) != len(tmp_mix):
                            #print(tmp_mix)
                            #print('QQ')
                            find_path_flag, tmp_mix = permutation_find_path(G, output_node, pn2_has_edge[i][0], pn2_has_edge[i][1], input_node)
                            if find_path_flag == False:
                                continue
                        
                        print(tmp_mix)
                        find_path_flag, tmp_mix_stereo = find_stereo_path(G, components_info, input_node_index, stereo_component_dict, tmp_mix)
                        if find_path_flag == False and [pn2_has_edge[i][0], pn2_has_edge[i][1]] not in illegal_stereo_path_node:
                            illegal_stereo_path_node.append([pn2_has_edge[i][0], pn2_has_edge[i][1]])
                            continue
                        find_path.append([tmp_mix, tmp_mix_stereo])
                        find_path_flag = True
                        break
                if find_path_flag == True:
                    break

        if find_path_flag == False:
            print('FAIL !!! some shortest path of pn2_has_edge not found')
            not_found_path_node.append([pn2_has_edge[i][0], pn2_has_edge[i][1]])
            #exit()
    return find_path, not_found_path_node, illegal_stereo_path_node


def greedy_pick_path(find_path, pn2_has_edge):
    greedy_choose_path = []
    max_match_num = [0, 0, []]       # [max_num, find_path idx, delete_idx array]
    useless_path = []                # 存放 在find_path中 沒有用的path idx (len(delete_idx)==0)
    last_max_num = -1                # 上一次找到的 max_num 值
    start_idx = 0                    # 從 start_idx 開始找 find_path for loop
    DEF_MAX_VAULE = 99999999
    end_idx = DEF_MAX_VAULE
    
    start_time = time.time()

    while(True):
        if end_idx == DEF_MAX_VAULE:
            max_match_num = [0, 0, []]
            useless_path = []
        print('now find_path :', len(find_path), 'now pn2_has_edge :', len(pn2_has_edge))
        for i in range(len(find_path)):
            if i < start_idx or i > end_idx:      # start_idx >= i >= end_idx  not continue
                continue
            delete_idx = []
            for edge_idx in range(len(pn2_has_edge)):
                mono_0_path = find_path[i][0]
                for mono_0_pre in range(len(mono_0_path)):
                    if pn2_has_edge[edge_idx][0] == mono_0_path[mono_0_pre]:
                        for mono_0_post in range(mono_0_pre+1, len(mono_0_path)):
                            if pn2_has_edge[edge_idx][1] == mono_0_path[mono_0_post]:
                                #print('mono_0 find edge :', edge_idx, pn2_has_edge[edge_idx])
                                delete_idx.append(edge_idx)

                mono_1_path = find_path[i][1]
                for mono_1_pre in range(len(mono_1_path)):
                    if pn2_has_edge[edge_idx][0] == mono_1_path[mono_1_pre]:
                        for mono_1_post in range(mono_1_pre+1, len(mono_1_path)):
                            if pn2_has_edge[edge_idx][1] == mono_1_path[mono_1_post]:
                                #print('mono_1 find edge :', edge_idx, pn2_has_edge[edge_idx])
                                delete_idx.append(edge_idx)
            
            if len(delete_idx) == 0:
                useless_path.append(i)

            if max_match_num[0] < len(delete_idx):
                max_match_num[0] = len(delete_idx)
                max_match_num[1] = i
                max_match_num[2] = delete_idx
                if last_max_num == max_match_num[0]:    # 如果目前找到的 max_num 是上一次找到的 max_num(last_max_num) 就可以不用繼續找了
                    break
            elif end_idx != DEF_MAX_VAULE and max_match_num[0] == len(delete_idx) and max_match_num[1] > i:
                max_match_num[0] = len(delete_idx)
                max_match_num[1] = i
                max_match_num[2] = delete_idx

            # print(delete_idx)
            # print(len(delete_idx))
        
        if max_match_num[0] == 0:       # can't be found pn2_has_edge anymore
            if start_idx != 0:
                start_idx = 0
                continue
            else:
                break
        
        if last_max_num != max_match_num[0] and start_idx != 0:
            end_idx = start_idx
            start_idx = 0
            continue

        print(max_match_num[0], max_match_num[1])

        last_max_num = max_match_num[0]                 # update last_max_num value
        start_idx = max_match_num[1] - len(useless_path)
        end_idx = DEF_MAX_VAULE

        greedy_choose_path.append(find_path[max_match_num[1]])
        useless_path.append(max_match_num[1])
        delete_tmp = sorted(useless_path, reverse=True)
        for item in delete_tmp:
            del find_path[item]
        delete_tmp = max_match_num[2][::-1]
        for item in delete_tmp:
            del pn2_has_edge[item]
        
        if len(pn2_has_edge) == 0:       # covered every pair in pn2_has_edge -> finish
            break
    
    print(time.time()-start_time)
    return greedy_choose_path, pn2_has_edge

if __name__ == '__main__':
    ################################################################## main ##################################################################
    components_parsing_rule = get_components_parsing_rule()
    components_info = get_components_info(components_parsing_rule)
    components_info = make_distinct(components_info)
    components_info = to_lower(components_info)
    components_info = sort_components_info(components_info)
    components_info = set_components_id(components_info)

    # find MIX_xto1, auto gen x new blocks
    old_component_num = len(components_info)
    new_block_cou = old_component_num
    mix_permuation_pair = []                     # these pairs are impossible to construct to a path
    for i in range(old_component_num):
        if components_info[i]['Type'].find('MIX') != -1:
            mix_num = int(components_info[i]['Type'].split('MIX_')[-1].split('to')[0])
            per_pair = []
            for mix_idx in range(mix_num):
                mix_input_name = components_info[i]['Inputs'][mix_idx]
                components_info[i]['Inputs'][mix_idx] = mix_input_name + '_new'
                tmp_dict = {'Type':'Block', 'IS_REVERSE':False, 'Outputs':[mix_input_name + '_new'], 'Selects':[], 'Inputs':[mix_input_name], 'NODE_ID':new_block_cou}
                components_info.append(tmp_dict)
                per_pair.append(new_block_cou)
                new_block_cou += 1
            for item in permutations(per_pair, 2):
                mix_permuation_pair.append(item)
    print(mix_permuation_pair)
    

    print('output_components_info...')
    output_components_info(components_info)
    print('done\n')

    print('parse_register_file...')
    all_register_info = parse_register_file()
    if not all_register_info:
        ERROR_MESSAGE('all_register_info not prepared')
    else:
        output_register_info(all_register_info)
        print('done\n')

    ####################################### check flow #######################################
    print('check_single_output...')
    CHECK_PASS = check_single_output(components_info)
    CHECK_ALL_PASS = check_merge(CHECK_PASS, CHECK_PASS)

    print('check_output_distinct...')
    CHECK_PASS = check_output_distinct(components_info)
    CHECK_ALL_PASS = check_merge(CHECK_ALL_PASS, CHECK_PASS)

    print('check_output_connection...')
    CHECK_PASS = check_output_connection(components_info)
    CHECK_ALL_PASS = check_merge(CHECK_ALL_PASS, CHECK_PASS)

    print('check_input_connection...')
    CHECK_PASS = check_input_connection(components_info)
    CHECK_ALL_PASS = check_merge(CHECK_ALL_PASS, CHECK_PASS)

    print('check_select_and_input_num...')
    CHECK_PASS = check_select_and_input_num(components_info)
    CHECK_ALL_PASS = check_merge(CHECK_ALL_PASS, CHECK_PASS)

    print('check_select_in_all_register_info...')
    CHECK_PASS = check_select_in_all_register_info(components_info, all_register_info)
    CHECK_ALL_PASS = check_merge(CHECK_ALL_PASS, CHECK_PASS)

    print('check_select_distinct...')
    CHECK_PASS = check_select_distinct(components_info)
    CHECK_PASS = True
    CHECK_ALL_PASS = check_merge(CHECK_ALL_PASS, CHECK_PASS)

    print('check_components_info_and_all_register_info...')
    CHECK_PASS = check_components_info_and_all_register_info(components_info, all_register_info)
    CHECK_ALL_PASS = check_merge(CHECK_ALL_PASS, CHECK_PASS)
    ####################################### check flow #######################################
    
    print('output_mux_gentop...')
    output_mux_gentop(components_info)
    print('done\n')

    if CHECK_ALL_PASS:
        PASS_MESSAGE('Check all pass\n')
        
        if not FOR_SD_CHECK_ONLY:  
            print('make_legal...')
            components_info = make_legal(components_info)
            print('done\n')
        else:
            print('make_legal...')
            components_info = make_legal(components_info)
            print('done\n')
                
        if not FOR_SD_CHECK_ONLY:
            print('gen_content_of_cust_system_configuration...')
            gen_content_of_cust_system_configuration(components_info)
            print('done\n')
            
            print('gen_audio_data_path_golden_pattern...')
            gen_audio_data_path_golden_pattern(components_info)
            print('done\n')
            
        if not FOR_SD_CHECK_ONLY:
            print('gen_transition_model...')
            components_info = gen_transition_model(components_info)
            print('done\n')
        else:
            components_info = gen_transition_model(components_info, output_enable = False)
            
        print('output_components_info...')
        output_components_info(components_info)
        print('done\n')
        

            
        print('output_components_info_xlsx...')
        output_components_info_xlsx(components_info)
        print('done\n')
            
        if not FOR_SD_CHECK_ONLY:   
            print('gen_dut_wrapper...')
            gen_dut_wrapper(components_info)
            print('done\n')
            
            print('gen_system_base_test...')
            gen_system_base_test(components_info)
            print('done\n')
            
            print('gen_interface...')
            gen_interface(components_info)
            print('done\n')
            
            print('gen_transaction...')
            gen_transaction(components_info)
            print('done\n')
            
            print('gen_monitor...')
            gen_monitor(components_info)
            print('done\n')
            
            print('gen_coverage...')
            gen_coverage(components_info)
            print('done\n')
        
        print('gen_grapth...')
        G, color_map, edge_labels = gen_grapth(components_info)
        print('done\n')
        







        input_node_index = []
        output_node_index = []
        for i in range(len(components_info)):
            if components_info[i]['Type'] == 'Input_Node':
                input_node_index.append(i)
            if components_info[i]['Type'] == 'Output_Node':
                output_node_index.append(i)

        stereo_component_dict = gen_stereo_componenet_dict()

        #print(G.nodes)

        # print('--------------------------------------')
        # print(nx.dfs_successors(G, source=180))
        # print('--------------------------------------')
        # print(nx.dfs_successors(G, source=22))
        # print('--------------------------------------')
        # print(nx.dfs_successors(G, source=110))
        # print(nx.has_path(G, 196, 0))
        # print(nx.has_path(G, 0, 196))
        # print(nx.has_path(G, 18, 0))
        # print(nx.has_path(G, 0, 18))
        # print(nx.shortest_path(G, 196, 0))
        # for item in nx.all_simple_paths(G, 0, 196):
        #     print(item)
        # print(list(nx.all_simple_paths(G, 0, 196)))
        #print(nx.dfs_successors(G, source=196))
        #exit()

        phase_node = []
        for i in range(len(components_info)):
            if components_info[i]['Type'] == 'Block' or components_info[i]['Type'] == 'SRC' or components_info[i]['Type'] == 'Input_Node':
                #print(components_info[i]['Type'])
                phase_node.append(i)
        print('------------------------------------------------------------')
        print('permutation node', phase_node)
        print('permutation node numbers : ' + str(len(phase_node)))
        per_list = permutations(phase_node, 2)
        
        pn2_has_edge = []
        for item in list(per_list):
            #print(item)
            if nx.has_path(G, item[0], item[1]) and item not in mix_permuation_pair:
                # if node0 -> node1 has path
                # mix_permutation_pair are impossible to construct to a path
                if only_direct_edge(G, item[1], item[0]):
                    # 如果 a->b has path 且 b->a是edge 且 a->b不是edge, 代表a或b一定不是Input_node, a->b 是一個中間段的path(Output->a->b->Input)
                    # 代表
                    continue
                if nx.has_path(G, item[1], item[0]):
                    if len(nx.shortest_path(G, item[1], item[0])) == 3:
                        node_0 = nx.shortest_path(G, item[1], item[0])[0]
                        node_1 = nx.shortest_path(G, item[1], item[0])[1]
                        node_2 = nx.shortest_path(G, item[1], item[0])[2]
                        if only_direct_edge(G, node_0, node_1) and only_direct_edge(G, node_1, node_2):
                            cou = 0
                            for item in nx.all_simple_paths(G, item[1], item[0]):
                                if cou >= 2:
                                    break
                                cou += 1
                            if cou == 1:
                                continue
                
                tmp = [item[0], item[1]]
                pn2_has_edge.append(tmp)
        print('permutation edges number : ' + str(len(phase_node) * len(phase_node)-1) + ', has_edge : ' + str(len(pn2_has_edge)))
        print('------------------------------------------------------------')
        #print(pn2_has_edge)

        ########################## find path ##########################

        if input('Read path from files?(y/n) ').lower() == 'y':
            with open('input/find_path.pickle', 'rb') as f:
                find_path = pickle.load(f)
            with open('input/not_found_path_node.pickle', 'rb') as f:
                not_found_path_node = pickle.load(f)
            with open('input/illegal_stereo_path_node.pickle', 'rb') as f:
                illegal_stereo_path_node = pickle.load(f)
        else:
            print('Start to gen path data...')
            find_path, not_found_path_node, illegal_stereo_path_node = gen_find_path(pn2_has_edge)
            print('Start to save data...')
            with open('input/find_path.pickle', 'wb') as f:
                pickle.dump(find_path, f)
            with open('input/not_found_path_node.pickle', 'wb') as f:
                pickle.dump(not_found_path_node, f)
            with open('input/illegal_stereo_path_node.pickle', 'wb') as f:
                pickle.dump(illegal_stereo_path_node, f)
            print('Finish !!')
        
        print('------------------------------------------------------------')
        print('successful path number :', len(find_path))
        print('fail path number :', len(not_found_path_node))
        # not_found_path_node = [[203,201]]        # test legal path
        print('fail path nodes :', not_found_path_node)
        print('illegal_stereo_path number :', len(illegal_stereo_path_node))
        print('illegal_stereo_path_node :', illegal_stereo_path_node)
        print('------------------------------------------------------------')
        
        #################### non Input_Node pair ####################
        '''

        for i in range(len(not_found_path_node)):
            find_path_flag = False
            print('{:>4d}->{:<4d}: '.format(not_found_path_node[i][0], not_found_path_node[i][1]))
            print('------------------------------------------------------------')
            arr_dict = dict()
            start_time = time.time()
            for output_node in output_node_index:
                a_b = []
                if nx.has_path(G, output_node, not_found_path_node[i][0]) and nx.has_path(G, not_found_path_node[i][0], not_found_path_node[i][1]):
                    # for node in nx.all_simple_paths(G, output_node, not_found_path_node[i][0]):
                    #     a.append(node)
                    # for node in nx.all_simple_paths(G, not_found_path_node[i][0], not_found_path_node[i][1]):
                    #     b.append(node)
                    a = list(nx.all_simple_paths(G, output_node, not_found_path_node[i][0]))
                    b = list(nx.all_simple_paths(G, not_found_path_node[i][0], not_found_path_node[i][1]))
                    for x in a:
                        for y in b:
                            tmp_mix = x + y[1:]
                            if len(set(tmp_mix)) == len(tmp_mix):
                                a_b.append(tmp_mix)
                arr_dict[output_node] = a_b
            for item in arr_dict:
                print(item, len(arr_dict[item]))

            print(str(time.time() - start_time) + ' sec')

            for output_node in output_node_index:
                print('Try Output Node :', output_node)
                for input_node in input_node_index:
                    if check_per_path(G, output_node, not_found_path_node[i][0], not_found_path_node[i][1], input_node):
                        if len(arr_dict[output_node]) == 0:
                            continue
                        start_time = time.time()
                        tmp_mix = []
                        c = list(nx.all_simple_paths(G, not_found_path_node[i][1], input_node))
                        # c = []
                        # for node in nx.all_simple_paths(G, not_found_path_node[i][1], input_node):
                        #     c.append(node)
                        
                        print(str(time.time() - start_time) + ' sec   ', input_node, len(c))
                        start_time = time.time()
                        cou = 0
                        for x in arr_dict[output_node]:
                            for y in c:
                                tmp_mix = x + y[1:]
                                if len(set(tmp_mix)) == len(tmp_mix):
                                    print('find !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                                    find_path_flag = True
                                    break
                            cou += 1
                            # if cou%100 == 0:
                            #     print(cou)
                            if find_path_flag == True:
                                break
                        print(str(time.time() - start_time) + ' sec')
                        if find_path_flag == False:
                            continue
                        print(tmp_mix)
                        find_path_flag, tmp_mix_stereo = find_stereo_path(G, components_info, input_node_index, stereo_component_dict, tmp_mix)
                        if find_path_flag == False:
                            continue
                        find_path.append([tmp_mix, tmp_mix_stereo])
                        find_path_len.append(len(tmp_mix))
                        find_path_flag = True
                        break
                if find_path_flag == True:
                    break
            #exit()
            if find_path_flag == False:
                print('illegal path : ', end='')
                print('{:>4d}->{:<4d}'.format(not_found_path_node[i][0], not_found_path_node[i][1]))

        '''

        #################### Input_Node pair ####################

        # ????????????



        ################### pick path(greedy) ###################

        if input('Read greedy choose path from files?(y/n) ').lower() == 'y':
            with open('input/greedy_choose_path.pickle', 'rb') as f:
                greedy_choose_path = pickle.load(f)
            with open('input/uncover_pairs.pickle', 'rb') as f:
                uncover_pairs = pickle.load(f)
        else:
            print('Start to gen greedy path data...')
            greedy_choose_path, uncover_pairs = greedy_pick_path(find_path, pn2_has_edge)
            print('Start to save data...')
            with open('input/greedy_choose_path.pickle', 'wb') as f:
                pickle.dump(greedy_choose_path, f)
            with open('input/uncover_pairs.pickle', 'wb') as f:
                pickle.dump(uncover_pairs, f)
            print('Finish !!')
        
        #print(greedy_choose_path)
        print('------------------------------------------------------------')
        print('pattern num :', len(greedy_choose_path))
        print('--------------------- uncovered pairs ----------------------')
        print(uncover_pairs)
        print(len(uncover_pairs))

        
        exit()
        

        if not FOR_SD_CHECK_ONLY:
            SKIP_PROCESS_PATH = False
            control = input('skip process path?\n   (y)es: read path from previous result(need input/all_path.txt and input/chosen_path_idx_list.txt)\n   (n)o : process again\n     ? ')
            if control == 'y':
                SKIP_PROCESS_PATH = True
        else:
            SKIP_PROCESS_PATH = False
        
        if not SKIP_PROCESS_PATH:
            print('process_path...')
            process_path()
            print('done\n')
            
        control = input('Merge all_path[*] to all_path?\n')
        if control == 'y':
            merge_all_path()
            
        chosen_path_idx_list = read_chosen_path_idx_list()
        all_path = read_all_path()
        
        if FOR_SD_CHECK_ONLY:
            input('Press enter to continue...')
        
        if not FOR_SD_CHECK_ONLY:
            control = input('Visualization?')
            if control == 'y':
                #control = input("Show grapth? Press Y(yes) or N(no): ")
                #if control.lower() == 'y':
                
                #pos = nx.random_layout(G, seed=13)
                #nx.draw_networkx(G, pos, node_color=color_map, with_labels = True)
                #plt.savefig('path.png')
                #plt.show()
                
                fig = plt.figure(figsize=(19.2, 10.8))
                #pos = nx.spectral_layout(G, scale = 2)
                pos = nx.spring_layout(G, k = 5/math.sqrt(G.order()))
                nx.draw(G, pos=pos,  node_color=color_map, with_labels=True) 
                nx.draw_networkx_edge_labels(G, pos=pos, edge_labels = edge_labels, alpha=0.7, bbox=dict(alpha=0), font_size=10, font_color='blue')
                plt.savefig('path.png', dpi=600)
                
                nx.write_graphml(G, "all.graphml")
                
                #cy = CyRestClient()
                #cy.session.delete()
                #n = cy.network.create_from_networkx(G)
                #cy.layout.apply(name='circular', network=n)
                #Image(n.get_png(height=400))

                #plt.show()
            with open('networkdata1.json', 'w') as outfile1:
                outfile1.write(json.dumps(json_graph.node_link_data(G)))
                    
            
            control = input('auto_add_chosen_path_greedy, y(es) or n(o)?')
            if control.lower() == 'y':
                print('auto_add_chosen_path_greedy...')
                print('get_coverd_map...')
                edge_covered_map = get_coverd_map(G, all_path, chosen_path_idx_list)
                print('done\n')
                chosen_path_idx_list = auto_add_chosen_path_greedy(G, all_path, chosen_path_idx_list, edge_covered_map)
                print('done\n')
                
            #else:
            #    print('auto_add_chosen_path...')
            #    chosen_path_idx_list = auto_add_chosen_path(G, all_path, chosen_path_idx_list, edge_covered_map)
            #    print('done\n')
            #    chosen_path_idx_list = reduce_chosen_path_idx_list(chosen_path_idx_list, all_path)
                
                print(chosen_path_idx_list)
                
                print('write_chosen_path_idx_list...')
                write_chosen_path_idx_list(chosen_path_idx_list)
                print('done\n')
            
            control = input('auto_add_chosen_path_search, y(es) or n(o)?')
            if control.lower() == 'y':
                print('try to cover all edges...')
                chosen_path_idx_list = auto_add_chosen_path_search(G, all_path, chosen_path_idx_list, edge_covered_map)
                print('done')
                
                print(chosen_path_idx_list)
            
                print('write_chosen_path_idx_list...')
                write_chosen_path_idx_list(chosen_path_idx_list)
                print('done\n')

            #control = input("Overwrite all_path.xlsx? Press Y(yes) or N(no): ")
            #if control.lower() == 'y':
            #    print('write_path_to_excel...')
            #    write_path_to_excel(all_path, chosen_path_idx_list, components_info)
            #    print('done\n')
            
            #user_choose_path_list = check_path_equal(all_path, chosen_path_idx_list, read_path_idx_list)
            #if user_choose_path_list:
            #    print('user_choose_path_list:')
            #    for user_choose_path in user_choose_path_list:
            #        print(user_choose_path)
            #    print('')
            
            #control = input("Please edit the all_path.xlsx then press C(continue) or press E(exit): ")
            #if control.lower() == 'c':
            #    read_path_idx_list = read_path_from_excel()
            #    
            #    print('')
            #    
            #    if read_path_idx_list:
            #        path_string = ''
            #        for read_path_idx in read_path_idx_list:
            #            path_string += '{} '.format(read_path_idx)
            #            
            #        print('Chosen paths: {}'.format(path_string))
            #        write_chosen_path_idx_list(read_path_idx_list)
            #    else:
            #        print('No paths chosen')
            
            chosen_path_idx_list = read_chosen_path_idx_list()
            edge_covered_map = get_coverd_map(G, all_path, chosen_path_idx_list)
            unvocered_edges = get_unvocered_edge(edge_covered_map)
            if unvocered_edges:
                print('uncovered edges:')
                for unvocered_edge in unvocered_edges:
                    print(unvocered_edge)
                print('')
                
            print('')
            

                    
            if all_register_info:
                control = input("Auto gen reg_info.xlsx? Press Y(yes) or N(no): ")
                if control.lower() == 'y':
                    print('gen_register_info...')
                    gen_register_info(components_info, all_register_info, True)
                    print('done')
                else:
                    control = input("Create blank reg_info.xlsx? Press Y(yes) or N(no): ")
                    if control.lower() == 'y':
                        print('gen_register_info...')
                        gen_register_info(components_info, {}, False)
                        print('done')

            control = input("Create blank in_info.xlsx and out_info.xlsx? Press Y(yes) or N(no): ")
            if control.lower() == 'y':
                print('gen_inout_info...')
                gen_in_and_out_info(components_info)
                #gen_inout_info(components_info)
                print('done')

            control = input("Please edit the reg_info.xlsx and in_info.xlsx out_info.xlsx then press C(continue) to gen patterns or press E(exit): ")
            if control.lower() == 'c':
                print('pattern_auto_gen...')
                read_path_idx_list = read_chosen_path_idx_list()
                pattern_auto_gen(read_path_idx_list, components_info, all_path)
                print('done')
                
            control = input('gen coveragereport, y(es) or n(o)?')
            if control.lower() == 'y':
                print('gen_coverage_report')
                gen_coverage_report(components_parsing_rule, edge_covered_map, all_path, chosen_path_idx_list, components_info, all_register_info)
                print('done')
                

    else:
        FAIL_MESSAGE('check failed, please check visio file')
        input('')
    ################################################################## main ##################################################################