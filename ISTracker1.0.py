import streamlit as st
import pandas as pd
from datetime import datetime

##########################
# Function to load existing inventory data from CSV file
def load_inventory_data():
    try:
        df = pd.read_csv('inventory.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Item', 'Quantity', 'Buy Price', 'Tax', 'Fees', 'Date'])
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=['Item', 'Quantity', 'Buy Price', 'Tax', 'Fees', 'Date'])
    return df


# Function to save inventory data to CSV file
def save_inventory_data(df):
    df.to_csv('inventory.csv', index=False)


# Function to load existing sales data from CSV file
def load_sales_data():
    try:
        df = pd.read_csv('sales.csv')
    except FileNotFoundError:
        df = pd.DataFrame(
            columns=['Item', 'Sales Price', 'Sales Tax', 'Sales Fees', 'Shipping', 'Sales Date', 'Quantity Sold'])
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(
            columns=['Item', 'Sales Price', 'Sales Tax', 'Sales Fees', 'Shipping', 'Sales Date', 'Quantity Sold'])
    return df


# Function to save sales data to CSV file
def save_sales_data(df):
    df.to_csv('sales.csv', index=False)


# Function to calculate total sales for each item
def calculate_total_sales(df):
    if df.empty:
        return pd.DataFrame(columns=['Total Sales', 'Total Quantity Sold'])

    filtered_sales.loc[:, 'Total Amount'] = filtered_sales['Quantity Sold'] * (
            filtered_sales['Sales Price'] - filtered_sales['Sales Tax'] - filtered_sales['Sales Fees'] - filtered_sales[
        'Shipping'])

    total_sales = df.groupby('Item')['Total Amount'].sum()
    total_quantity_sold = df.groupby('Item')['Quantity Sold'].sum()

    # Concatenate total sales and total quantity sold into a single DataFrame
    total_df = pd.concat([total_sales, total_quantity_sold], axis=1)
    total_df.columns = ['Total Sales', 'Total Quantity Sold']

    return total_df


# Function to calculate total buy price and quantity for selected item
def calculate_inventory_totals(df, item_selected):
    total_buy_price = df.loc[df['Item'] == item_selected, 'Buy Price'].sum()
    total_quantity = df.loc[df['Item'] == item_selected, 'Quantity'].sum()
    return total_buy_price, total_quantity

######################
# Function to format currency
def format_currency(amount):
    return f"${amount:,.2f}"

