'''
todo: 
login() log users in
logout() log out user logged in

place_order() allow reseller to place an order // use new_order.user_email = current_user.email to assign the current user as owner
track_orders() view and track their own orders // user_orders = Order.query.filter_by(user_email=current_user.email).all() will be useful :D

view_all_orders() view all orders placed by all resellers
update_order_status() change the status of any order (admin only) (possibly a button on the view all orders screen)

update_product_catalog() update product details (bonus) (admin only)
add_product() add a new product to the catalog (bonus) (admin only)
home() landing page or dashboard (depending on who's logged in) // button to go back to the respective home page based on user
'''
