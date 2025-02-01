import streamlit as st
import pandas as pd
import re

st.title("Let's play a game!")

# --- Currency Selection ---
currency = st.selectbox(
    "Select the currency that you're interested:",
    options=[
        "USD ($)", 
        "INR (₹)",
        "EUR (€)", 
        "GBP (£)", 
        "JPY (¥)", 
        "AUD (A$)", 
        "CAD (C$)", 
        "CHF (CHF)", 
        "CNY (¥)"  
    ]
)

# --- Set Numerical System Options and Multipliers Based on Currency ---
if currency == "INR (₹)":
    numerical_system_options = ["Thousand", "Lakhs", "Crores"]
    multipliers = {
        "Thousand": 1_000,
        "Lakhs": 100_000,
        "Crores": 10_000_000
    }
else:
    numerical_system_options = ["Thousand", "Millions", "Billions", "Trillions"]
    multipliers = {
        "Thousand": 1_000,
        "Millions": 1_000_000,
        "Billions": 1_000_000_000,
        "Trillions": 1_000_000_000_000
    }

# --- Base Amount and Numerical System Input in Two Columns ---
col_ret_base, col_ret_system = st.columns([1, 1])
with col_ret_base:
    base_amount = st.number_input(
        "Enter the base retirement amount (0-1000):",
        min_value=0.0,
        max_value=1000.0,
        value=100.0,
        step=1.0,
        format="%.2f"
    )
with col_ret_system:
    num_system = st.selectbox(
        "Select Numerical System",
        options=numerical_system_options
    )

# Calculate the total retirement amount based on the selected numerical system
retirement_amount = base_amount * multipliers[num_system]

# --- Lump-Sum Investment Details ---
lump_sum_details = st.number_input(
    "Do you have a lump sum amount available for investment? If yes, please provide details:",
    min_value=0.0,
    value=10000.0,
    step=1.0,
    format="%.2f"
)

# --- Investment Type Selection ---
investment_type = st.radio(
    "Investment Type",
    options=["Single investment", "Regular investment per year"]
)

# For regular investments, ask for the annual investment amount.
annual_investment = 0.0
if investment_type == "Regular investment per year":
    annual_investment = st.number_input(
        f"Enter the amount that will be invested per year in {currency}: ",
        min_value=0.0,
        value=5000.00,
        step=1000.00,
        format="%.2f"
    )
    
# --- Other Inputs ---
current_age = st.number_input(
    "Enter your current age:",
    min_value=0,
    max_value=120,
    value=30,
    step=1,
    format="%d"
)

retirement_age = st.number_input(
    "Enter at which age you would like to retire:",
    min_value=0,
    max_value=120,
    value=65,
    step=1,
    format="%d"
)

rate_of_return = st.slider(
    "Estimated rate of return per year (in %):",
    min_value=0,
    max_value=50,
    value=7
)

# --- Calculation and Final Table ---
if st.button("Calculate"):
    if retirement_age <= current_age:
        st.error("Retirement age must be greater than your current age.")
    else:
        # Extract the currency symbol (e.g., '$') from the selected currency.
        match = re.search(r'\((.*?)\)', currency)
        symbol = match.group(1) if match else currency
        
        ages = list(range(current_age, retirement_age + 1))
        results = []
        r = rate_of_return / 100  # Convert rate from percentage to decimal
        
        # Initialize total accumulated investment
        total_allocated_investment = lump_sum_details
        
        for age in ages:
            years_to_retirement = retirement_age - age
            
            # --- Reverse Calculation of Required Starting Corpus ---
            if investment_type == "Single investment":
                if rate_of_return == 0:
                    required = retirement_amount
                else:
                    required = retirement_amount / ((1 + r) ** years_to_retirement)
                # For single investment:
                # The current age row gets the computed value; later rows have zero annual investment.
                invest_annually = required if age == current_age else 0
            else:  # Regular investment per year
                if r != 0:
                    fv_contrib = annual_investment * (((1 + r) ** years_to_retirement - 1) / r)
                else:
                    fv_contrib = annual_investment * years_to_retirement
                
                adjusted_target = retirement_amount - fv_contrib
                if adjusted_target < 0:
                    required = 0
                else:
                    required = adjusted_target / ((1 + r) ** years_to_retirement) if years_to_retirement > 0 else adjusted_target
                # For regular investment:
                # The current age row shows the computed required value; subsequent rows show the annual investment.
                invest_annually = required if age == current_age else annual_investment
            
            # --- Determine Available Investment per Year ---
            if investment_type == "Single investment":
                available_investment = lump_sum_details if age == current_age else 0
            else:  # Regular investment
                available_investment = lump_sum_details if age == current_age else annual_investment
                    
            # --- Calculate Amount Allocated per Year ---
            years_invested = age - current_age
            if investment_type == "Single investment":
                total_allocated_investment = lump_sum_details * ((1 + r) ** years_invested)
            else:
                # Compound the corpus and add the new investment (except for the first year)
                if age > current_age:
                    total_allocated_investment = (total_allocated_investment * (1 + r)) + annual_investment
            
            # Format the computed values.
            formatted_required = f"{symbol}{required:,.2f}"
            formatted_investment = f"{symbol}{invest_annually:,.2f}"
            formatted_available = f"{symbol}{available_investment:,.2f}"
            formatted_allocated = f"{symbol}{total_allocated_investment:,.2f}"
            
            results.append({
                "Age": age, 
                f"Available Investment per Year ({symbol})": formatted_available,
                f"Amount Accumulated per Year ({symbol})": formatted_allocated,
                f"Desired Amount to Invest Annually ({symbol})": formatted_investment,
                f"Desired Corpus Amount ({symbol})": formatted_required,
                
            })
        
        df = pd.DataFrame(results)
        st.subheader("Retirement Investment Plan by Age")
        st.markdown(df.to_html(index=False), unsafe_allow_html=True)

        # Extract last record (Retirement Age)
        final_age = results[-1]["Age"]
        final_accumulated_corpus = float(results[-1][f"Amount Accumulated per Year ({symbol})"].replace(symbol, '').replace(',', ''))
        final_desired_corpus = float(results[-1][f"Desired Corpus Amount ({symbol})"].replace(symbol, '').replace(',', ''))

        # Compare the final accumulated corpus with the desired corpus
        st.subheader("Retirement Plan Conclusion")

        if final_accumulated_corpus >= final_desired_corpus:
            st.success(f"Hurray! 🎉 You will have {symbol}{final_accumulated_corpus:,.2f} by age {final_age}, which is more than your desired retirement corpus of {symbol}{final_desired_corpus:,.2f}. You're all set for retirement! 🚀")
        else:
            shortfall = final_desired_corpus - final_accumulated_corpus
            st.warning(f"Your projected corpus at age {final_age} is {symbol}{final_accumulated_corpus:,.2f}, which is short of your desired corpus by {symbol}{shortfall:,.2f}. You may need to increase your annual investment or retirement age to achieve your target. 📈")
