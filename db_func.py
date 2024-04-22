import pymongo

client = pymongo.MongoClient('mongodb+srv://admin:admin@garnet.hotoadz.mongodb.net/')

db = client['aps5_db']

counter = db.counters.find_one()

usuario_id = counter['usuarios_id']
bicicletas_id = counter['bicicletas_id']
emprestimos_id = counter['emprestimos_id']

#create user
def user_add(nome, cpf, data):
  if nome and cpf and data:
    user = db.usuarios.find_one({'CPF':cpf})
    if user == None:
      dic = {
        'id': usuario_id,
        'nome': nome,
        'CPF': cpf,
        'data': data,
        'emprestimos':[]
      }
      db.counters.update_one({}, {'$inc':{'usuarios_id':1}})
      db.usuarios.insert_one(dic)
      return {'resp':'Usuario cadastrado com sucesso!', 'status_code': 201}
    return {'resp':'Erro: Usuario já existe!', 'status_code': 400}
  else:
    return {'resp':'Erro: Todos os campos são obrigatorios!', 'status_code': 400}

#read one user
def user_find(id=None):
  '''
  retorna: {'_id': ObjectId('xxx'), 'id': 1, 'nome': 'exemplo', 'CPF': '123', 'data': '00/00/0000'}
  caso o id não existir no DB, retorna: 'Erro: Usuario não encontrado / não existe'
  '''
  if id == None:
    return {'resp': list(db.usuarios.find()), 'status_code': 200}
  else:
    user = db.usuarios.find_one({'id': id})
    if user == None:
      return {'resp': f'Erro: Usuario <{id}> não existe', 'status_code': 404}
    return {'resp': user, 'status_code': 200}

#update user
def user_update(id, dic):
  user = user_find(id)
  if not isinstance(user, str):
    for key in dic.keys():
      db.usuarios.update_one({'id':id}, {'$set': {key:dic[key]}})
    return {'resp': f'Usuario <{id}> editado com sucesso', 'status_code': 200}
  return {'resp': f'Erro: Usuario <{id}> não existe', 'status_code': 404}

#delete user
def user_delete(id):
  user = user_find(id)
  if not isinstance(user, str):
    db.usuarios.delete_one({'id':id})
    return {'resp': f'Usuario <{id}> deletado com sucesso', 'status_code': 200}
  return {'resp': f'Erro: Usuario <{id}> não existe', 'status_code': 404}

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

#create bike
def bike_add(marca, modelo, cidade):
  if marca and modelo and cidade:
    dic = {
      'id': bicicletas_id,
      'marca': marca,
      'modelo': modelo,
      'cidade': cidade,
      'status': 'disponivel',
      'emprestimo': []
    }
    db.counters.update_one({}, {'$inc':{'bicicletas_id':1}})
    db.bicicletas.insert_one(dic)
    return {'resp': 'Bicicleta cadastrada com sucesso!', 'status_code': 201}
  else:
    return {'resp': 'Erro: Todos os campos são obrigatorios!', 'status_code': 400}
  
#read one bike or all
def bike_find(id=None):
  '''
  retorna: {'_id': ObjectId('xxx'), 'id': 1, 'marca': 'exemplo', 'modelo': 'speed', 'cidade': 'sp'}
  caso o id não existir no DB, retorna: 'Erro: bicicleta não encontrada / não existe'
  caso a funcao seja chamada sem nenhum argumento, devolvera TODAS as bicicletas
  '''
  if id == None:
    return {'resp': list(db.bicicletas.find()), 'status_code': 200}
  else:
    bike = db.bicicletas.find_one({'id': id})
    if bike == None:
      return {'resp': f'Erro: Bicicleta <{id}> não existe', 'status_code': 404}
    return {'resp': bike, 'status_code': 200}
    
#update bike
def bike_update(id, dic):
  bike = bike_find(id)
  if not isinstance(bike, str):
    for key in dic.keys():
      db.bicicletas.update_one({'id':id}, {'$set': {key:dic[key]}})
    return {'resp': f'Bicicleta <{id}> editada com sucesso', 'status_code': 200}
  return {'resp': f'Erro: Bicicleta <{id}> não existe', 'status_code': 404}

#delete bike
def bike_delete(id):
  bike = bike_find(id)
  if not isinstance(bike, str):
    db.bicicleta.delete_one({'id':id})
    return {'resp': f'Bicicleta <{id}> deletada com sucesso', 'status_code': 200}
  return {'resp': f'Erro: Bicicleta <{id}> não existe', 'status_code': 404}

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

