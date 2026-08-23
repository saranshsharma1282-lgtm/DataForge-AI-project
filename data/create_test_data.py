import pandas as pd

data = [
    ["Frigidaire", "Frigidaire", "PDSH4816AF", "Stainless steel dishwasher 120V 15A, 5 wash cycles"],
    ["Samsung", "Samsung", "QN55Q80D", "55 inch 4K LED smart television, Wi-Fi enabled"],
    ["LG", "LG", "WM4000HWA", "Front load washing machine, 4.5 cu ft, white"],
    ["Whirlpool", "Whirlpool", "WRS588FIHZ", "25 cu ft side-by-side refrigerator, stainless steel"],
    ["Bosch", "Bosch", "SHX78CM5N", "24 inch built-in dishwasher, stainless steel, 120V"],
    ["Sony", "Sony", "XBR55X90L", "55 inch 4K HDR LED smart TV with Wi-Fi"],
    ["GE", "GE", "GDT650SYVFS", "Built-in dishwasher, stainless steel, 120V"],
    ["Haier", "Haier", "QLED65S9", "65 inch 4K QLED smart television"],
    ["Electrolux", "Electrolux", "ELFW7637AT", "Front load washer, 4.5 cu ft, titanium"],
    ["KitchenAid", "KitchenAid", "KDTM704KPS", "24 inch dishwasher, stainless steel, 120V"]
]

columns = [
    "Manufacturer",
    "Brand",
    "MPN",
    "Product Description"
]

df = pd.DataFrame(data, columns=columns)

df.to_excel("test_products.xlsx", index=False)

print("Excel file created successfully!")
print("Total products:", len(df))
