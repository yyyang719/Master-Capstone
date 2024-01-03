#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: yuanyuan
"""
import pandas as pd

# read heading
file_heading = "heading_columns.csv"
heading = pd.read_csv(file_heading, dtype={"School Code":str,"Zip":str, "District Code":str})

# enrollemnt with school and grade level
file_enroll = "enrollmentbygrade.xlsx"
enrollment = pd.read_excel(file_enroll, sheet_name="Enrollment By Grade Report", header = 1, dtype={"School Code":str})
enrollment = enrollment.drop_duplicates(ignore_index = True)
enrollment.drop('School Name', axis=1, inplace=True)

data_2018 = pd.merge(heading, enrollment, how='left', on='School Code')

# population groups report with school level
file_pgroup = "selectedpopulations.xlsx"
pgroup = pd.read_excel(file_pgroup, sheet_name="Selected Populations Report", header = 1, dtype={"School Code":str})
# need drop 6 more empty columns
pgroup.drop(['School Name','Free Lunch #', 'Free Lunch %', 'Reduced Lunch #','Reduced Lunch %'], axis=1, inplace=True)

data_2018 = pd.merge(data_2018, pgroup, how='left', on='School Code')

# enrollment by Race/Gender report with school level
file_racegender = "enrollmentbyracegender.xlsx"
racegender = pd.read_excel(file_racegender, sheet_name="Enrollment By Race Gender Repor", header = 1, dtype={"School Code":str})
racegender.drop('School Name', axis=1, inplace=True)
data_2018 = pd.merge(data_2018, racegender, how='left', on='School Code')

# class with school level
file_class = "ClassSizebyGenPopulation.xlsx"
classsize = pd.read_excel(file_class, sheet_name="Class Size by Gender and Select", header = 1, dtype={"School Code":str})
# classsize.drop('School Name', axis=1, inplace=True)
classsize =classsize[['School Code', 'Total # of Classes', 'Average Class Size','Number of Students']]
data_2018 = pd.merge(data_2018, classsize, how='left', on='School Code')


# teacher data: student/teacher ratio with school level, percent of experienced teachers
file_teacherdata = "teacherdata.xlsx"
teacherdata = pd.read_excel(file_teacherdata, sheet_name="Teacher Data", header = 1, dtype={"School Code":str})
teacherdata.drop('School Name', axis=1, inplace=True)

# process student/teacher ratio data
teacherdata['Student / Teacher Ratio'] = teacherdata['Student / Teacher Ratio'].apply(lambda x: float(str(x).split("to")[0]) if "#" not in str(x) else x)

data_2018 = pd.merge(data_2018, teacherdata, how='left', on='School Code')

# averge salary with district level
file_teachersalary = "TeacherSalaries.xlsx"
teachersalary = pd.read_excel(file_teachersalary, sheet_name="Teacher Salaries", header = 1, dtype={"District Code":str})
teachersalary.drop('District Name', axis =1, inplace=True)
data_2018 = pd.merge(data_2018, teachersalary, how='left', on='District Code')

# educator evaluation performance with school level: percent of proficient, examplary, needs improvement, unsatisfactory
file_teachereval = "EducatorEvalPerf.xlsx"
teachereval = pd.read_excel(file_teachereval, sheet_name="Educator Evaluation Performance", header = 1, dtype={"Org Code":str})
teachereval.drop('School Name', axis =1, inplace=True)
teachereval.rename(columns = {'Org Code': 'School Code'}, inplace=True)

data_2018 = pd.merge(data_2018, teachereval, how='left', on='School Code')

# Expenditures with district level
file_expendi = "PerPupilExpenditures.xlsx"
expenditure = pd.read_excel(file_expendi, sheet_name="Per Pupil Expenditures", header = 1, dtype={"District Code":str})
expenditure.drop('District Name', axis =1, inplace=True)
data_2018 = pd.merge(data_2018, expenditure, how='left', on='District Code')

# grad rates with school level
file_gradrate = "gradrates.xlsx"
gradrate = pd.read_excel(file_gradrate, sheet_name= "Graduation Rate", header =1, dtype={"School Code":str})
gradrate.drop("School Name", axis=1, inplace=True)
data_2018 = pd.merge(data_2018, gradrate, how='left', on='School Code')

# drop out with school level
file_dropout = "dropout.xlsx"
dropout = pd.read_excel(file_dropout, sheet_name="Dropout Report", header=1, usecols = "B:E", dtype={"School Code":str})
data_2018 = pd.merge(data_2018, dropout, how='left', on='School Code')

# attendcollege with school level
file_attendcollege = "Gradsattendingcollege.xlsx"
attend = pd.read_excel(file_attendcollege, sheet_name= "Graduates Attending Institution", header =1, dtype={"School Code":str,})
attend.drop("School Name", axis=1, inplace=True)
# add column for 4 year college that includes private and public
attend['4Ycollege%'] = attend['Private Four-Year (%)'] +attend['Public Four-Year (%)']

data_2018 = pd.merge(data_2018, attend, how='left', on='School Code')

# masscore with school level
file_masscore = "masscore.xlsx"
masscore = pd.read_excel(file_masscore, sheet_name="MassCore Completion Report", header=1, usecols = "B:E", dtype={"School Code":str})
data_2018 = pd.merge(data_2018, masscore, how='left', on='School Code')

# advanced placement participaiton with school level
file_appartici = "ap_participation.xlsx"
appartici = pd.read_excel(file_appartici, sheet_name= "Advanced Placement Participatio", header =1, dtype={"School Code":str,})
appartici.drop("School Name", axis=1, inplace=True)
columns = appartici.columns.values
appartici_columns = ["AP " + name for name in columns[1:]]
appartici.columns = ["School Code"] + appartici_columns

data_2018 = pd.merge(data_2018, appartici, how='left', on='School Code')

# advanced placement performance with school level
file_apperfor = "ap_performance.xlsx"
apperfor = pd.read_excel(file_apperfor, sheet_name= "Advanced Placement Performance ", header =1, dtype={"School Code":str,})
apperfor.drop("School Name", axis=1, inplace=True)
apperfor.drop("Tests Taken", axis=1, inplace=True)
columns = apperfor.columns.values
apperfor_columns = ["AP " + name for name in columns[1:]]
apperfor.columns = ["School Code"] + apperfor_columns

data_2018 = pd.merge(data_2018, apperfor, how='left', on='School Code')

# sat performance with school level
file_sat = "sat_performance.xlsx"
sat = pd.read_excel(file_sat, sheet_name= "SAT Performance Report", header =1, dtype={"School Code":str,})
sat.drop("School Name", axis=1, inplace=True)
sat.drop("Writing", axis=1, inplace=True)
columns = sat.columns.values
sat_columns = ["SAT " + name for name in columns[1:]]
sat.columns = ["School Code"] + sat_columns
data_2018 = pd.merge(data_2018, sat, how='left', on='School Code')

# Advanced Course Completion with school level
file_ac = "AdvancedCourseCompletion.xlsx"
ac = pd.read_excel(file_ac, sheet_name= "Advanced Course Completion Repo", header =1, dtype={"School Code":str,})
ac = ac[['School Code', '# Grade 11 and 12 Students','# Students Completing Advanced', '% Students Completing Advanced']]
data_2018 = pd.merge(data_2018, ac, how='left', on='School Code')

# MCAS performance with school level
file_MCAS = "NextGenMCAS.xlsx"
MCAS = pd.read_excel(file_MCAS, sheet_name= "Next Generation MCAS Achievemen", header =1, dtype={"School Code":str,})
MCAS.drop("School Name", axis=1, inplace=True)

MCAS_ELA = MCAS[MCAS.Subject=='ELA']
MCAS_MATH = MCAS[MCAS.Subject=='MATH']

columns = MCAS.columns.values
columns_ELA = [name + " ELA" for name in columns[1:]]
columns_MATH = [name + " MATH" for name in columns[1:]]

MCAS_ELA.columns = ["School Code"] + columns_ELA
MCAS_MATH.columns = ["School Code"] + columns_MATH
MCAS_ELA = MCAS_ELA.drop("Subject ELA", axis=1)
MCAS_MATH = MCAS_MATH.drop("Subject MATH", axis=1)

data_2018 = pd.merge(data_2018, MCAS_ELA, how='left', on='School Code')
data_2018 = pd.merge(data_2018, MCAS_MATH, how='left', on='School Code')

# accountability at school level
file_account = "Accountability.xlsx"
account = pd.read_excel(file_account, sheet_name= "Accountability Report", header =1, dtype={"School Code":str,})
account.drop("School Name", axis=1, inplace=True)
data_2018 = pd.merge(data_2018, account, how='left', on='School Code')

# save to csv
file_name = "data_2018.csv"
data_2018.to_csv(file_name, index = False)