#############################
# Main function to run the Streamlit app
def main():
    st.title('Inventory and Sales Tracker')

    # Load existing inventory and sales data
    inventory_df = load_inventory_data()
    sales_df = load_sales_data()

    # Sidebar navigation
    st.sidebar.title('Navigation')
    page = st.sidebar.radio('Go to',
                            ['Inventory', 'Sales', 'Total Sales', 'Inventory Totals', 'Edit Inventory', 'Edit Sales', 'Sales View', 'Inventory View', 'Dashboard'])

    # Bold all labels
    st.markdown("<style>label {font-weight: bold !important;}</style>", unsafe_allow_html=True)

    if page == 'Inventory':
        st.header('Inventory')

        # Input fields for new inventory entry
        item_name = st.text_input('Item')
        item_number = st.text_input('Item Number')
        quantity = st.number_input('Quantity', min_value=0)
        buy_price = st.number_input('Buy Price', min_value=0.0)
        tax = st.number_input('Tax', min_value=0.0)
        fees = st.number_input('Fees', min_value=0.0)
        date = st.date_input('Date', datetime.now())

        # Save button to add new inventory entry
        if st.button('Save to Inventory'):
            new_inventory = pd.DataFrame(
                {'Item': [item_name], 'Item Number': [item_number], 'Quantity': [quantity],
                 'Buy Price': [buy_price], 'Tax': [tax], 'Fees': [fees], 'Date': [date]})
            inventory_df = pd.concat([inventory_df, new_inventory], ignore_index=True)
            save_inventory_data(inventory_df)
            st.success('Inventory saved successfully.')

    elif page == 'Sales':
        st.header('Sales')
        item = st.selectbox('Select Item', inventory_df['Item'])
        quantity_sold = st.number_input('Quantity Sold', min_value=0)
        sales_price = st.number_input('Sales Price', min_value=0.0)
        sales_tax = st.number_input('Sales Tax', min_value=0.0)
        sales_fees = st.number_input('Sales Fees', min_value=0.0)
        shipping = st.number_input('Shipping', min_value=0.0)
        total_amount = quantity_sold * (sales_price - sales_tax - sales_fees - shipping)
        st.write(f'Total Amount: {total_amount}')
        sales_date = st.date_input('Sales Date', datetime.now())
        if st.button('Save Sale'):
            # Subtract quantity sold from inventory quantity
            inventory_df.loc[inventory_df['Item'] == item, 'Quantity'] -= quantity_sold

            # Save the updated inventory data
            save_inventory_data(inventory_df)

            # Save the sale data
            new_sale = pd.DataFrame({'Item': [item], 'Sales Price': [sales_price], 'Sales Tax': [sales_tax],
                                     'Sales Fees': [sales_fees], 'Shipping': [shipping], 'Sales Date': [sales_date],
                                     'Quantity Sold': [quantity_sold]})
            sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
            save_sales_data(sales_df)
            st.success('Sale saved successfully.')


    elif page == 'Total Sales':
        st.header('Total Sales')
        selected_item = st.selectbox('Select Item', sales_df['Item'].unique())
        filtered_sales = sales_df[sales_df['Item'] == selected_item]
        if not filtered_sales.empty:
            filtered_sales['Total Amount'] = filtered_sales['Quantity Sold'] * (
                    filtered_sales['Sales Price'] - filtered_sales['Sales Tax'] - filtered_sales['Sales Fees'] -
                    filtered_sales['Shipping'])
            total_sales = filtered_sales['Total Amount'].sum()
            total_quantity_sold = filtered_sales['Quantity Sold'].sum()

            st.write('Selected Item:', selected_item)
            st.write('Total Sales:', total_sales)
            st.write('Total Quantity Sold:', total_quantity_sold)
        else:
            st.warning('Total sales information is not available for this item.')


    elif page == 'Inventory Totals':
        st.header('Inventory Totals')
        item_selected = st.selectbox('Select Item', inventory_df['Item'].unique())
        total_buy_price, total_quantity = calculate_inventory_totals(inventory_df, item_selected)
        st.write('Total Buy Price:')
        st.write(total_buy_price)
        st.write('Total Quantity:')
        st.write(total_quantity)
    elif page == 'Edit Inventory':
        st.header('Edit Inventory')
        selected_item = st.selectbox('Select Item to Edit', inventory_df['Item'].unique())
        selected_row = inventory_df[inventory_df['Item'] == selected_item].iloc[0]

        item_name = st.text_input('Item', value=selected_row['Item'])
        quantity = st.number_input('Quantity', value=selected_row['Quantity'])
        item_number = st.text_input('Item Number', value=selected_row['Item Number'])
        buy_price = st.number_input('Buy Price', value=selected_row['Buy Price'])
        tax = st.number_input('Tax', value=selected_row['Tax'])
        fees = st.number_input('Fees', value=selected_row['Fees'])
        date = st.date_input('Date', value=pd.to_datetime(selected_row['Date']))

        if st.button('Save Edit'):
            inventory_df.loc[inventory_df['Item'] == selected_item, 'Item'] = item_name
            inventory_df.loc[inventory_df['Item'] == selected_item, 'Quantity'] = quantity
            inventory_df.loc[inventory_df['Item'] == selected_item, 'Item Number'] = item_number
            inventory_df.loc[inventory_df['Item'] == selected_item, 'Buy Price'] = buy_price
            inventory_df.loc[inventory_df['Item'] == selected_item, 'Tax'] = tax
            inventory_df.loc[inventory_df['Item'] == selected_item, 'Fees'] = fees
            inventory_df.loc[inventory_df['Item'] == selected_item, 'Date'] = date
            save_inventory_data(inventory_df)
            st.success('Edit saved successfully.')

        if st.button('Delete Item'):
            inventory_df = inventory_df[inventory_df['Item'] != selected_item]
            save_inventory_data(inventory_df)
            st.success('Item deleted successfully.')

