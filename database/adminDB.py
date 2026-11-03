
from database.connection import DatabaseConnction


class AdminQueries:
    @staticmethod
    def insertProductRecord(product_data:tuple[str|int]):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """insert into products(productname, description, category, quantity, 
                        saleprice, imgname, storedpath)
                        values(%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query,product_data)
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Product Added"
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.insertProductRecord:{e}"


    # get all products
    @staticmethod
    def getAllProducts(productname:str=None, category:str=None, product_id:int=None):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """select * from products where 1=1"""
            values = []
            if productname:
                query += " and productname like %s"
                values.append(f"%{productname}%")
            if category:
                query += " and category = %s"
                values.append(category)
            if product_id is not None:
                query += " and productid = %s"
                cursor.execute(query, (product_id,))
                product = cursor.fetchone()
                cursor.close()
                db_config.close()
                return True, product

            cursor.execute(query,values)
            products = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, products
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllProducts:{e}"


    @staticmethod
    def updateProductRecord(product_data:tuple[str|int]):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """update products set productname =%s, description=%s,
                         category = %s, quantity=%s, 
                        saleprice=%s, imgname=%s, storedpath=%s
                        where productid = %s"""
            cursor.execute(query,product_data)
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Product Updated"
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.updateProductRecord:{e}"


    # get all categories 
    @staticmethod
    def getAllCategories():
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            query = """select distinct category from products"""
            cursor.execute(query)
            categories = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, categories
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllCategories:{e}"
    # get users data
    @staticmethod
    def getAllUsers():
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """select * from users"""
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, users
        except Exception as e:
            return False, f"Something wrong in database/adminDB.AdminQueries.getAllUsers:{e}"

    # Get All Orders 
    @staticmethod
    def getAllOrders():
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """
                SELECT
                    o.orderid,
                    o.userid,
                    o.status,
                    o.address,
                    o.created_at,

                    u.username AS customer_name,
                    u.email AS customer_email,

                    COALESCE((
                        SELECT SUM(od.quantity)
                        FROM order_details od
                        WHERE od.orderid = o.orderid
                    ), 0) AS item_count,

                    COALESCE((
                        SELECT SUM(od.quantity * od.price)
                        FROM order_details od
                        WHERE od.orderid = o.orderid
                    ), 0) AS total_amount,

                    COALESCE((
                        SELECT UPPER(p.status::text)
                        FROM payments p
                        WHERE p.orderid = o.orderid
                        ORDER BY p.paymentid DESC
                        LIMIT 1
                    ), 'PENDING') AS payment_status

                FROM orders o

                LEFT JOIN users u
                    ON u.userid = o.userid

                ORDER BY o.created_at DESC
            """

            cursor.execute(query)
            orders = cursor.fetchall()

            return True, orders

        except Exception as e:
            return False, f"getAllOrders error: {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()

    # Get Dashboard order Data
    @staticmethod
    def getDashboardOrderData():
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            # Total orders
            cursor.execute("""
                SELECT COUNT(*) AS total_orders
                FROM orders
            """)

            total_orders = cursor.fetchone()["total_orders"]

            # Orders created during the last 7 days
            cursor.execute("""
                SELECT COUNT(*) AS recent_count
                FROM orders
                WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
            """)

            recent_count = cursor.fetchone()["recent_count"]

            # Latest 5 orders
            cursor.execute("""
                SELECT
                    o.orderid,
                    o.status,
                    o.created_at,
                    u.username AS customer_name,

                    COALESCE((
                        SELECT SUM(od.quantity * od.price)
                        FROM order_details od
                        WHERE od.orderid = o.orderid
                    ), 0) AS total_amount

                FROM orders o

                LEFT JOIN users u
                    ON u.userid = o.userid

                ORDER BY o.created_at DESC
                LIMIT 5
            """)

            recent_orders = cursor.fetchall()

            return True, {
                "total_orders": total_orders,
                "recent_count": recent_count,
                "recent_orders": recent_orders
            }

        except Exception as e:
            return False, f"Dashboard order query error: {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()

    #   
    @staticmethod
    def getOrderDetails(order_id):

        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            # Get order and customer information
            cursor.execute("""
                SELECT
                    o.orderid,
                    o.userid,
                    o.status,
                    o.address,
                    o.created_at,

                    u.username AS customer_name,
                    u.email AS customer_email,
                    u.phone AS customer_phone,

                    COALESCE((
                        SELECT p.method::text
                        FROM payments p
                        WHERE p.orderid = o.orderid
                        ORDER BY p.paymentid DESC
                        LIMIT 1
                    ), 'N/A') AS payment_method,

                    COALESCE((
                        SELECT UPPER(p.status::text)
                        FROM payments p
                        WHERE p.orderid = o.orderid
                        ORDER BY p.paymentid DESC
                        LIMIT 1
                    ), 'PENDING') AS payment_status,

                    COALESCE((
                        SELECT SUM(od.quantity * od.price)
                        FROM order_details od
                        WHERE od.orderid = o.orderid
                    ), 0) AS total_amount

                FROM orders o

                LEFT JOIN users u
                    ON u.userid = o.userid

                WHERE o.orderid = %s

                LIMIT 1
            """, (order_id,))

            order = cursor.fetchone()

            if not order:
                return False, "Order not found"

            # Get individual products
            cursor.execute("""
                SELECT
                    od.productid,
                    od.quantity,
                    od.price,

                    (od.quantity * od.price) AS subtotal,

                    p.productname,
                    p.imgname,
                    p.storedpath

                FROM order_details od

                LEFT JOIN products p
                    ON p.productid = od.productid

                WHERE od.orderid = %s
            """, (order_id,))

            order_items = cursor.fetchall()

            return True, {
                "order": order,
                "items": order_items
            }

        except Exception as e:
            return False, f"getOrderDetails error: {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()


    @staticmethod
    def updateOrderStatus(order_id, new_status):

        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()

            cursor.execute(
                "SELECT orderid FROM orders WHERE orderid = %s",
                (order_id,)
            )

            if not cursor.fetchone():
                return False, "Order not found."

            cursor.execute("""
                UPDATE orders
                SET status = %s::order_status
                WHERE orderid = %s
            """, (new_status, order_id))

            db_config.commit()

            return True, "Delivery status updated successfully."

        except Exception as e:
            if db_config:
                db_config.rollback()

            return False, f"updateOrderStatus error: {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()

    
    @staticmethod
    def getOrderInvoice(order_id, user_id=None):

        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            # Restrict customers to their own orders.
            # Admins can retrieve any order.
            if user_id is None:
                where_clause = "WHERE o.orderid = %s"
                params = (order_id,)
            else:
                where_clause = """
                    WHERE o.orderid = %s
                    AND o.userid = %s
                """
                params = (order_id, user_id)

            cursor.execute(f"""
                SELECT
                    o.orderid,
                    o.userid,
                    o.status AS order_status,
                    o.address,
                    o.created_at,

                    u.username AS customer_name,
                    u.email AS customer_email,
                    u.phone AS customer_phone,

                    p.method AS payment_method,
                    p.status AS payment_status,
                    p.razorpay_payment_id,
                    p.amount AS total_amount,
                    p.created_at AS payment_date

                FROM orders o

                LEFT JOIN users u
                    ON u.userid = o.userid

                LEFT JOIN payments p
                    ON p.orderid = o.orderid

                {where_clause}

                ORDER BY p.paymentid DESC
                LIMIT 1
            """, params)

            order = cursor.fetchone()

            if not order:
                return False, "Order not found."

            cursor.execute("""
                SELECT
                    od.productid,
                    od.quantity,
                    od.price,
                    (od.quantity * od.price) AS subtotal,
                    p.productname

                FROM order_details od

                LEFT JOIN products p
                    ON p.productid = od.productid

                WHERE od.orderid = %s
            """, (order_id,))

            items = cursor.fetchall()

            order["invoice_number"] = f"SZ-{order_id:06d}"

            if order["payment_method"] == "cash":
                order["payment_method_label"] = "Cash on Delivery"
                order["payment_status_label"] = "Pay on Delivery"
            else:
                order["payment_method_label"] = "Online Payment"
                order["payment_status_label"] = (
                    str(order["payment_status"] or "pending").upper()
                )

            return True, {
                "order": order,
                "items": items
            }

        except Exception as e:
            return False, f"getOrderInvoice error: {e}"

        finally:
            if cursor:
                cursor.close()

            if db_config:
                db_config.close()
