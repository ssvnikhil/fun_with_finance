import streamlit as st
import pandas as pd
import re


def main():
    st.set_page_config(page_title="Retirement Game", page_icon="🎯", layout="wide")

    # Home navigation button
    if st.button("🏠 Home"):
        st.switch_page("Home.py")

    # Title and Introduction
    st.title("🎯 Let's Play a Retirement Game!")
    st.subheader("Plan your retirement effectively and see how your investments grow!")

    # Currency Selection
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
            "CNY (¥)",
        ],
    )

    # Numerical System Selection
    if currency == "INR (₹)":
        numerical_system_options = ["Thousand", "Lakhs", "Crores"]
        multipliers = {"Thousand": 1_000, "Lakhs": 100_000, "Crores": 10_000_000}
    else:
        numerical_system_options = ["Thousand", "Millions", "Billions", "Trillions"]
        multipliers = {
            "Thousand": 1_000,
            "Millions": 1_000_000,
            "Billions": 1_000_000_000,
            "Trillions": 1_000_000_000_000,
        }

    col1, col2 = st.columns([1, 1])
    with col1:
        base_amount = st.number_input(
            "Enter the base retirement amount (0-1000):",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=1.0,
            format="%.2f",
        )
    with col2:
        num_system = st.selectbox(
            "Select Numerical System", options=numerical_system_options
        )

    # Calculate total retirement amount
    retirement_amount = base_amount * multipliers[num_system]

    # Lump-Sum Investment Details
    lump_sum_details = st.number_input(
        "Lump sum available for investment:",
        min_value=0.0,
        value=10000.0,
        step=1.0,
        format="%.2f",
    )

    # Investment Type
    investment_type = st.radio(
        "Investment Type", options=["Single investment", "Regular investment per year"]
    )

    annual_investment = 0.0
    if investment_type == "Regular investment per year":
        annual_investment = st.number_input(
            f"Enter annual investment amount in {currency}: ",
            min_value=0.0,
            value=5000.00,
            step=1000.00,
            format="%.2f",
        )

    # Other Inputs
    col1, col2 = st.columns([1, 1])
    with col1:
        current_age = st.number_input(
            "Enter your current age:",
            min_value=0,
            max_value=120,
            value=30,
            step=1,
            format="%d",
        )
    with col2:
        retirement_age = st.number_input(
            "Enter desired retirement age:",
            min_value=0,
            max_value=120,
            value=65,
            step=1,
            format="%d",
        )

    rate_of_return = st.slider(
        "Estimated rate of return per year (in %):", min_value=0, max_value=50, value=7
    )

    if st.button("Calculate"):
        if retirement_age <= current_age:
            st.error("Retirement age must be greater than your current age.")
        else:
            match = re.search(r"\((.*?)\)", currency)
            symbol = match.group(1) if match else currency

            ages = list(range(current_age, retirement_age + 1))
            results = []
            r = rate_of_return / 100
            total_allocated_investment = lump_sum_details

            for age in ages:
                years_to_retirement = retirement_age - age

                if investment_type == "Single investment":
                    required = (
                        retirement_amount / ((1 + r) ** years_to_retirement)
                        if rate_of_return
                        else retirement_amount
                    )
                    invest_annually = required if age == current_age else 0
                else:
                    fv_contrib = (
                        annual_investment * (((1 + r) ** years_to_retirement - 1) / r)
                        if r != 0
                        else annual_investment * years_to_retirement
                    )
                    adjusted_target = retirement_amount - fv_contrib
                    required = (
                        (adjusted_target / ((1 + r) ** years_to_retirement))
                        if adjusted_target > 0
                        else 0
                    )
                    invest_annually = (
                        required if age == current_age else annual_investment
                    )

                available_investment = (
                    lump_sum_details
                    if age == current_age
                    else (
                        annual_investment
                        if investment_type == "Regular investment per year"
                        else 0
                    )
                )
                total_allocated_investment = (
                    (total_allocated_investment * (1 + r)) + annual_investment
                    if age > current_age
                    else lump_sum_details * ((1 + r) ** (age - current_age))
                )

                results.append(
                    {
                        "Age": age,
                        f"Available Investment per Year ({symbol})": f"{available_investment:,.2f}",
                        f"Amount Accumulated per Year ({symbol})": f"{total_allocated_investment:,.2f}",
                        f"Desired Amount to Invest Annually ({symbol})": f"{invest_annually:,.2f}",
                        f"Desired Corpus Amount ({symbol})": f"{required:,.2f}",
                    }
                )

            df = pd.DataFrame(results)
            st.subheader("📋 Retirement Investment Plan by Age")
            st.markdown(df.to_html(index=False), unsafe_allow_html=True)

            final_accumulated_corpus = float(
                df.iloc[-1][f"Amount Accumulated per Year ({symbol})"].replace(",", "")
            )
            final_desired_corpus = float(
                df.iloc[-1][f"Desired Corpus Amount ({symbol})"].replace(",", "")
            )
            shortfall = final_desired_corpus - final_accumulated_corpus

            st.subheader("📊 Retirement Plan Conclusion")
            currency_in_words = currency.split(" ")[0]
            if final_accumulated_corpus >= final_desired_corpus:
                st.success(
                    f"""
            🎉 **Hurray!**  
            - You will have **{symbol}{final_accumulated_corpus:,.2f}** by age **{retirement_age}**.  
            - This is more than your desired retirement corpus of **{final_desired_corpus:,.2f} {currency_in_words}**.  
            
            ✅ You're all set for retirement! 🚀
            """
                )
            else:
                st.warning(
                    f"""
            ⚠️ **Shortfall Detected!**  
            - Your projected corpus at age **{retirement_age}** is **{symbol}{final_accumulated_corpus:,.2f}**  
            - This is **short** by **{symbol}{shortfall:,.2f}** from your desired corpus of **{final_desired_corpus:,.2f} {currency_in_words}**.
            
            📈 You may need to **increase your annual investment** or **extend your retirement age** to achieve your target.
            """
                )


if __name__ == "__main__":
    main()
