"""
ChannelPRO™ — Multi-page Streamlit app structure.

This directory is prepared for migrating to Streamlit's native multi-page
app layout (https://docs.streamlit.io/get-started/multipage-apps).

Suggested page files to create as the migration proceeds:

    pages/
    ├── 1_Client_Intake.py
    ├── 2_Scoring_Criteria.py
    ├── 3_Score_Partner.py
    ├── 4_Partner_Assessment.py
    ├── 5_Partner_Classification.py
    ├── 6_Import_Data.py
    ├── 7_Partner_List.py
    ├── 8_Ask_ChannelPRO.py
    ├── 9_Break_Even_Costs.py
    ├── 10_Break_Even_Analysis.py
    ├── 11_Admin_Users.py
    └── 12_Admin_All_Clients.py

Each page should import shared utilities from the ``utils/`` package
and render only its own section of the UI.
"""
