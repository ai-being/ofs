import xlrd

class ExcelToMap:

    def __init__(self, file_name):
        self.file_name = file_name

    def get_dict(self):
        print("Getting values..")
        workbook = xlrd.open_workbook(self.file_name)
        worksheet = workbook.sheet_by_index(0)
        keys = [i.value for i in worksheet.row(0)]
        data = list()
        for i in range(1, worksheet.nrows):
            values = worksheet.row(i)
            payload = dict()
            for key, value in zip(keys, values):
                payload[key] = value.value
            data.append(payload)
        return data


if __name__ == "__main__":
    excel_map = ExcelToMap("cus.xlsx")
    data = excel_map.get_dict()
    for i in data:
        print(i)