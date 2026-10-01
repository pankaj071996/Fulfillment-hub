import streamlit as st
import pandas as pd
import sqlite3

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Fulfillment Hub",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #f7f8fa;
    }

    /* Main content width */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* Sidebar title */
    section[data-testid="stSidebar"] h2 {
        font-weight: 700;
    }

    /* Main headings */
    h1, h2, h3 {
        font-weight: 700;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Select boxes */
    div[data-baseweb="select"] > div {
        border-radius: 8px;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 1.5rem 0;
    }

    /* Info boxes */
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #6b7280;
        font-size: 13px;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #e5e7eb;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DATABASE
# =========================================================

DB_FILE = "fulfillment.db"


def get_connection():
    return sqlite3.connect(DB_FILE)


# =========================================================
# LOAD DATA
# =========================================================

conn = get_connection()

orders = pd.read_sql_query("SELECT * FROM orders", conn)
inventory = pd.read_sql_query("SELECT * FROM inventory", conn)
issues = pd.read_sql_query("SELECT * FROM issues", conn)
transfers = pd.read_sql_query("SELECT * FROM transfers", conn)
products = pd.read_sql_query("SELECT * FROM products", conn)
warehouses = pd.read_sql_query("SELECT * FROM warehouses", conn)
couriers = pd.read_sql_query("SELECT * FROM couriers", conn)

conn.close()

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("📦 Fulfillment Hub")
st.sidebar.caption("XYZ Order Fulfillment Management System")

st.sidebar.divider()

st.sidebar.header("🧭 Navigation")

pages = [
    "Dashboard",
    "Orders",
    "Inventory",
    "Issues",
    "Transfers",
    "Products",
    "Warehouses",
    "Couriers"
]

page = st.sidebar.selectbox(
    "Select Module",
    pages
)

st.sidebar.divider()

st.sidebar.caption("Fulfillment Hub")
st.sidebar.caption("Order & Warehouse Operations")

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("📊 Fulfillment Hub — Operations Dashboard")

    st.write(
        "Monitor order fulfillment, inventory, warehouse transfers, "
        "courier operations and operational issues."
    )

    st.divider()

    # -----------------------------
    # KEY METRICS
    # -----------------------------

    total_orders = len(orders)
    total_products = len(products)
    total_inventory = len(inventory)

    if "Status" in issues.columns:
        open_issues = len(
            issues[
                issues["Status"]
                .astype(str)
                .str.lower()
                .eq("open")
            ]
        )
    else:
        open_issues = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📦 Total Orders",
            total_orders
        )

    with col2:
        st.metric(
            "🏷️ Products / SKUs",
            total_products
        )

    with col3:
        st.metric(
            "📋 Inventory Records",
            total_inventory
        )

    with col4:
        st.metric(
            "⚠️ Open Issues",
            open_issues
        )

    st.divider()

    # -----------------------------
    # ORDER STATUS
    # -----------------------------

    st.subheader("📊 Order Status Overview")

    if "Status" in orders.columns:

        status_counts = (
            orders["Status"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Orders")
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            st.dataframe(
                status_counts,
                use_container_width=True,
                hide_index=True
            )

        with col2:
            st.bar_chart(
                status_counts.set_index("Status")["Orders"]
            )

    st.divider()

    # -----------------------------
    # RECENT ORDERS
    # -----------------------------

    st.subheader("📋 Recent Orders")

    st.caption("Latest 20 orders currently available in the fulfillment system.")

    st.dataframe(
        orders.head(20),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# ORDERS
# =========================================================

elif page == "Orders":

    st.title("📦 Order Management")

    st.write(
        "Search, monitor and update order fulfillment status."
    )

    st.divider()

    # -----------------------------
    # FILTERS
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        search_order = st.text_input(
            "🔎 Search Order ID",
            placeholder="Enter Order ID..."
        )

    with col2:
        status_options = ["All"] + sorted(
            orders["Status"].dropna().astype(str).unique().tolist()
        )

        status_filter = st.selectbox(
            "📌 Order Status",
            status_options
        )

    with col3:
        priority_options = ["All"] + sorted(
            orders["Priority"].dropna().astype(str).unique().tolist()
        )

        priority_filter = st.selectbox(
            "🚨 Priority",
            priority_options
        )

    filtered_orders = orders.copy()

    if search_order:
        filtered_orders = filtered_orders[
            filtered_orders["Order ID"]
            .astype(str)
            .str.contains(
                search_order,
                case=False,
                na=False
            )
        ]

    if status_filter != "All":
        filtered_orders = filtered_orders[
            filtered_orders["Status"] == status_filter
        ]

    if priority_filter != "All":
        filtered_orders = filtered_orders[
            filtered_orders["Priority"] == priority_filter
        ]

    st.subheader("📋 Orders")

    st.dataframe(
        filtered_orders,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # SELECT ORDER
    # -----------------------------

    if len(filtered_orders) > 0:

        selected_order_id = st.selectbox(
            "Select an Order",
            filtered_orders["Order ID"].tolist()
        )

        selected_order = filtered_orders[
            filtered_orders["Order ID"] == selected_order_id
        ].iloc[0]

        st.subheader("📄 Order Details")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"**Order ID:** {selected_order['Order ID']}")
            st.write(f"**Customer:** {selected_order['Customer']}")
            st.write(f"**Product:** {selected_order['Product']}")
            st.write(f"**SKU:** {selected_order['SKU']}")

        with col2:
            st.write(f"**Variant:** {selected_order['Variant']}")
            st.write(f"**Color:** {selected_order['Color']}")
            st.write(f"**Qty:** {selected_order['Qty']}")
            st.write(f"**Priority:** {selected_order['Priority']}")

        with col3:
            st.write(f"**Courier:** {selected_order['Courier']}")
            st.write(f"**Ship From:** {selected_order['Ship From']}")
            st.write(f"**Order Value:** ₹{selected_order['Order Value']}")
            st.write(f"**Current Status:** {selected_order['Status']}")

        st.divider()

        # -----------------------------
        # ORDER ACTIONS
        # -----------------------------

        current_status = str(
            selected_order["Status"]
        ).strip().lower()

        if current_status == "pending":

            if st.button(
                "📦 Mark as Picked",
                key="order_picked"
            ):
                conn = get_connection()

                conn.execute(
                    """
                    UPDATE orders
                    SET "Status" = ?
                    WHERE "Order ID" = ?
                    """,
                    ("Picked", selected_order_id)
                )

                conn.commit()
                conn.close()

                st.success("Order marked as Picked.")
                st.rerun()

        elif current_status == "picked":

            if st.button(
                "📦 Mark as Packed",
                key="order_packed"
            ):
                conn = get_connection()

                conn.execute(
                    """
                    UPDATE orders
                    SET "Status" = ?
                    WHERE "Order ID" = ?
                    """,
                    ("Packed", selected_order_id)
                )

                conn.commit()
                conn.close()

                st.success("Order marked as Packed.")
                st.rerun()

        elif current_status == "packed":

            if st.button(
                "🚚 Mark as Shipped",
                key="order_shipped"
            ):
                conn = get_connection()

                conn.execute(
                    """
                    UPDATE orders
                    SET "Status" = ?
                    WHERE "Order ID" = ?
                    """,
                    ("Shipped", selected_order_id)
                )

                conn.commit()
                conn.close()

                st.success("Order marked as Shipped.")
                st.rerun()

        elif current_status == "shipped":

            if st.button(
                "✅ Mark as Delivered",
                key="order_delivered"
            ):
                conn = get_connection()

                conn.execute(
                    """
                    UPDATE orders
                    SET "Status" = ?
                    WHERE "Order ID" = ?
                    """,
                    ("Delivered", selected_order_id)
                )

                conn.commit()
                conn.close()

                st.success("Order marked as Delivered.")
                st.rerun()

        elif current_status == "delivered":

            st.success("✅ Order is already Delivered.")

        elif current_status == "delayed":

            st.warning(
                "⚠️ This order is Delayed and requires attention."
            )

        elif current_status == "stock issue":

            st.error(
                "⚠️ This order has a Stock Issue and requires inventory action."
            )

        else:

            st.info(
                "ℹ️ No workflow action is available for this status."
            )


# =========================================================
# INVENTORY
# =========================================================

elif page == "Inventory":

    st.title("📦 Inventory Management")

    st.write(
        "Monitor stock across Main Warehouse and Backup Warehouse."
    )

    st.divider()

    # -----------------------------
    # METRICS
    # -----------------------------

    main_stock = inventory["Main WH Qty"].sum()
    backup_stock = inventory["Backup WH Qty"].sum()
    total_stock = inventory["Total Qty"].sum()

    low_stock = inventory[
        inventory["Main WH Status"]
        .astype(str)
        .str.lower()
        .str.contains(
            "low|reorder|critical",
            na=False
        )
    ]

    low_stock_count = len(low_stock)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Main WH Stock",
            int(main_stock)
        )

    with col2:
        st.metric(
            "Backup WH Stock",
            int(backup_stock)
        )

    with col3:
        st.metric(
            "Total Stock",
            int(total_stock)
        )

    with col4:
        st.metric(
            "Low Stock SKUs",
            low_stock_count
        )

    st.divider()

    # -----------------------------
    # FILTERS
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:
        inventory_search = st.text_input(
            "🔎 Search SKU / Product",
            placeholder="Search inventory..."
        )

    with col2:
        inventory_status_options = ["All"] + sorted(
            inventory["Main WH Status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        inventory_status_filter = st.selectbox(
            "📌 Main WH Stock Status",
            inventory_status_options
        )

    filtered_inventory = inventory.copy()

    if inventory_search:

        search_text = inventory_search.lower()

        filtered_inventory = filtered_inventory[
            filtered_inventory["SKU"]
            .astype(str)
            .str.lower()
            .str.contains(search_text, na=False)
            |
            filtered_inventory["Product"]
            .astype(str)
            .str.lower()
            .str.contains(search_text, na=False)
        ]

    if inventory_status_filter != "All":

        filtered_inventory = filtered_inventory[
            filtered_inventory["Main WH Status"]
            == inventory_status_filter
        ]

    # -----------------------------
    # CURRENT INVENTORY
    # -----------------------------

    st.subheader("📦 Current Inventory")

    st.dataframe(
        filtered_inventory,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # LOW STOCK
    # -----------------------------

    st.subheader("⚠️ Low Stock / Reorder Required")

    if len(low_stock) > 0:

        st.warning(
            f"{len(low_stock)} SKU(s) may require stock attention."
        )

        st.dataframe(
            low_stock,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success("No low-stock SKUs found.")

    st.divider()

    # -----------------------------
    # STOCK TRANSFER RECOMMENDATION
    # -----------------------------

    st.subheader("🔄 Stock Transfer Recommendation")

    transfer_candidates = inventory[
        (inventory["Main WH Qty"] < inventory["Reorder Level"])
        &
        (inventory["Backup WH Qty"] > 0)
    ].copy()

    if len(transfer_candidates) > 0:

        transfer_candidates["Suggested Transfer Qty"] = (
            transfer_candidates["Reorder Level"]
            - transfer_candidates["Main WH Qty"]
        ).clip(lower=0)

        recommendation_columns = [
            "SKU",
            "Product",
            "Main WH Qty",
            "Backup WH Qty",
            "Reorder Level",
            "Suggested Transfer Qty"
        ]

        st.dataframe(
            transfer_candidates[recommendation_columns],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No immediate stock transfer recommendation."
        )


# =========================================================
# ISSUES
# =========================================================

elif page == "Issues":

    st.title("⚠️ Issue Management")

    st.write(
        "Track, investigate and resolve fulfillment problems."
    )

    st.divider()

    # -----------------------------
    # METRICS
    # -----------------------------

    total_issues = len(issues)

    open_issues = len(
        issues[
            issues["Status"]
            .astype(str)
            .str.lower()
            .eq("open")
        ]
    )

    high_priority = len(
        issues[
            issues["Priority"]
            .astype(str)
            .str.lower()
            .eq("high")
        ]
    )

    resolved_issues = len(
        issues[
            issues["Status"]
            .astype(str)
            .str.lower()
            .eq("resolved")
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Issues", total_issues)

    with col2:
        st.metric("Open Issues", open_issues)

    with col3:
        st.metric("High Priority", high_priority)

    with col4:
        st.metric("Resolved", resolved_issues)

    st.divider()

    # -----------------------------
    # FILTERS
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:

        issue_status_options = ["All"] + sorted(
            issues["Status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        issue_status_filter = st.selectbox(
            "📌 Issue Status",
            issue_status_options
        )

    with col2:

        issue_type_options = ["All"] + sorted(
            issues["Issue Type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        issue_type_filter = st.selectbox(
            "🛠️ Issue Type",
            issue_type_options
        )

    filtered_issues = issues.copy()

    if issue_status_filter != "All":

        filtered_issues = filtered_issues[
            filtered_issues["Status"]
            == issue_status_filter
        ]

    if issue_type_filter != "All":

        filtered_issues = filtered_issues[
            filtered_issues["Issue Type"]
            == issue_type_filter
        ]

    st.subheader("⚠️ Current Issues")

    st.dataframe(
        filtered_issues,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # SELECT ISSUE
    # -----------------------------

    if len(filtered_issues) > 0:

        selected_issue_id = st.selectbox(
            "Select Issue",
            filtered_issues["Issue ID"].tolist()
        )

        selected_issue = filtered_issues[
            filtered_issues["Issue ID"]
            == selected_issue_id
        ].iloc[0]

        st.subheader("📄 Issue Details")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Issue ID:** {selected_issue['Issue ID']}")
            st.write(f"**Order ID:** {selected_issue['Order ID']}")
            st.write(f"**Issue Type:** {selected_issue['Issue Type']}")
            st.write(f"**Description:** {selected_issue['Description']}")

        with col2:
            st.write(f"**Status:** {selected_issue['Status']}")
            st.write(f"**Priority:** {selected_issue['Priority']}")
            st.write(f"**Owner:** {selected_issue['Owner']}")
            st.write(f"**Reported At:** {selected_issue['Reported At']}")

        st.divider()

        current_issue_status = str(
            selected_issue["Status"]
        ).strip().lower()

        if current_issue_status in ["open", "investigating"]:

            if st.button(
                "✅ Mark Issue as Resolved",
                key="resolve_issue"
            ):

                conn = get_connection()

                conn.execute(
                    """
                    UPDATE issues
                    SET "Status" = ?
                    WHERE "Issue ID" = ?
                    """,
                    ("Resolved", selected_issue_id)
                )

                conn.commit()
                conn.close()

                st.success("Issue marked as Resolved.")
                st.rerun()

        elif current_issue_status == "resolved":

            st.success("✅ This issue is already Resolved.")

        else:

            st.info(
                "ℹ️ No action is available for this issue status."
            )


# =========================================================
# TRANSFERS
# =========================================================

elif page == "Transfers":

    st.title("🔄 Transfer Management")

    st.write(
        "Monitor stock movement between Backup Warehouse and Main Warehouse."
    )

    st.divider()

    # -----------------------------
    # METRICS
    # -----------------------------

    total_transfers = len(transfers)

    pending_transfers = len(
        transfers[
            transfers["Status"]
            .astype(str)
            .str.lower()
            .isin(
                ["pending", "requested", "open"]
            )
        ]
    )

    completed_transfers = len(
        transfers[
            transfers["Status"]
            .astype(str)
            .str.lower()
            .isin(
                ["completed", "complete", "received"]
            )
        ]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Transfers",
            total_transfers
        )

    with col2:
        st.metric(
            "Pending Transfers",
            pending_transfers
        )

    with col3:
        st.metric(
            "Completed Transfers",
            completed_transfers
        )

    st.divider()

    # -----------------------------
    # FILTERS
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:

        transfer_status_options = ["All"] + sorted(
            transfers["Status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        transfer_status_filter = st.selectbox(
            "📌 Transfer Status",
            transfer_status_options
        )

    with col2:

        warehouse_values = sorted(
            set(
                transfers["From Warehouse"]
                .dropna()
                .astype(str)
                .tolist()
            )
            |
            set(
                transfers["To Warehouse"]
                .dropna()
                .astype(str)
                .tolist()
            )
        )

        warehouse_filter = st.selectbox(
            "🏭 Warehouse",
            ["All"] + warehouse_values
        )

    filtered_transfers = transfers.copy()

    if transfer_status_filter != "All":

        filtered_transfers = filtered_transfers[
            filtered_transfers["Status"]
            == transfer_status_filter
        ]

    if warehouse_filter != "All":

        filtered_transfers = filtered_transfers[
            (
                filtered_transfers["From Warehouse"]
                == warehouse_filter
            )
            |
            (
                filtered_transfers["To Warehouse"]
                == warehouse_filter
            )
        ]

    st.subheader("🔄 Transfer Requests")

    st.dataframe(
        filtered_transfers,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # TRANSFER DETAILS
    # -----------------------------

    if len(filtered_transfers) > 0:

        selected_transfer_id = st.selectbox(
            "Select a Transfer",
            filtered_transfers["Transfer ID"].tolist()
        )

        selected_transfer = filtered_transfers[
            filtered_transfers["Transfer ID"]
            == selected_transfer_id
        ].iloc[0]

        st.subheader("📄 Transfer Details")

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Transfer ID:** {selected_transfer['Transfer ID']}"
            )
            st.write(
                f"**SKU:** {selected_transfer['SKU']}"
            )
            st.write(
                f"**Product:** {selected_transfer['Product']}"
            )
            st.write(
                f"**Qty:** {selected_transfer['Qty']}"
            )

        with col2:
            st.write(
                f"**From Warehouse:** {selected_transfer['From Warehouse']}"
            )
            st.write(
                f"**To Warehouse:** {selected_transfer['To Warehouse']}"
            )
            st.write(
                f"**Status:** {selected_transfer['Status']}"
            )
            st.write(
                f"**Reason:** {selected_transfer['Reason']}"
            )

        st.divider()

        current_transfer_status = str(
            selected_transfer["Status"]
        ).strip().lower()

        if current_transfer_status in [
            "pending",
            "requested",
            "open"
        ]:

            if st.button(
                "🚚 Mark as In Transit",
                key="transfer_transit"
            ):

                conn = get_connection()

                conn.execute(
                    """
                    UPDATE transfers
                    SET "Status" = ?
                    WHERE "Transfer ID" = ?
                    """,
                    ("In Transit", selected_transfer_id)
                )

                conn.commit()
                conn.close()

                st.success("Transfer marked as In Transit.")
                st.rerun()

        elif current_transfer_status == "in transit":

            if st.button(
                "✅ Mark as Completed",
                key="transfer_completed"
            ):

                conn = get_connection()

                conn.execute(
                    """
                    UPDATE transfers
                    SET "Status" = ?
                    WHERE "Transfer ID" = ?
                    """,
                    ("Completed", selected_transfer_id)
                )

                conn.commit()
                conn.close()

                st.success("Transfer marked as Completed.")
                st.rerun()

        elif current_transfer_status in [
            "completed",
            "complete",
            "received"
        ]:

            st.success("✅ This transfer is already Completed.")

        else:

            st.info(
                "ℹ️ No action is available for this transfer status."
            )


# =========================================================
# PRODUCTS
# =========================================================

elif page == "Products":

    st.title("🏷️ Product Management")

    st.write(
        "Manage product and SKU master information."
    )

    st.divider()

    # -----------------------------
    # METRICS
    # -----------------------------

    total_skus = len(products)

    categories_count = (
        products["Category"].nunique()
        if "Category" in products.columns
        else 0
    )

    product_count = (
        products["Product"].nunique()
        if "Product" in products.columns
        else 0
    )

    avg_price = (
        products["Unit Price"].mean()
        if "Unit Price" in products.columns
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total SKUs", total_skus)

    with col2:
        st.metric("Categories", categories_count)

    with col3:
        st.metric("Products", product_count)

    with col4:
        st.metric(
            "Avg. Unit Price",
            f"₹{avg_price:,.0f}"
        )

    st.divider()

    # -----------------------------
    # FILTERS
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        product_search = st.text_input(
            "🔎 Search SKU / Product",
            placeholder="Search..."
        )

    with col2:

        category_options = ["All"] + sorted(
            products["Category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        category_filter = st.selectbox(
            "Category",
            category_options
        )

    with col3:

        variant_options = ["All"] + sorted(
            products["Variant"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        variant_filter = st.selectbox(
            "Variant",
            variant_options
        )

    filtered_products = products.copy()

    if product_search:

        search_text = product_search.lower()

        filtered_products = filtered_products[
            filtered_products["SKU"]
            .astype(str)
            .str.lower()
            .str.contains(search_text, na=False)
            |
            filtered_products["Product"]
            .astype(str)
            .str.lower()
            .str.contains(search_text, na=False)
        ]

    if category_filter != "All":

        filtered_products = filtered_products[
            filtered_products["Category"]
            == category_filter
        ]

    if variant_filter != "All":

        filtered_products = filtered_products[
            filtered_products["Variant"]
            == variant_filter
        ]

    st.subheader("🏷️ Product Catalogue")

    st.dataframe(
        filtered_products,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # PRODUCT DETAILS
    # -----------------------------

    if len(filtered_products) > 0:

        selected_sku = st.selectbox(
            "Select SKU",
            filtered_products["SKU"].tolist()
        )

        selected_product = filtered_products[
            filtered_products["SKU"] == selected_sku
        ].iloc[0]

        st.subheader("📄 Product Details")

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**SKU:** {selected_product['SKU']}"
            )
            st.write(
                f"**Product:** {selected_product['Product']}"
            )
            st.write(
                f"**Category:** {selected_product['Category']}"
            )

        with col2:
            st.write(
                f"**Variant:** {selected_product['Variant']}"
            )
            st.write(
                f"**Color:** {selected_product['Color']}"
            )
            st.write(
                f"**Unit Price:** ₹{selected_product['Unit Price']}"
            )


# =========================================================
# WAREHOUSES
# =========================================================

elif page == "Warehouses":

    st.title("🏭 Warehouse Management")

    st.write(
        "Monitor warehouse locations, types and operational status."
    )

    st.divider()

    # -----------------------------
    # METRICS
    # -----------------------------

    total_warehouses = len(warehouses)

    active_warehouses = len(
        warehouses[
            warehouses["Status"]
            .astype(str)
            .str.lower()
            .eq("active")
        ]
    )

    main_warehouse_count = len(
        warehouses[
            warehouses["Type"]
            .astype(str)
            .str.lower()
            .isin(
                ["main", "primary"]
            )
        ]
    )

    backup_warehouse_count = len(
        warehouses[
            warehouses["Type"]
            .astype(str)
            .str.lower()
            .isin(
                ["backup", "secondary", "overflow"]
            )
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Warehouses",
            total_warehouses
        )

    with col2:
        st.metric(
            "Active Warehouses",
            active_warehouses
        )

    with col3:
        st.metric(
            "Main Warehouse",
            main_warehouse_count
        )

    with col4:
        st.metric(
            "Backup Warehouse",
            backup_warehouse_count
        )

    st.divider()

    # -----------------------------
    # FILTERS
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        warehouse_search = st.text_input(
            "🔎 Search Warehouse",
            placeholder="ID / Name / Location"
        )

    with col2:

        warehouse_type_options = ["All"] + sorted(
            warehouses["Type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        warehouse_type_filter = st.selectbox(
            "Warehouse Type",
            warehouse_type_options
        )

    with col3:

        warehouse_status_options = ["All"] + sorted(
            warehouses["Status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        warehouse_status_filter = st.selectbox(
            "Warehouse Status",
            warehouse_status_options
        )

    filtered_warehouses = warehouses.copy()

    if warehouse_search:

        search_text = warehouse_search.lower()

        filtered_warehouses = filtered_warehouses[
            filtered_warehouses["Warehouse ID"]
            .astype(str)
            .str.lower()
            .str.contains(search_text, na=False)
            |
            filtered_warehouses["Warehouse Name"]
            .astype(str)
            .str.lower()
            .str.contains(search_text, na=False)
            |
            filtered_warehouses["Location"]
            .astype(str)
            .str.lower()
            .str.contains(search_text, na=False)
        ]

    if warehouse_type_filter != "All":

        filtered_warehouses = filtered_warehouses[
            filtered_warehouses["Type"]
            == warehouse_type_filter
        ]

    if warehouse_status_filter != "All":

        filtered_warehouses = filtered_warehouses[
            filtered_warehouses["Status"]
            == warehouse_status_filter
        ]

    st.subheader("🏭 Warehouse Directory")

    st.dataframe(
        filtered_warehouses,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # WAREHOUSE DETAILS
    # -----------------------------

    if len(filtered_warehouses) > 0:

        warehouse_labels = [
            f"{row['Warehouse ID']} - {row['Warehouse Name']}"
            for _, row in filtered_warehouses.iterrows()
        ]

        selected_warehouse_label = st.selectbox(
            "Select Warehouse",
            warehouse_labels
        )

        selected_index = warehouse_labels.index(
            selected_warehouse_label
        )

        selected_warehouse = filtered_warehouses.iloc[
            selected_index
        ]

        st.subheader("📄 Warehouse Details")

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Warehouse ID:** {selected_warehouse['Warehouse ID']}"
            )
            st.write(
                f"**Warehouse Name:** {selected_warehouse['Warehouse Name']}"
            )

        with col2:
            st.write(
                f"**Type:** {selected_warehouse['Type']}"
            )
            st.write(
                f"**Location:** {selected_warehouse['Location']}"
            )
            st.write(
                f"**Status:** {selected_warehouse['Status']}"
            )


# =========================================================
# COURIERS
# =========================================================

elif page == "Couriers":

    st.title("🚚 Courier Management")

    st.write(
        "Manage courier partners, delivery services, pickup schedules and shipping costs."
    )

    st.divider()

    # -----------------------------
    # METRICS
    # -----------------------------

    total_couriers = len(couriers)

    express_couriers = len(
        couriers[
            couriers["Service Type"]
            .astype(str)
            .str.lower()
            .eq("express")
        ]
    )

    standard_couriers = len(
        couriers[
            couriers["Service Type"]
            .astype(str)
            .str.lower()
            .eq("standard")
        ]
    )

    avg_base_cost = couriers["Base Cost"].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Couriers",
            total_couriers
        )

    with col2:
        st.metric(
            "Express Couriers",
            express_couriers
        )

    with col3:
        st.metric(
            "Standard Couriers",
            standard_couriers
        )

    with col4:
        st.metric(
            "Avg. Base Cost",
            f"₹{avg_base_cost:,.0f}"
        )

    st.divider()

    # -----------------------------
    # FILTERS
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:

        courier_search = st.text_input(
            "🔎 Search Courier",
            placeholder="Search courier..."
        )

    with col2:

        service_type_options = ["All"] + sorted(
            couriers["Service Type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        service_type_filter = st.selectbox(
            "Service Type",
            service_type_options
        )

    filtered_couriers = couriers.copy()

    if courier_search:

        search_text = courier_search.lower()

        filtered_couriers = filtered_couriers[
            filtered_couriers["Courier"]
            .astype(str)
            .str.lower()
            .str.contains(search_text, na=False)
        ]

    if service_type_filter != "All":

        filtered_couriers = filtered_couriers[
            filtered_couriers["Service Type"]
            == service_type_filter
        ]

    st.subheader("🚚 Courier Directory")

    st.dataframe(
        filtered_couriers,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------
    # COURIER DETAILS
    # -----------------------------

    if len(filtered_couriers) > 0:

        selected_courier = st.selectbox(
            "Select Courier",
            filtered_couriers["Courier"].tolist()
        )

        selected_courier_data = filtered_couriers[
            filtered_couriers["Courier"]
            == selected_courier
        ].iloc[0]

        st.subheader("📄 Courier Details")

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                f"**Courier ID:** {selected_courier_data['Courier ID']}"
            )
            st.write(
                f"**Courier:** {selected_courier_data['Courier']}"
            )
            st.write(
                f"**Service Type:** {selected_courier_data['Service Type']}"
            )

        with col2:
            st.write(
                f"**Typical Delivery:** {selected_courier_data['Typical Delivery']}"
            )
            st.write(
                f"**Pickup Time:** {selected_courier_data['Pickup Time']}"
            )
            st.write(
                f"**Base Cost:** ₹{selected_courier_data['Base Cost']}"
            )

# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer-text">
        Fulfillment Hub • Order & Warehouse Operations Management System
    </div>
    """,
    unsafe_allow_html=True
)