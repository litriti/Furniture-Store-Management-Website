def count_cart(cart):
    total_amount, total_quantity, total_product = 0, 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity']*c['price']
            total_product =len(cart)



    return {
        "total_amount": total_amount,
        "total_quantity": total_quantity,
        "total_product": total_product
    }


