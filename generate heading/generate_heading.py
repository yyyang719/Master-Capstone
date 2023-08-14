#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: yuanyuan
"""
import pandas as pd

file_publicschools = "public_schools.xlsx"
public_schools = pd.read_excel(file_publicschools, sheet_name="public_schools", header = 0, dtype={"Org Code":str,"Zip":str})
public_schools = public_schools[['Org Name', 'Org Code', 'Org Type', 'Town', 'State', 'Zip', 'Grade']]
public_schools = public_schools.drop_duplicates(ignore_index=True)
public_schools = public_schools.rename(columns={"Org Name": "School Name", "Org Code": "School Code", "Org Type": "School Type"})
public_schools['District Name'] = public_schools['School Name'].map(lambda x: x.split(':')[0] if len(x.split(':'))==2 else x.split(':')[0]+":"+x.split(':')[1])

file_schooldistricts = "public_charter_districts.xlsx"
school_district_MA = pd.read_excel(file_schooldistricts, sheet_name="Sheet1", header = 0, dtype={"Org Code":str,"Zip":str})
school_district_MA = school_district_MA[['Org Name', 'Org Code', 'Org Type']]
school_district_MA = school_district_MA.rename(columns={"Org Name": "District Name", "Org Code": "District Code", "Org Type": "District Type"})

public_schools = public_schools.drop_duplicates(ignore_index=True)
school_district_MA = school_district_MA.drop_duplicates(ignore_index=True)

heading = pd.merge(public_schools, school_district_MA, how ="left", on ="District Name")


filename = "headidng_columns.csv"
heading.to_csv(filename, index=False)