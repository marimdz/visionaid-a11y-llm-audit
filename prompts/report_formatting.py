"""
These prompt elements are designed for testing different output specifications.
"""

csv_report_minimum = """
The report should be structured as csv and include the following columns: 
  ID, 
  element_name, 
  browser_combination, 
  page_title, 
  issue_title, 
  steps_to_reproduce, 
  actual_result, 
  expected_result, 
  recommendation, 
  wcag_sc, 
  category, 
  log_date, and 
  reported_by.
"""