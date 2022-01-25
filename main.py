from fastapi import FastAPI

app = FastAPI()


@app.get('/products')
def all_products():
    return 'these are all the products'
