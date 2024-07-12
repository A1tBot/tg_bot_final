import firebase_admin
from firebase_admin import db, credentials
from config import SERVICE_ACCOUNT_KEY_PATH, DATABASE_URL, DATABASE_ROOT

credentials = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
firebase_admin.initialize_app(credentials, {'databaseURL': DATABASE_URL})

async def writeData(path, data):
    reference = db.reference(path=path)
    reference.push().set(data)

async def updateData(path, child, data):
    reference = db.reference(path=path)
    childToUpdate = reference.child(child)
    childToUpdate.update(data)

async def formatData(data):
    tgUser = {
        'id': data['id'],
        'fName': data['fName'],
        'lName': data['lName'],
        'pType': data['pType'],
        'pAge': data['pAge'],
        'languages': data['languages'],
        'levels': data['levels'],
        'purpose': data['purpose'],
        'phone': data['phone'],
        'date': data['date'],
    }

    reference = db.reference(DATABASE_ROOT)
    users = reference.get()
    for i in users:
        if users[i]['id'] == tgUser['id'] and users[i]['pType'] == tgUser['pType']:
            print(f'LOG: User {tgUser["id"]} firebase data UPDATED')
            return await updateData(DATABASE_ROOT, str(i), tgUser)
    print(f'LOG: User {tgUser["id"]} firebase data ADDED')
    return await writeData(DATABASE_ROOT, tgUser)
    