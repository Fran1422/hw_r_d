import os
import json
import pandas as pd
data_path = 'file_storage\\json\\'
convert_data_path = 'file_storage\\csv\\'
for i in os.listdir(data_path):
    for j in os.listdir(data_path+i):
        with open(data_path+i+"\\"+j, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            if not os.path.exists((data_path+i).replace("json", "csv")):
                os.makedirs((data_path+i).replace("json", "csv"))
            pd.json_normalize(data).to_csv((data_path+i+"\\"+j).replace("json", "csv"), index=False, encoding='utf-8')