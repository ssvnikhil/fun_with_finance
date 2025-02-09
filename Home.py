import streamlit as st


def main():
    st.set_page_config(page_title="Fun with Finance", page_icon="💰", layout="wide")

    # Title and Subtitle
    st.title("📊 Fun with Finance")
    st.subheader("Making finance fun and interactive!")

    # Introduction
    st.markdown(
        """
        Welcome to **Fun with Finance**! This app offers interactive tools to explore financial planning, investment strategies, and retirement scenarios. 
        Choose a feature below to get started:
        """
    )

    # Features Overview
    col1, col2 = st.columns(2)

    with col1:
        st.header("🎯 Retirement Game")
        st.write(
            "Simulate your retirement journey by adjusting savings, expenses, and investment strategies to see how long your wealth lasts."
        )
        if st.button("Go to Retirement Game ➡️"):
            st.switch_page("pages/1_Retirement_Game.py")

    with col2:
        st.header("📈 Wealth Storage & Investment")
        st.write(
            "Analyze different investment options, track your wealth over time, and explore strategies for long-term financial growth."
        )
        if st.button("Go to Wealth Storage & Investment ➡️"):
            st.switch_page("pages/2_Wealth_Storage_and_Investment.py")

    # Footer
    st.markdown("---")
    st.markdown(
        """🚀 Empowering smart financial decisions  
    📢 Connect for new content creation or collaboration: [X](https://x.com/NikhilSsv)"""
    )


if __name__ == "__main__":
    main()
