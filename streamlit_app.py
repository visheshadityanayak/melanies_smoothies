# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie!:cup_with_straw: {st.__version__}")
st.write(
    """Choose the fruits you want in your custom smoothie!
    """
)
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be :", name_on_order)
cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    my_dataframe,
    max_selections = 5)

if ingredients_list:
    # BUILD THE COMPLETE INGREDIENTS STRING FIRST (OUTSIDE THE LOOP)
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '  # Add space between fruits
    
    # DISPLAY NUTRITION INFO FOR EACH FRUIT (SEPARATE FROM INGREDIENTS STRING)
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruit_chosen + ' NUTRITION INFORMATION')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    # SHOW THE COMPLETE INGREDIENTS STRING
    st.write("Your selected ingredients:", ingredients_string)
    
    # CREATE INSERT STATEMENT (OUTSIDE THE LOOP - ONLY ONCE)
    my_insert_stmt = """INSERT INTO smoothies.public.orders (ingredients, name_on_order)
VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    
    st.write(my_insert_stmt)
    
    # SUBMIT BUTTON (OUTSIDE THE LOOP - ONLY ONE BUTTON)
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