##################################################
    elif page == 'Edit Sales':
        st.header('Edit Sales')

        if sales_df.empty:
            st.warning('No sales data available. Please add sales data first.')
        else:
            selected_item = st.selectbox('Select Item to Edit', sales_df['Item'].unique())
            selected_row = sales_df[sales_df['Item'] == selected_item].iloc[0]

            sales_price = st.number_input('Sales Price', value=selected_row['Sales Price'])
            sales_tax = st.number_input('Sales Tax', value=selected_row['Sales Tax'])
            sales_fees = st.number_input('Sales Fees', value=selected_row['Sales Fees'])
            shipping = st.number_input('Shipping', value=selected_row['Shipping'])
            quantity_sold = st.number_input('Quantity Sold', value=selected_row['Quantity Sold'])
            sales_date = st.date_input('Sales Date', value=pd.to_datetime(selected_row['Sales Date']))

            if st.button('Save Edit'):
                sales_df.loc[sales_df['Item'] == selected_item, 'Sales Price'] = sales_price
                sales_df.loc[sales_df['Item'] == selected_item, 'Sales Tax'] = sales_tax
                sales_df.loc[sales_df['Item'] == selected_item, 'Sales Fees'] = sales_fees
                sales_df.loc[sales_df['Item'] == selected_item, 'Shipping'] = shipping
                sales_df.loc[sales_df['Item'] == selected_item, 'Quantity Sold'] = quantity_sold
                sales_df.loc[sales_df['Item'] == selected_item, 'Sales Date'] = sales_date
                save_sales_data(sales_df)
                st.success('Edit saved successfully.')

            if st.button('Delete Sale'):
                sales_df = sales_df[sales_df['Item'] != selected_item]
                save_sales_data(sales_df)
                st.success('Sale deleted successfully.')

###########################################################################################
    elif page == 'Sales View':
        st.header('Sales View')

        # Load existing sales data
        sales_df = load_sales_data()

        st.write('Sales View:')
        st.markdown("""
                    <div style="height: 450px; overflow-y: scroll; border: 1px solid #e6e9ef; border-radius: 10px; padding: 10px;">
                        {}
                    </div>
                """.format(sales_df.to_html(index=False)), unsafe_allow_html=True)


######################################################################################
    elif page == 'Inventory View':
        st.header('Inventory View')

##################################################################################################
        # Display existing sales data
        st.write('Inventory View:')
        st.markdown("""
            <div style="height: 450px; overflow-y: scroll; border: 1px solid #e6e9ef; border-radius: 10px; padding: 10px;">
                {}
            </div>
        """.format(inventory_df.to_html(index=False)), unsafe_allow_html=True)
#################################################################################################
    elif page == 'Dashboard':
        st.header('Dashboard')

        # Calculate total sales price, sales tax, sales fees, and shipping
        total_sales_price_sum = sales_df['Sales Price'].sum()
        total_sales_tax_sum = sales_df['Sales Tax'].sum()
        total_sales_fees_sum = sales_df['Sales Fees'].sum()
        total_shipping_sum = sales_df['Shipping'].sum()

        # Calculate total buy price
        total_buy_price_sum = inventory_df['Buy Price'].sum()

        # Calculate profit or loss
        profit_or_loss = total_sales_price_sum + total_sales_tax_sum + total_sales_fees_sum + total_shipping_sum - total_buy_price_sum

        # Display total sales price, sales tax, sales fees, shipping, and profit or loss
        st.write(f"Total Sales Price: {format_currency(total_sales_price_sum)}")
        st.write(f"Total Sales Tax: {format_currency(total_sales_tax_sum)}")
        st.write(f"Total Sales Fees: {format_currency(total_sales_fees_sum)}")
        st.write(f"Total Shipping: {format_currency(total_shipping_sum)}")
        st.write(f"Profit or Loss: {format_currency(profit_or_loss)}")

if __name__ == '__main__':
    main()
