from database.connection import DatabaseConnction
from decimal import Decimal, ROUND_HALF_UP

class UserQueries:
    @staticmethod
    def addToCart(product_id, user_id, quantity):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor()
            query = """update cart set quantity = quantity + %s 
                        where productid = %s and userid = %s"""
            cursor.execute(query, (quantity, product_id, user_id))
            if cursor.rowcount:
                db_config.commit()
                cursor.close()
                db_config.close()
                return True, "Item Added to Cart"
            query = """insert into cart(productid, userid, quantity) values(%s, %s, %s)"""
            cursor.execute(query, (product_id, user_id, quantity))
            db_config.commit()
            cursor.close()
            db_config.close()
            return True, "Item Added to Cart"
        except Exception as e:
            return False, f"Something wrong in database/userDB.UserQueries.addToCart():{e}"
            

    # get cart items
    @staticmethod
    def cartItems(user_id):
        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)
            query = """select c.cartid, p.productid, p.productname, p.category, p.saleprice,
                                c.quantity, p.storedpath,p.quantity as stock, 
                                (c.quantity * p.saleprice) as subtotal
                                from products p
                                inner join cart c
                                on c.productid = p.productid
                                where c.userid = %s"""
            cursor.execute(query, (user_id, ))
            
            items = cursor.fetchall()
            cursor.close()
            db_config.close()
            return True, items
        except Exception as e:
            return False, f"Something wrong in database/userDB.UserQueries.cartItems():{e}"
            


    # create order
        
    @staticmethod
    def createOrder(userid: int, address: str, payment_method: str,
                    razorpay_order_id: str = None,
                    razorpay_payment_id: str = None):
        db_config = None
        cursor = None

        try:
            db_config = DatabaseConnction()
            cursor = db_config.cursor(dictionary=True)

            query = """
                SELECT c.cartid, c.userid, c.quantity,
                    p.productname, p.productid,
                    p.quantity AS stock, p.saleprice
                FROM cart c
                JOIN products p ON c.productid = p.productid
                WHERE c.userid = %s
                FOR UPDATE
            """
            cursor.execute(query, (userid,))
            items = cursor.fetchall()

            if not items:
                return False, "Cart is empty"

            sub_total = Decimal("0.00")

            # Validate stock and calculate subtotal
            for item in items:
                if item['quantity'] > item['stock']:
                    raise ValueError(
                        f"{item['productname']}: only {item['stock']} items available"
                    )

                price = Decimal(str(item['saleprice']))
                sub_total += Decimal(str(item['quantity'])) * price

            # Calculate shipping at 1%
            shipping = (sub_total * Decimal("0.01")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            total = sub_total + shipping

            # Create order
            query = """
    INSERT INTO orders(userid, status, address)
    VALUES(%s, %s::order_status, %s)
    RETURNING orderid
            """
            cursor.execute(query, (userid, "pending", address))
            orderid = cursor.fetchone()["orderid"]

            # Create order details and reduce stock
            for item in items:
                query = """
                    INSERT INTO order_details(orderid, productid, quantity, price)
                    VALUES(%s, %s, %s, %s)
                """
                cursor.execute(
                    query,
                    (orderid, item['productid'],
                    item['quantity'], item['saleprice'])
                )

                query = """
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE productid = %s
                """
                cursor.execute(
                    query, (item['quantity'], item['productid'])
                )

            
            # Create payment record
            payment_status = "pending"
            method = "cash" if payment_method == "COD" else "upi"

            query = """
    INSERT INTO payments (
        userid,
        orderid,
        method,
        amount,
        status,
        razorpay_order_id,
        razorpay_payment_id
    )
    VALUES (
        %s, %s, %s::payment_method, %s,
        %s::payment_status, %s, %s
    )
"""

            cursor.execute(
                query,
                (
                    userid,
                    orderid,
                    method,
                    total,
                    payment_status,
                    razorpay_order_id,
                    razorpay_payment_id
                )
            )
            
            # Clear cart after successful order creation
            cursor.execute(
                "DELETE FROM cart WHERE userid = %s",
                (userid,)
            )

            db_config.commit()

            return True, {
                "order_id": orderid,
                "amount": total
            }

        except Exception as e:
            if db_config:
                db_config.rollback()

            return False, (
                f"Something wrong in database/userDB.py/"
                f"UserQueries.createOrder(): {e}"
            )

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()
