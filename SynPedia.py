"""
Copyright 2017 The Research Foundation for the State University of New York

This SynPedia(TM) program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (included below the code).  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import sys
import urllib

EXTRACT = re.compile(r'<td><a href="[^"]*/wiki/([^"]+)"')

import marshal

def extract(line,tag):
    value = ""
    begin = line.find(tag) + len(tag) + 1
    end = line.find('</' + tag)
    if end > begin:
        value = line[begin:end]
        
    return value
     
def extract_link(line,tag):
    value = ""
    begin = line.find('[[' + tag) + len(tag) + 2
    end = line.find(']]',begin)
    if end > begin:
        value = line[begin:end]
        
    return value
     
def extract_redirect(line):
    value = ""
    redirect_tag = '<redirect title="'
    begin = line.find(redirect_tag) + len(redirect_tag)
    end = line.find('" />',begin)
    if end > begin:
        value = line[begin:end]
        
    return value
    
def filter_categories():
    input = open("misc_page_info.txt")
    #input = open("page_info.txt")
    
    for line in input:
                        
        line_parts = line.split(',')
        if len(line_parts) == 4:
            categories_out = line_parts[3]
            if categories_out:
                categories = categories_out.split('#')
                if categories:
                    open("misc_cat_page_info.txt","a").write(line.strip('\n') + '\n')
            
            '''
            person = False
            for category in categories:
                #print("category:",category)
                if category.strip().lower().find("births") != -1:
                    open("people_page_info.txt","a").write(line.strip('\n') + '\n')
                    person = True
                    break                    
            if not(person):                    
                open("misc_page_info.txt","a").write(line.strip('\n') + '\n')
            '''  
                
def load_categories_dict(): 
    '''
    AccessibleComputing,Computer accessibility,7181920,
    Anarchism,,3020778,Anarchism| #Political culture#Political ideologies#Social theories#Anti-fascism#Anti-capitalism#Far-left politics
    AfghanistanHistory,History of Afghanistan,750223,
    AfghanistanGeography,Geography of Afghanistan,194203,
    AfghanistanPeople,Demography of Afghanistan,279219,
    AfghanistanCommunications,Communications in Afghanistan,750223,
    AfghanistanTransportations,Transport in Afghanistan,930338,
    AfghanistanMilitary,Afghan Armed Forces,11292982,
    AfghanistanTransnationalIssues,Foreign relations of Afghanistan,241822,
    AssistiveTechnology,Assistive technology,750223,
    AmoeboidTaxa,Amoeboid,750223,
    Autism,,19292718,Autism| #Communication disorders#Mental and behavioural disorders#Neurological disorders#Neurological disorders in children#Pervasive developmental disorders#Psychiatric diagnosis
    AlbaniaHistory,History of Albania,750223,
    AlbaniaPeople,Demographics of Albania,750223,
    AsWeMayThink,As We May Think,750223,
    AlbaniaGovernment,Politics of Albania,750223,
    
    '''
    input = open("misc_page_info.txt")
    categories_dict = {}
    for line in input:
        
        line_parts = line.split(',')
        #outstring = page_title + "," + redirect_title + "," + id + "," + categories_out
        if len(line_parts) == 4:
            page_title = line_parts[0]
            redirect_title = line_parts[1]
            id = line_parts[2]
            categories_out = line_parts[3].strip()
            key = ""
            if redirect_title:
                key = redirect_title
            else:
                key = page_title
            if categories_out and key:
                if categories_dict.has_key(key):
                    value = categories_dict[key]
                    if value != categories_out:
                        '''
                        open("check_info.txt","a").write("---------------" + '\n')
                        open("check_info.txt","a").write("key:" + key + '\n')
                        open("check_info.txt","a").write("cats:" + categories_out + '\n')
                        open("check_info.txt","a").write("line:" + line + '\n')
                        open("check_info.txt","a").write("val:" + value + '\n')
                        open("check_info.txt","a").write("merged:" + value + "#" + categories_out + '\n')
                        '''
                        categories_dict[key] = value + "#" + categories_out 
                else:
                    categories_dict[key] = categories_out
                    
    return categories_dict
    
def load_snomed_matches_dict():
    '''
    snomed_wiki_matches_short.txt
    120843002,Influenzavirus B antibody,Influenza B antibody,substance
    120843002,Influenzavirus B antibody,Influenzavirus B antibody,substance
    188511002,Burkitt's lymphoma of intrathoracic lymph nodes,Burkitt lymphoma of intrathoracic lymph nodes,disorder
    188511002,Burkitt's lymphoma of intrathoracic lymph nodes,Burkitt's lymphoma of intrathoracic lymph nodes,disorder
    372316007,Morganella species,Morganella species,organism
    96065002,Temocillin,Temocillin,product
    96065002,Temocillin,Temocillin product,product
    '''
    input = open("snomed_wiki_match_short.txt")
    snomed_matches_dict = {}
    # the term is what matches the wikipedia page
    #outstring = concept + "," + full_term + "," + term + "," + semantic_type
    for line in input:
        
        line_parts = line.split(',')
        
        if len(line_parts) == 4:
            concept = line_parts[0]
            full_term = line_parts[1]
            term = line_parts[2]
            semantic_type = line_parts[3]
            values_string = concept + "," + full_term + "," + semantic_type
            if snomed_matches_dict.has_key(term):
                snomed_matches_dict[term].append(values_string)
            else:
                snomed_matches_dict[term] = [values_string]
                    
    return snomed_matches_dict
    
def merge_dicts(snomed_matches_dict, categories_dict):
    merged_dict = {}
    for key in snomed_matches_dict:
        snomed_values = snomed_matches_dict[key]        
        if categories_dict.has_key(key):
            categories = categories_dict[key] 
            for snomed_value in snomed_values:
                snomed_parts = snomed_value.split(',')
                #values_string = concept + "," + full_term + "," + semantic_type
                if len(snomed_parts) == 3:
                    concept = snomed_parts[0]
                    full_term = snomed_parts[1]
                    semantic_type = snomed_parts[2]
                    outstring = key + "," + full_term + "," + semantic_type + "," + categories
                    if merged_dict.has_key(concept):
                        merged_dict[concept].append(outstring)
                    else:
                        merged_dict[concept] = [outstring]
                else:
                    print("bad snomed:",str(snomed_parts))
                    
    return merged_dict            
  
def main():
    count = 0
    input = open("enwiki-20140614-pages-articles.xml")
    #input = open("enwiki-latest-category.sql")
    
    in_page = False
    page_title = ""
    redirect_title = ""
    id = ""
    sections = []
    categories = []
    for line in input:
        if line.find("<page>") != -1:
            in_page = True
            
        if line.find("</page>") != -1:
            in_page = False
            if page_title:
                categories_out = ""
                if categories:
                    categories_out = "#".join([cat for cat in categories])
                    
                #print("title:",page_title," redirect title:",redirect_title," id:",id," categories:",categories_out)
                outstring = page_title + "," + redirect_title + "," + id + "," + categories_out
                open("page_info.txt","a").write(outstring + '\n')
                
                page_title = ""
                redirect_title = ""
                id = ""
                sections = []
                categories = []
            
            
        if line.find("<title>") != -1 and in_page:
            page_title = extract(line,'title')
            
        if line.find("<redirect title") != -1 and in_page:
            redirect_title = extract_redirect(line)
            
        if line.find("<id>") != -1 and in_page:
            id = extract(line,'id')
            
        if line.find("[[Category:") != -1 and in_page:
            category = extract_link(line,'Category:')
            if category:
                categories.append(category)
    
        count = count + 1
        '''
        if count > 10000:
            break
        '''
        
        #match = EXTRACT.match(line)
        #print(line)
        '''
        if match:
            # Convert escape sequences
            title = urllib.unquote(match.group(1))
            # Convert _ to " "
            print title.replace("_", " ")
        '''  
        
if __name__ == "__main__":
    #profile.run('main()')
    #filter_categories()
    #main()
    categories_dict = load_categories_dict()
    snomed_matches_dict = load_snomed_matches_dict()
    merged_dict = merge_dicts(snomed_matches_dict, categories_dict)
    marshal.dump(merged_dict, open("snomed_wiki_matches_full.marshal", 'wb'))
