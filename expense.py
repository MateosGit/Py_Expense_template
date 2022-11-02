from PyInquirer import prompt
import json
from utils import read_json_file, write_json_file

EXPENSES_DATA_FILE = "expenses.json"
USERS_DATA_FILE = "users.json"
STATUS_DATA_FILE = "status.json"

expenses_data = read_json_file(EXPENSES_DATA_FILE)

def hot_reload_users_list():
    return [user['name'] for user in list(read_json_file(USERS_DATA_FILE).values())]

def hot_reload_users_checkbox():
    return [{"name": user['name']} for user in list(read_json_file(USERS_DATA_FILE).values())]

expense_questions = [
    {
        "type": "input",
        "name": "amount",
        "message": "New Expense - Amount: ",
        'validate': lambda val: len(val) > 0 and val.isdigit()
    },
    {
        "type": "input",
        "name": "label",
        "message": "New Expense - Label: ",
        'validate': lambda val: len(val) > 0
    },
    {
        "type": "list",
        "name": "spender",
        "message": "New Expense - Spender: ",
        "choices": []
    },
    {
        'type': 'checkbox',
        'qmark': '😃',
        'message': 'New Expense - Involved User: ',
        'name': 'involved_users',
        'choices': []
    },

]

def new_expense(*args):
    if len(list(read_json_file(USERS_DATA_FILE).values())) <= 1:
        print("You need to add more than 1 users to access this feature")
        return False
    
    # Reloading user list in case of new user appeared
    expense_questions[2]['choices'] = hot_reload_users_list()
    expense_questions[3]['choices'] = hot_reload_users_checkbox()
    
    infos = prompt(expense_questions)
    
    if (infos['spender'] in infos['involved_users']):
        infos['involved_users'].pop(infos['involved_users'].index(infos['spender']))
        print("Spender removed from involved user list as he's already involved.")
        
    expenses_data["expenses"].append(infos)
    write_json_file(EXPENSES_DATA_FILE, expenses_data)
    
    return True

def dump_status(status):
    users = [user['name'] for user in list(read_json_file(USERS_DATA_FILE).values())]
    for user in users:
        debt_list = status.get(user)
        if debt_list is None:
            print(f'{user} owes nothing')
        else:
            for other_user in list(debt_list.keys()):
                spec_user = debt_list.get(other_user)
                paid = ("PAID" if spec_user.get('paid')else "NOT PAID")
                amount = spec_user.get('amount')
                print(f'{user} owes {amount} to {other_user} {paid}')

def balance_status(status):
    for user in list(status.keys()):
        debt_list = status.get(user)
        for other_user in list(debt_list.keys()):
            debt = debt_list.get(other_user)
            
            other_user_debt = status.get(other_user)
            if other_user_debt is None:
                break
            
            other_user_debt_to_current = other_user_debt.get(user)
            if other_user_debt_to_current is None:
                break
            print(debt['amount'])
            print(other_user_debt_to_current.get('amount'))
            if debt['amount'] == 0 or other_user_debt_to_current.get('amount') == 0:
                break
            
            count = debt['amount'] - other_user_debt_to_current.get('amount')
            
            if count < 0: 
                debt['amount'] = 0
                other_user_debt_to_current['amount'] += count
            elif count > 0:
                debt['amount'] -= count
                other_user_debt_to_current['amount'] = 0
            if count == 0:
                debt['amount'] = 0
                other_user_debt_to_current['amount'] = 0
    
    return status
def compute_status(*args):
    '''
    Building a dict of status
    if a owes 30 to b and 40 to c
    b owes 10 to c we gonna have
    {
        a : { 
            b : {amount: 30, paid: False},
            c : {amount: 40, paid: False},
        },
        b : { 
            c : {amount: 10, paid: False}
        }
    }
    '''
    status = {}
    for expense in expenses_data['expenses']:
        for involved in expense.get('involved_users'):
            current_status = status.get(involved) 
            if current_status is None:
                status[involved] = { expense['spender']: {"amount": int(expense['amount']) / (len(expense['involved_users']) + 1), "paid": False} }
            else:
                debt = current_status.get(expense['spender'])
                print(debt)
                if debt is None:
                    current_status[expense.spender] = {"amount": int(expense['amount']) / (len(expense['involved_users']) + 1), "paid" : False}
                else:
                    debt['amount'] += int(expense['amount']) / (len(expense['involved_users']) + 1)
    
    
    status = balance_status(status)
    
    dump_status(status)
    return True
        