#create emprestimo
def emp_add(user_id, bike_id, inicio, devolucao='em aberto'):
  if user_id and bike_id and inicio:
    bike = bike_find(bike_id)
    user = user_find(user_id)
    if bike['resp']['status'] == 'disponivel' and not isinstance(user['resp'], str):
      dic = {
        'id': emprestimos_id,
        'usuario_id': user_id,
        'bicicleta_id': bike_id,
        'inicio': inicio,
        'devolucao': devolucao,
        'status': 'ativo'
      }

      dic_user = {
        'id': emprestimos_id,
        'bicicleta_id': bike_id,
        'inicio': inicio,
        'devolucao': devolucao
      }

      dic_bike = {
        'id': emprestimos_id,
        'usuario_id': usuario_id,
        'inicio': inicio,
        'devolucao': devolucao
      }

      db.counters.update_one({}, {'$inc':{'emprestimos_id':1}})
      db.emprestimos.insert_one(dic)
      db.bicicletas.update_one({'id': bike_id}, {'$set': {'status': 'Em uso'}})

      db.usuarios.update_one({'id': user_id}, {'$push': {'emprestimos': dic_user}})

      db.bicicletas.update_one({'id': bike_id}, {'$push': {'emprestimo': dic_bike}})

      return {'resp': 'Emprestimo cadastrado com sucesso!', 'status_code': 201}
    else:
      return {'resp': f'Bicicleta <{bike_id}> já está em uso!', 'status_code': 400}
  else:
    return {'resp': 'Erro: Todos os campos são obrigatorios!', 'status_code': 400}
  
#read one emp or all
def emp_find(id=None, status=''):
  '''
  retorna: {'_id': ObjectId('xxx'), 'id': 1, 'usuario_id': 1, 'bicicleta_id': 1, 'inicio': '01/01/2024', 'devolução': 'em aberto / 'dd/mm/aaaa'}
  caso o id não existir no DB, retorna: 'Erro: bicicleta não encontrada / não existe'
  para ver TODOS os emprestimos passe o SEGUNDO argumento como 'all' => emp_find(, 'all') <=
  '''
  if id == None:
    if status == 'all':
      return {'resp': list(db.emprestimos.find()), 'status_code': 200}
    else:
      return {'resp': list(db.emprestimos.find({'status': 'ativo'})), 'status_code': 200}
  else:
    emp = db.emprestimos.find_one({'id': id})
    if emp == None:
      return {'resp': f'Erro: Emprestimo <{id}> não existe', 'status_code': 404}
    return {'resp': emp, 'status_code': 200}
  
#read one emp user
def emp_user_find(id, status='ativos'):
  '''
  retorna os emprestimos do usuario (por default retorna so os emprestimos ativos) \n
  para obter TODOS os emprestimos que o usuario ja teve => emp_user_find(id, 'all') <=
  '''
  user = user_find(id)
  if user['status_code'] == 404:
    return user
  
  if list(db.emprestimos.find({'usuario_id': id})) == None:
    return {'resp': f'Nenhum emprestimo encontrado para o usuario <{id}>', 'status_code': 200}
  if status == 'ativos':
    emp_ativos = db.emprestimos.find({'$and': [{'usuario_id': id}, {'status': 'ativo'}]})
    return {'resp': emp_ativos, 'status_code': 200}
  all_emps = db.emprestimos.find({'usuario_id': id})
  return {'resp': all_emps, 'status_code': 200}

#read one emp bike
def emp_bike_find(id):
  bike = bike_find(id)
  if bike['status_code'] == 404:
    return bike
  
  emp = db.emprestimos.find_one({'bicicleta_id': id})
  if emp == None:
    return {'resp': f'Nenhum emprestimo encontrado para a bicicleta <{id}>', 'status_code': 200}
  return {'resp': emp, 'status_code': 200}

#update emp
def emp_update(id, dic):
  emp = emp_find(id)
  if not isinstance(emp, str):
    for key in dic.keys():
      db.emprestimos.update_one({'id':id}, {'$set': {key:dic[key]}})
    return {'resp': f'Emprestimo <{id}> editado com sucesso', 'status_code': 200}
  return {'resp': f'Erro: Emprestimo <{id}> não encontrado', 'status_code': 404}

#delete emp
def emp_delete(id):
  emp = emp_find(id)
  if not isinstance(emp['resp'], str):
    db.emprestimos.update_one({'id':id}, {'$set': {'status': 'inativo'}})
    db.bicicletas.update_one({'id': emp['resp']['bicicleta_id']}, {'$set': {'status': 'disponivel'}})
    db.usuarios.update_one({'id': emp['resp']['usuario_id']}, {'$pull': {'emprestimos': {'id': id}}})
    db.bicicletas.update_one({'id': emp['resp']['bicicleta_id']}, {'$pull': {'emprestimo': {'id': id}}})
    return {'resp': f'Emprestimo <{id}> deletado com sucesso', 'status_code': 200}
  return {'resp': f'Erro: Emprestimo <{id}> não existe', 'status_code': 404}
