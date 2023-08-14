#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: yuanyuan
"""



from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import time
import random
# import validators



def load_school_lists():
    """
    - load school name/code from files
        * public school district
        * charter school
        * private school
    - files are downloaded from https://profiles.doe.mass.edu/search/search.aspx?leftNavId=11238

    Returns
    -------
    school_df : pd.dataframe 
        contains : 
            school name 
            org code 
            org type
            town
            zip
            grade
            
    """
    cur_path = os.path.curdir
    folder = "school_lists"

    col_needed = ["Org Name", "Org Code", "Org Type", "Town", "Zip", "Grade"]    

    # load public and charter school districts
    file_public_charter = "public_charter_districts.xlsx"
    public_charter = pd.read_excel(os.path.join(cur_path,
                                                folder,
                                                file_public_charter),
                                   sheet_name="Sheet1",
                                   dtype={"Org Code":str,
                                          "Zip":str})
    # keep columns needed
    public_charter = public_charter[col_needed]
    
    # # load private school
    # file_private = "private_schools.xlsx"
    # private_schools = pd.read_excel(os.path.join(cur_path,
    #                                              folder,
    #                                              file_private),
    #                                 sheet_name="Sheet1",
    #                                 dtype={"Org Code":str,
    #                                        "Zip":str})
    # private_schools.rename(columns={"Unnamed: 12":"Grade"},
    #                        inplace=True)
    # private_schools = private_schools[col_needed]
    
    # school_df = pd.concat([public_charter, private_schools],
    #                         axis=0,
    #                         ignore_index=True)
    school_df = public_charter # only includes public and charter districts
    return school_df



def read_sat(school_df):
    """
    read sat performance

    Parameters
    ----------
    school_list : pd.dataframe
        school district name, org code, org type, town, zip, grade.

    Returns
    -------
    None    
    sat for each school has been saved into corresponding files (with school name)

    """
    url_base = "https://profiles.doe.mass.edu/sat/sat_perf_dist.aspx?orgtypecode=5"
    years = range(2005, 2023) # data from 2005 to 2022
    
    # there are two versions of columns
    columns_4 = ['Student Group', 'Test Takers', 'Reading / Writing', 'Math']
    columns_5 = ['Student Group', 'Test Takers', 'Reading', 'Writing', 'Math']
    
    
    # for each school district
    for index, row in school_df.iterrows():
        org_name = row["Org Name"]
        org_code = row["Org Code"]
        org_type = row["Org Type"]
        town = row["Town"]
        
        sat_columns = ["Org Name", "Org Code", "Org Type", "Town", "Year", 
                       "SAT_Student_Group", "SAT_Test_Taker", "SAT_Reading", "SAT_Writing", "SAT_Math"]
        sat = pd.DataFrame(columns=sat_columns)

        # random wait few seconds to avoid anti-scraping
        rand_num = random.randint(2,10)
        print("Wait {} seconds...".format(rand_num))
        time.sleep(rand_num)
        
        # for each year
        for year in years:
            print("Feteching SAT: {}, {}, {}, {}.".format(org_name, org_code, org_type, year))

            # roate user-agent header
            user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
                           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
                           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
                           'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
                           'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36'] 
            user_agent = random.choice(user_agents)
            headers = {'User-Agent': user_agent} 

            url_full = url_base + "&orgcode=" + org_code + "&&fycode=" + str(year)
            page = requests.get(url_full, "html", headers=headers)
            
            # status code 200 means success, other codes mean fail
            if page.status_code != 200:
                page.raise_for_status()
            
            # load page into soup
            soup = BeautifulSoup(page.text, features="html.parser")
            # find table with sat performance
            table = soup.find_all("table", id="ctl00_ContentPlaceHolder1_teacherDataGridView")[0]
            data_list = []
            # if table has data
            if len(table) > 0:
                # 1st step, determine column counts
                # (each year table may contain different number of columns)
                th = table.find_all("th")
                headers = []
                for col in th:
                    headers.append(col.text)
                # check which version of columns for current table
                if headers == columns_4:
                    column_counts = 4
                elif headers == columns_5:
                    column_counts = 5
                else:
                    # if error, set columns to 5
                    column_counts = 5
                    # print("Warning: mismatch columns, org code {}, year {}".format(org_code, year))
                
                # find table data
                table_data = table.find_all("td")
                
                # each record contains 4 or 5 columns
                # if 4 columns, we duplicate "writting" using "reading" score
                # if 5 columns, don't do any edits
                if len(table_data) % column_counts == 0:
                    for i in range(int(len(table_data) / column_counts)):
                        student_group = table_data[(i * column_counts + 0)].text
                        test_taker = table_data[(i * column_counts + 1)].text
                        reading = table_data[(i * column_counts + 2)].text
                        if column_counts == 4:
                            writing = reading
                            math = table_data[(i * column_counts + 3)].text
                        else:
                            writing = table_data[(i * column_counts + 3)].text
                            math = table_data[(i * column_counts + 4)].text
                        
                        data_list.append([org_name, org_code, org_type, town, year, 
                                          student_group, test_taker, reading, writing, math])
                else:
                    # if table has NO data
                    # make dummy row to keep information
                    data_list = [[org_name, org_code, org_type, town, year, 
                                 "nan", "nan", "nan", "nan", "nan"]]    

            # if table has NO data
            # make dummy row to keep information
            else:
                data_list = [[org_name, org_code, org_type, town, year, 
                             "nan", "nan", "nan", "nan", "nan"]]    
            
            temp = pd.DataFrame(data=data_list, columns=sat_columns)
            sat = pd.concat([sat, temp], ignore_index=True)
        
        # save to file, each file contains one school, for all years
        file_name = "./sat/{}.csv".format(org_name)
        sat.to_csv(file_name, index=False)            
        
    return sat
        
    
    
def read_AP_performance(school_df):
    """
    read advanced placement (AP) performance

    Parameters
    ----------
    school_list : pd.dataframe
        school district name, org code, org type, town, zip, grade.

    Returns
    -------
    AP performance for each district, by years.

    """
    url_base = "https://profiles.doe.mass.edu/adv_placement/ap_perf_dist.aspx?orgtypecode=5"
    years = range(2007, 2023) # data from 2007 to 2022

    column_counts = 4
    
    # for each school district
    for index, row in school_df.iterrows():
        org_name = row["Org Name"]
        org_code = row["Org Code"]
        org_type = row["Org Type"]
        town = row["Town"]
    
        AP_columns = ["Org Name", "Org Code", "Org Type", "Town", "Year", 
                       "AP_Student_Group", "AP_Subject", "AP_Tests_Taken", "AP_Score1_2", "AP_Score3_5"]
        AP = pd.DataFrame(columns=AP_columns)

        rand_num = random.randint(2,10)
        print("Wait {} seconds...".format(rand_num))
        time.sleep(rand_num)
        
        # for each year
        for year in years:
            print("Feteching AP: {}, {}, {}, {}.".format(org_name, org_code, org_type, year))

            # roate user-agent header
            user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
                           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
                           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
                           'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
                           'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36'] 
            user_agent = random.choice(user_agents)
            headers = {'User-Agent': user_agent} 

            url_full = url_base + "&orgcode=" + org_code + "&&fycode=" + str(year)
            
            page = requests.get(url_full, "html", headers=headers)
            
            # status code 200 means success, other codes mean fail
            if page.status_code != 200:
                page.raise_for_status()
            
            # load page into soup
            soup = BeautifulSoup(page.text, features="html.parser")
            
            # find student group
            student_groups = soup.find_all("td", title="Student Group Result")[0]
            if len(student_groups) > 0:
                student_group = student_groups.find_all("option", selected="selected")[0].text
            else:
                student_group = "nan"
            
            # find table with AP performance
            table = soup.find_all("table", id="ctl00_ContentPlaceHolder1_teacherDataGridView")[0]
            data_list = []
            # if table has data
            if len(table) > 0:
                # find table data, return list
                table = table.find_all("td")
                # each record contains 4 columns, make sure we get correct rows
                if len(table) % column_counts == 0:
                    for i in range(int(len(table) / column_counts)):
                        AP_subject = table[(i * column_counts)].text
                        AP_tests_taken = table[(i * column_counts + 1)].text
                        AP_Score1_2 = table[(i * column_counts + 2)].text
                        AP_Score3_5 = table[(i * column_counts + 3)].text
                        data_list.append([org_name, org_code, org_type, town, year, 
                                          student_group, AP_subject, AP_tests_taken, AP_Score1_2, AP_Score3_5])
                else:
                    # if table has NO data
                    # make dummy row to keep information
                    data_list = [[org_name, org_code, org_type, town, year, 
                                  student_group, "nan", "nan", "nan", "nan"]]   
                            
            # if table has NO data
            # make dummy row to keep information
            else:
                data_list = [[org_name, org_code, org_type, town, year, 
                              student_group, "nan", "nan", "nan", "nan"]]
            
            temp = pd.DataFrame(data=data_list, columns=AP_columns)
            AP = pd.concat([AP, temp], ignore_index=True)
        
        # save to file, one school, all years
        file_name = "./AP/{}.csv".format(org_name)
        AP.to_csv(file_name, index=False)            
        
    return AP    
    
    
    
def main():
    """
    main function

    Returns
    -------
    None.

    """
    # load school list: public district, charter district, private school
    school_df = load_school_lists()
    
    # scraping sat performance
    # sat = read_sat(school_df.iloc[1:10,:])
    sat = read_sat(school_df)
    
    # # scraping AP performance
    # AP = read_AP_performance(school_df.iloc[:10,:])
    
    print("Break Here")
    
    
    
    
    
    
if __name__ == "__main__":
    main()