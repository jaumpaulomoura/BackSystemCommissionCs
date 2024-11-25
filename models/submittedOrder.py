from database import db

class SubmittedOrder(db.Model):
    __tablename__ = 'submitted_order'
    
    order_id = db.Column(db.String, primary_key=True)
    submitted_date = db.Column(db.Date)
    send_franchise_order_kpl = db.Column(db.Boolean)
    state = db.Column(db.String)
    occ_payload = db.Column(db.JSON)
    cs_shipping = db.Column(db.JSON)
    cs_pickup_in_store = db.Column(db.String)
    profile_id = db.Column(db.String)

    def __init__(self, order_id, submitted_date, send_franchise_order_kpl, state, occ_payload, cs_shipping, cs_pickup_in_store, profile_id):
        self.order_id = order_id
        self.submitted_date = submitted_date
        self.send_franchise_order_kpl = send_franchise_order_kpl
        self.state = state
        self.occ_payload = occ_payload
        self.cs_shipping = cs_shipping
        self.cs_pickup_in_store = cs_pickup_in_store
        self.profile_id = profile_id

    def to_dict(self):
        return {
            'pedido': self.order_id,
            'data_submissao': self.submitted_date,
            'mes': self.submitted_date.month,
            'ano': self.submitted_date.year,
            'hora_submissao': self.submitted_date.strftime('%H:%M:%S'),  
            'status': self.get_status(),
            'total_itens': self.get_total_items(),
            'envio': self.get_shipping_method(),
            'idloja': self.get_store_id(),
            'site': self.get_site(),
            'valor_bruto': self.get_raw_subtotal(),  
            'valor_desconto': self.get_valor_desconto(),
            'valor_frete': self.get_valor_frete(),
            'valor_pago': self.get_valor_pago(),
            'cupom': self.get_coupon_code(),
            'cupom_vendedora': self.get_seller_coupon_code(),
            'metodo_pagamento': self.get_payment_method(),
            'id_cliente': self.profile_id
        }


    def get_payment_method(self):
        payment_groups = self.occ_payload.get('order', {}).get('paymentGroups', [])
        if not payment_groups:
            return 'UNKNOWN'
        
        payment_method = payment_groups[0].get('paymentMethod', 'UNKNOWN')
        if payment_method == 'creditCard':
            return 'CARTAO DE CREDITO'
        elif payment_method == 'invoiceRequest':
            return 'BOLETO'
        elif payment_method == 'cash':
            return 'PIX'
        else:
            return payment_method

    def get_shipping_method(self):
        shipping_groups = self.occ_payload.get('order', {}).get('shippingGroups', [])
        if not shipping_groups:
            return 'UNKNOWN'
        
        shipping_method = shipping_groups[0].get('shippingMethod', 'UNKNOWN')
        if shipping_method == 'economic':
            return 'ECONOMICO'
        elif shipping_method == 'fast':
            return 'RAPIDO'
        elif shipping_method == '700001':
            return 'RETIRADA EM LOJA'
        else:
            return shipping_method.upper()
    
    def get_status(self):
        if self.send_franchise_order_kpl in [True, False]:
            return 'PRE-VENDA'
        
        state_map = {
            'APPROVED': 'APROVADO',
            'FAILED_APPROVAL': 'NAO AUTORIZADO',
            'REMOVED': 'CANCELADO',
            'PROCESSING': 'PENDENTE',
            'PENDING_PAYMENT': 'PENDENTE'
        }
        
        return state_map.get(self.state, self.state)

    def get_store_id(self):
        if self.cs_shipping:
            shipping_info = self.cs_shipping.get('shipping', [])
            if shipping_info and len(shipping_info) > 0:
                store_id = shipping_info[0].get('storeId', '')
                if store_id:
                    return store_id
        
        if self.cs_pickup_in_store:
            return self.cs_pickup_in_store
        
        return None

    def get_coupon_code(self):
        commerce_items = self.occ_payload.get('order', {}).get('commerceItems', [])
        for item in commerce_items:
            price_info = item.get('priceInfo', {})
            order_discount_infos = price_info.get('orderDiscountInfos', [])
            if order_discount_infos:
                coupon_codes = order_discount_infos[0].get('couponCodes', [])
                if coupon_codes: 
                    return coupon_codes[0]
        return None

    def get_seller_coupon_code(self):
        commerce_items = self.occ_payload.get('order', {}).get('commerceItems', [])
        for item in commerce_items:
            price_info = item.get('priceInfo', {})
            item_discount_infos = price_info.get('itemDiscountInfos', [])
            if item_discount_infos:
                coupon_codes = item_discount_infos[0].get('couponCodes', [])
                if coupon_codes: 
                    return coupon_codes[0]
        return None

    def get_parcelas(self):
        card_installments = self.occ_payload.get('order', {}).get('cardInstallments', '')
        if not card_installments or card_installments not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']:
            return '1'
        return card_installments
    def get_site(self):
        site_name = self.occ_payload.get('site', {}).get('siteName', '')
        return site_name.upper()

    def get_valor_desconto(self):
        discount_amount = self.occ_payload.get('order', {}).get('priceInfo', {}).get('discountAmount', '')
        if isinstance(discount_amount, str):
            return discount_amount.replace('.', ',')
        return discount_amount

    def get_valor_frete(self):
        shipping = self.occ_payload.get('order', {}).get('priceInfo', {}).get('shipping', '')
        if isinstance(shipping, str):
            return shipping.replace('.', ',')
        return shipping

    def get_valor_pago(self):
        total = self.occ_payload.get('order', {}).get('priceInfo', {}).get('total', '')
        if isinstance(total, str):
            return total.replace('.', ',')
        return total
    def get_total_items(self):
        total_items = self.occ_payload.get('order', {}).get('totalCommerceItemCount', '')
        return total_items
    def get_valor_total(self):
        return float(self.occ_payload.get('order', {}).get('priceInfo', {}).get('total', 0))
    def get_raw_subtotal(self):
        raw_subtotal = self.occ_payload.get('order', {}).get('priceInfo', {}).get('rawSubtotal', '')
        if isinstance(raw_subtotal, str):
            return raw_subtotal.replace('.', ',')
        return raw_subtotal
    