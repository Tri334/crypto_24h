modal_usdt = 500 
modal_rupiah = modal_usdt*16000
# Formatting the values
modal_usdt = f"$ {modal_usdt:,.2f}"
modal_rupiah = f"Rp {modal_rupiah:,.2f}".replace(".", ",", 1)

print(f'Modal : {modal_usdt}')
print(f'Modal Rupiah: {modal_rupiah}')


