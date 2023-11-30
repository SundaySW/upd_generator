class AddrData:
    def __init__(self, data: list):
        self.all_data = {"КодРегион":   data[0],
                         "Индекс":      data[1],
                         "Город":       data[2],
                         "Район":       data[3],
                         "НаселПункт":  data[4],
                         "НетЗнач":     data[5],
                         "Улица":       data[6],
                         "Дом":         data[7],
                         "Корпус":      data[8],
                         "Кварт":       data[9]}

    def get_data(self):
        return {k: v for k, v in self.all_data.items() if v}
