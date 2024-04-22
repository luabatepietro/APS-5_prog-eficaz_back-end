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
        'data': data
      }
      db.counters.update_one({}, {'$inc':{'usuarios_id':1}})
      db.usuarios.insert_one(dic)
      return 'Usuario cadastrado com sucesso!'
    return 'Erro: Usuario já existe!'
  else:
    return 'Erro: Todos os campos são obrigatorios!'

#read one user
def user_find(id):
  '''
  retorna: {'_id': ObjectId('xxx'), 'id': 1, 'nome': 'exemplo', 'CPF': '123', 'data': '00/00/0000'}
  caso o id não existir no DB, retorna: 'Erro: Usuario não encontrado / não existe'
  '''
  user = db.usuarios.find_one({'id': id})
  if user == None:
    return 'Erro: Usuario não encontrado / não existe'
  return user

#update user
def user_update(id, dic):
  user = user_find(id)
  if not isinstance(user, str):
    for key in dic.keys():
      db.usuarios.update_one({'id':id}, {'$set': {key:dic[key]}})
    return f'Usuario <{id}> editado com sucesso'
  return 'Erro: Usuario não encontrado / não existe'

#delete user
def user_delete(id):
  user = user_find(id)
  if not isinstance(user, str):
    db.usuarios.delete_one({'id':id})
    return f'Usuario <{id}> deletado com sucesso'
  return 'Erro: Usuario não encontrado / não existe'

#read all users
def user_all():
  users = db.usuarios.find()
  return list(users)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

#create bike
def bike_add(marca, modelo, cidade):
  if marca and modelo and cidade:
    dic = {
      'id': bicicletas_id,
      'marca': marca,
      'modelo': modelo,
      'cidade': cidade,
      'status': 'disponivel'
    }
    db.counters.update_one({}, {'$inc':{'bicicletas_id':1}})
    db.bicicletas.insert_one(dic)
    return 'Bicicleta cadastrada com sucesso!'
  else:
    return 'Erro: Todos os campos são obrigatorios!'
  
#read one bike
def bike_find(id):
  '''
  retorna: {'_id': ObjectId('xxx'), 'id': 1, 'marca': 'exemplo', 'modelo': 'speed', 'cidade': 'sp'}
  caso o id não existir no DB, retorna: 'Erro: bicicleta não encontrada / não existe'
  '''
  bike = db.bicicletas.find_one({'id': id})
  if bike == None:
    return 'Erro: Bicicleta não encontrada / não existe'
  return bike
    
#update bike
def bike_update(id, dic):
  bike = bike_find(id)
  if not isinstance(bike, str):
    for key in dic.keys():
      db.bicicletas.update_one({'id':id}, {'$set': {key:dic[key]}})
    return f'Bicicleta <{id}> editada com sucesso'
  return 'Erro: Bicicleta não encontrada / não existe'

#delete bike
def bike_delete(id):
  bike = bike_find(id)
  if not isinstance(bike, str):
    db.bicicleta.delete_one({'id':id})
    return f'Bicicleta <{id}> deletada com sucesso'
  return 'Erro: Bicicleta não encontrada / não existe'

#read all bikes
def bike_all():
  bikes = db.bicicletas.find()
  return list(bikes)

#-----------------------------------------------------------------------------------------------------------------------------------------------------#

#create emprestimo
def emp_add(user_id, bike_id, inicio, devolucao='em aberto'):
  if user_id and bike_id and inicio:
    bike = bike_find(bike_id)
    user = user_find(user_id)
    if bike['status'] == 'disponivel' and not isinstance(user, str):
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
      db.counters.update_one({}, {'$inc':{'emprestimos_id':1}})
      db.emprestimos.insert_one(dic)
      db.bicicletas.update_one({'id': bike_id}, {'$set': {'status': 'Em uso'}})
      if 'emprestimos' in user.keys():
        db.usuarios.update_one({'id': user_id}, {'$push': {'emprestimos': dic_user}})
      else:
        db.usuarios.update_one({'id': user_id}, {'$addToSet': {'emprestimos': dic_user}})
      return 'Emprestimo cadastrado com sucesso!'
    else:
      return f'Bicicleta <{bike_id}> já está em uso!'
  else:
    return 'Erro: Todos os campos são obrigatorios!'
  
#read one emp
def emp_find(id):
  '''
  retorna: {'_id': ObjectId('xxx'), 'id': 1, 'usuario_id': 1, 'bicicleta_id': 1, 'inicio': '01/01/2024', 'devolução': 'em aberto / 'dd/mm/aaaa'}
  caso o id não existir no DB, retorna: 'Erro: bicicleta não encontrada / não existe'
  '''
  emp = db.emprestimos.find_one({'id': id})
  if emp == None:
    return 'Erro: Emprestimo não encontrado / não existe'
  return emp

#read one emp
def emp_user_find(id, status='ativos'):
  '''
  retorna os emprestimos do usuario (por default retorna so os emprestimos ativos) \n
  para obter TODOS os emprestimos que o usuario ja teve => emp_user_find(id, 'all') <=
  '''
  if list(db.emprestimos.find({'usuario_id': id})) == None:
    return f'Nenhum emprestimo encontrado para o usuario <{id}>'
  if status == 'ativos':
    emp_ativos = db.emprestimos.find({'$and': [{'usuario_id': id}, {'status': 'ativo'}]})
    return emp_ativos
  all_emps = db.emprestimos.find({'usuario_id': id})
  return all_emps

#read one emp  
def emp_bike_find(id):
  emp = db.emprestimos.find_one({'bicicleta_id': id})
  if emp == None:
    return f'Nenhum emprestimo encontrado para o usuario <{id}>'
  return emp

#update emp
def emp_update(id, dic):
  emp = emp_find(id)
  if not isinstance(emp, str):
    for key in dic.keys():
      db.emprestimos.update_one({'id':id}, {'$set': {key:dic[key]}})
    return f'Emprestimo <{id}> editado com sucesso'
  return 'Erro: Emprestimo não existe / não encontrado'

#delete emp
def emp_delete(id):
  emp = emp_find(id)
  if not isinstance(emp, str):
    db.emprestimos.delete_one({'id':id})
    db.bicicletas.update_one({'id': emp['bicicleta_id']}, {'$set': {'status': 'disponivel'}})
    db.usuarios.update_one({'id': emp['usuario_id']}, {'$pull': {'emprestimos': {'id': id}}})
    return f'Emprestimo <{id}> deletado com sucesso'
  return 'Erro: Emprestimo não encontrado / não existe'
