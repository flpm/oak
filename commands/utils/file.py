"""
Convert the export files from the Bookshelf IOS app into a JSON file for archiving.
"""
import json

work_catalogue_filename = "./work/catalogue.json"
output_cover_folder = "./output/covers"
amazon_orders_filename = "./raw/amazon/amazon_orders.json"


def read_catalogue(file_name=work_catalogue_filename):
    try:
        with open(file_name, "r") as fp:
            result = json.load(fp)
    except FileNotFoundError:
        result = dict()
    return result


def save_catalogue(catalogue, file_name=work_catalogue_filename):
    with open(file_name, "w") as file:
        json.dump(catalogue, file)


def save_cover_image(image_data, file_name):
    with open(f"{output_cover_folder}/{file_name}", "wb") as file:
        file.write(image_data)


def read_amazon_orders():
    with open(amazon_orders_filename, "r") as fp:
        orders = json.load(fp)
    return orders
