import time

from pyadbautomator_package.pyadbautomator import PyAdbAutomator

def get(email, password):
    try:
        adb = PyAdbAutomator('com.picpay', 5)
        adb.open()
        label_name = adb.first('resource-id', 'com.picpay:id/balanceMainFeedHeader')
        print(label_name)
        if label_name is not None:
            label_name.click()
            result = {
                'transactions': [],
                'cards': [],
                'cdb': float(adb.first('resource-id', 'com.picpay:id/textBalance').get_attr('text').replace('R$ ', '').replace('.', '').replace(',', '.'))
            }
            adb.close()
            return result
        else:
            #precisa de autorização de dispositivo
            pass
    except:
        pass
    try:
        button_inicio = adb.first('text', 'Início')
        button_inicio.click()
    except:
        pass
    adb.close()