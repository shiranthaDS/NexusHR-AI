"""
Sample test data for Employee Handbook
This simulates an HR policy document for demonstration purposes
"""

SAMPLE_HR_POLICIES = {
    "leave_policy": """
    LEAVE POLICY - SECTION 4.2
    
    1. SICK LEAVE
    - Each employee is entitled to 12 days of sick leave per year
    - Sick leave cannot be encashed
    - Unused sick leave will lapse on December 31st
    - Medical certificate required for sick leave exceeding 3 consecutive days
    
    2. PRIVILEGE LEAVE (PL)
    - Each employee receives 18 days of privilege leave annually
    - PL can be encashed up to 10 days at the end of the year
    - Minimum 3 days notice required for planned PL
    - PL can be carried forward up to 5 days to next year
    
    3. CASUAL LEAVE
    - 10 days of casual leave per year
    - Cannot be combined with other leave types
    - No carry forward to next year
    - Minimum 1 day notice required
    
    4. MATERNITY LEAVE
    - Female employees: 26 weeks of paid maternity leave
    - Can be availed 8 weeks before expected delivery date
    
    5. PATERNITY LEAVE
    - Male employees: 15 days of paid paternity leave
    - Must be availed within 6 months of child's birth
    """,
    
    "working_hours": """
    WORKING HOURS - SECTION 2.1
    
    1. STANDARD WORKING HOURS
    - Monday to Friday: 9:00 AM to 6:00 PM
    - Lunch break: 1:00 PM to 2:00 PM
    - Total working hours: 40 hours per week
    
    2. FLEXIBLE TIMING
    - Employees can opt for flexible timing with manager approval
    - Core hours: 11:00 AM to 4:00 PM (must be present)
    - Flexible window: 8:00 AM to 11:00 AM and 4:00 PM to 8:00 PM
    
    3. REMOTE WORK
    - Up to 2 days per week remote work allowed with manager approval
    - Full remote work requires VP approval
    - Remote work policy subject to role requirements
    
    4. OVERTIME
    - Overtime compensated at 1.5x hourly rate
    - Prior approval required from department head
    - Overtime applicable only for non-exempt employees
    """,
    
    "salary_structure": """
    COMPENSATION STRUCTURE - SECTION 6.1
    
    1. SALARY COMPONENTS
    - Basic Salary: 50% of CTC
    - House Rent Allowance: 30% of CTC
    - Special Allowance: 10% of CTC
    - Performance Bonus: Up to 10% based on annual review
    
    2. SALARY PAYMENT
    - Monthly salary paid on last working day of the month
    - Direct bank transfer to employee's account
    - Salary slip available on employee portal
    
    3. INCREMENTS
    - Annual increment based on performance review
    - Typically ranges from 8% to 15%
    - Effective from April 1st each year
    
    4. BONUS
    - Annual performance bonus paid in December
    - Variable based on individual and company performance
    - Ranges from 0% to 20% of annual CTC
    
    5. DEDUCTIONS
    - Provident Fund: 12% of basic salary
    - Professional Tax: As per state regulations
    - Income Tax: TDS as per IT regulations
    """,
    
    "performance_review": """
    PERFORMANCE EVALUATION - SECTION 8.1
    
    1. REVIEW CYCLE
    - Annual performance review in March
    - Mid-year review in September (informal)
    - Continuous feedback encouraged throughout the year
    
    2. RATING SCALE
    - Outstanding: Exceeds all expectations (5)
    - Exceeds Expectations: Above role requirements (4)
    - Meets Expectations: Satisfactory performance (3)
    - Needs Improvement: Below expectations (2)
    - Unsatisfactory: Does not meet minimum requirements (1)
    
    3. EVALUATION CRITERIA
    - Goal Achievement: 40%
    - Competencies: 30%
    - Values Alignment: 20%
    - Innovation & Initiative: 10%
    
    4. PROMOTION CRITERIA
    - Minimum 2 years in current role
    - Consistent "Exceeds Expectations" rating
    - Demonstrated leadership potential
    - Manager recommendation required
    """,
    
    "holidays": """
    HOLIDAYS AND TIME OFF - SECTION 3.1
    
    1. PUBLIC HOLIDAYS
    - 12 public holidays per year
    - List announced at beginning of calendar year
    - Includes national and state-specific holidays
    
    2. OPTIONAL HOLIDAYS
    - 3 optional holidays per year
    - Can be chosen from provided list
    - Must be informed 7 days in advance
    
    3. FESTIVAL ADVANCES
    - Festival advance available during Diwali
    - Up to one month's basic salary
    - Recovered in 10 equal installments
    
    4. COMPENSATORY OFF
    - Granted for working on weekly off or holidays
    - Must be availed within 30 days
    - Requires manager approval
    """
}


def get_sample_policy(policy_type: str = "all") -> str:
    """
    Get sample HR policy text
    
    Args:
        policy_type: Type of policy (leave_policy, working_hours, salary_structure, 
                     performance_review, holidays, or 'all' for complete handbook)
    
    Returns:
        Policy text
    """
    if policy_type == "all":
        return "\n\n" + "\n\n".join(SAMPLE_HR_POLICIES.values())
    return SAMPLE_HR_POLICIES.get(policy_type, "")


if __name__ == "__main__":
    # Generate complete handbook
    handbook = """
    ================================================================================
                            EMPLOYEE HANDBOOK 2025
                                NexusHR Company
    ================================================================================
    
    """ + get_sample_policy("all") + """
    
    ================================================================================
    END OF EMPLOYEE HANDBOOK
    For queries, contact: hr@nexushr.com
    Last Updated: January 2025
    ================================================================================
    """
    
    # Save to file
    with open("Employee_Handbook_Sample.txt", "w") as f:
        f.write(handbook)
    
    print("✅ Sample Employee Handbook created: Employee_Handbook_Sample.txt")
    print("📄 This is sample data for testing the RAG system")
