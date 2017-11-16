./build_tree.py -s \
    -company Companies.csv \
    -custom-org-defaults Gold\ Supervisory_Organization_Assignment_Restrictions_and_Defaults_Custom\ Orgs*.csv \
    -cost-center Cost_Centers.csv \
    -custom-organization Custom_Organizations.csv  \
    -region Regions.csv \
    -propagate-custom-orgs \
    -iload supervisory_oganization_assignment_restrictions_and_defaults_GENERATED_GOLD.csv \
    dbo*COMBINED*201711160930*.csv \
    > t.html
exit
./build_tree.py -s \
    -company Companies.csv \
    -custom-org-defaults Gold\ Supervisory_Organization_Assignment_Restrictions_and_Defaults_Custom\ Orgs*.csv \
    -cost-center Cost_Centers.csv \
    -custom-organization Custom_Organizations.csv  \
    -region Regions.csv \
    -propagate-custom-orgs \
    -roles i2.s-Role-Based_Security_Group_Assignments_genmills3.csv \
    -pre-hire h.aa1-Create_Pre-Hires_genmills3.csv \
    -pre-hire h.aa1-Create_Pre-Hires_genmills3_NonSAP.csv \
    -job-change h.za-Job_Change_genmills3.csv \
    -job-change h.za-Job_Change_genmills3_NonSAP.csv \
    -role-validation-report Role_Validation_Report.csv \
    dbo*COMBINED*Gold.csv \
    > t.html
