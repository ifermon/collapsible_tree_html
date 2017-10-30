./build_tree.py -s \
    -company Companies.csv \
    -custom-org-defaults P3\ Supervisory_Organization_Assignment_Restrictions_and_Defaults_Custom\ Orgs\(Final\ 7.20.17\).csv \
    -cost-center Cost_Centers.csv \
    -custom-organization Custom_Organizations.csv  \
    -region Regions.csv \
    -propagate-custom-orgs \
    -roles i2.s-Role-Based_Security_Group_Assignments_genmills3_10.12.17.csv \
    -pre-hire h.aa1-Create_Pre-Hires_genmills3.csv \
    -pre-hire h.aa1-Create_Pre-Hires_genmills3_NonSAP.csv \
    -job-change h.za-Job_Change_genmills3.csv \
    -job-change h.za-Job_Change_genmills3_NonSAP.csv \
    -role-validation-report Role_Validation_Report.csv \
    dbo*Gold.csv \
    > t.html
