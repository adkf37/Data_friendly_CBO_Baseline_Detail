# CBO Cost Estimate Lab - Project Overview

Date: 2026-05-08
Status: Initial concept and backlog

## Purpose

CBO publishes a bunch of detail about its baseline budget projections for selected prorgrams. These publications are individual Excel and pdf files for 30 programs. 

These files are designed for humans to read, not for bulk data analysis.This data is quite useful, but would be more useful if it were in a tidier data format. 

## Resources

CBO url: https://www.cbo.gov/data/baseline-projections-selected-programs


## Steps and Scope of Data_friendly_CBO_Baseline_Detail

- Download all the Excel files for every program. Ignore the pdfs
- Figure out how to transform each file from a formatted Excel file, into a longer csv that are meant for machines to read. 
- Ok to combine or break about files in multiple csvs if it makes sense to. For example, breaking apart enrollment and spending information into separate files might make sense. Or combining the enrollment projections for all the health programs in one file may make sense. Having different Excel sheets be different csvs probably generally makes sense.
- Preference for long data
- Write detailed data schemas for each dataset we crease.
- Figuring out how to verify that the transforms match the source Excel files.
- No human oversight until project is completed. Just keep trying.
