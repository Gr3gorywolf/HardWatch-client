class NotExposedApi:
    def notExposedMethod(self):
        return 'This method is not exposed'

class JsApi:
    json_data: dict = None
    on_save: callable = None
    def __init__(self, json_data:dict, on_save: callable = None):
        self.json_data = json_data
        self.on_save = on_save

    def getData(self):
        return {"data": self.json_data}

    def saveData(self, data:dict):
        self.on_save(data)
        return {"data": self.json_data}