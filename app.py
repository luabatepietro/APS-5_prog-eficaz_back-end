from bson import json_util, ObjectId
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import pymongo
import os
import db_func
import datetime

app = Flask(__name__)
uri = 'mongodb+srv://admin:admin@garnet.hotoadz.mongodb.net/aps5_db'
app.config["MONGO_URI"] = uri
mongo = PyMongo(app)


@app.route('/')
def hello_world():
    return "Web service funcionando"

def serialize_doc(doc):
    """ Helper function to serialize MongoDB documents (convert ObjectId). """
    doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
    return doc

#--------------------------------------------------------------------------------------
#----------------------------------------USUARIOS--------------------------------------
#--------------------------------------------------------------------------------------


@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():

    if request.method == 'GET':
        users = mongo.db.usuarios.find()
        user_list = [serialize_doc(user) for user in users]
        if not user_list:
            return ({'Mensagem': 'Nenhum usuário encontrado'}), 404
        return (user_list), 200
    

    elif request.method == 'POST':
        data = request.json
        nome = data.get('nome')
        cpf = data.get('CPF')
        nascimento = data.get('data')
        
        if nome and cpf and nascimento:
            existing_user = mongo.db.usuarios.find_one({'CPF': cpf})
            if existing_user is None:

                counter = mongo.db.counters.find_one()
                usuario_id = counter['usuarios_id']

                novo_usuario = {
                    'id': usuario_id,
                    'nome': nome,
                    'CPF': cpf,
                    'data': nascimento,
                    'emprestimos': []
                }

                mongo.db.counters.update_one({}, {'$inc':{'usuarios_id':1}})
                mongo.db.usuarios.insert_one(novo_usuario)
                return ({'message': 'Usuário cadastrado com sucesso!'}), 201
            return ({'error': 'Usuário já existe!'}), 409
        return ({'error': 'Todos os campos são obrigatórios!'}), 400


@app.route('/usuarios/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def usuario(id):
    if request.method == 'GET':
        user = mongo.db.usuarios.find_one({'id': id})
        if user is None:
            return ({'mensagem': 'Usuário com este ID não existe'}), 404
        return serialize_doc(user), 200

    elif request.method == 'PUT':
        update_data = request.json
        result = mongo.db.usuarios.update_one({'id': id}, {'$set': update_data})
        if result.matched_count == 0:
            return ({'mensagem': 'Nenhum usuario encontrado com este ID'}), 404
        return ({'mensagem': 'Usuario atualizado com sucesso'}), 200

    elif request.method == 'DELETE':
        result = mongo.db.usuarios.delete_one({'id': id})
        if result.deleted_count == 0:
            return ({'message': 'Nenhum usuario encontrado com este ID'}), 404
        return ({'message': 'Usuario deletado com sucesso'}), 200


#--------------------------------------------------------------------------------------
#----------------------------------------BICICLETAS------------------------------------
#--------------------------------------------------------------------------------------


@app.route('/bikes', methods=['GET', 'POST'])
def bicicletas():
    if request.method == 'GET':
        bikes = mongo.db.bicicletas.find()
        bikes_list = [serialize_doc(bike) for bike in bikes]
        if not bikes_list:
            return jsonify({'Mensagem': 'Nenhuma bicicleta encontrada'}), 404
        return(bikes_list), 200
    
    elif request.method == 'POST':
        data = request.json
        marca = data.get('marca')
        modelo = data.get('modelo')
        cidade = data.get('cidade')
        
        if marca and modelo and cidade:
            counter = mongo.db.counters.find_one()
            bicicletas_id = counter['bicicletas_id']

            dic = {
            'id': bicicletas_id,
            'marca': marca,
            'modelo': modelo,
            'cidade': cidade,
            'status': 'disponivel'
            }

            mongo.db.counters.update_one({}, {'$inc':{'bicicletas_id':1}})
            mongo.db.bicicletas.insert_one(dic)
            return ({'message': 'Bike cadastrada com sucesso!'}), 201
        return ({'error': 'Todos os campos são obrigatórios!'}), 400


@app.route('/bikes/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def bike(id):
    if request.method == 'GET':
        bike = mongo.db.bicicletas.find_one({'id': id})
        if bike is None:
            return ({'mensagem': 'bike com este ID não existe'}), 404
        return serialize_doc(bike), 200

    elif request.method == 'PUT':
        update_data = request.json
        result = mongo.db.bicicletas.update_one({'id': id}, {'$set': update_data})
        if result.matched_count == 0:
            return ({'mensagem': 'Nenhuma bike encontrado com este ID'}), 404
        return ({'mensagem': 'bike atualizadacom sucesso'}), 200

    elif request.method == 'DELETE':
        result = mongo.db.bicicletas.delete_one({'id': id})
        if result.deleted_count == 0:
            return ({'message': 'Nenhuma bike encontrado com este ID'}), 404
        return ({'message': 'bike deletada com sucesso'}), 200    


#--------------------------------------------------------------------------------------
#----------------------------------------EMPRESTIMO------------------------------------
#--------------------------------------------------------------------------------------

@app.route('/emprestimos', methods=['GET'])
def emprestimos():
    if request.method == 'GET':
        emprestimos = mongo.db.emprestimos.find({}, {'id': 1, 'usuario_id': 1, 'bicicleta_id': 1})
        emp_list = [serialize_doc(emp) for emp in emprestimos]
        if not emp_list:
            return ({'Mensagem': 'Nenhum emprestimo encontrado'}), 404
        return (emp_list), 200

@app.route('/emprestimos/usuarios/<int:id_usuario>/bikes/<int:id_bike>', methods=['POST'])
def emp_bike(id_usuario, id_bike):
    if request.method == 'POST':
        if id_usuario and id_bike:
            bike = db_func.bike_find(id_bike)
            user = db_func.user_find(id_usuario)
            inicio = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            devolucao = 'em aberto'

            counter = mongo.db.counters.find_one()
            emprestimos_id = counter['emprestimos_id']

            if bike['status'] == 'disponivel' and not isinstance(user, str):
                dic = {
                    'id': emprestimos_id,
                    'usuario_id': id_usuario,
                    'bicicleta_id': id_bike,
                    'inicio': inicio,
                    'devolucao': devolucao,
                    'status': 'ativo'
                }

                dic_user = {
                    'id': emprestimos_id,
                    'bicicleta_id': id_bike,
                    'inicio': inicio,
                    'devolucao': devolucao
                }

                dic_bike = {
                    'id': emprestimos_id,
                    'usuario_id': id_usuario,
                    'inicio': inicio,
                    'devolucao': devolucao
                }

                mongo.db.counters.update_one({}, {'$inc':{'emprestimos_id':1}})
                mongo.db.emprestimos.insert_one(dic)
                mongo.db.bicicletas.update_one({'id': id_bike}, {'$set': {'status': 'Em uso'}})

                mongo.db.usuarios.update_one({'id': id_usuario}, {'$push': {'emprestimos': dic_user}})

                mongo.db.bicicletas.update_one({'id': id_bike}, {'$push': {'emprestimo': dic_bike}})

                return {'resp': 'Emprestimo cadastrado com sucesso!', 'status_code': 201}
            else:
                return {'resp': f'Bicicleta <{id_bike}> já está em uso!', 'status_code': 400}
        else:
            return {'resp': 'Erro: Todos os campos são obrigatorios!', 'status_code': 400}


@app.route('/emprestimos/<int:id_emprestimo>', methods=['DELETE'])
def emp_delete(id_emprestimo):
  if request.method == 'DELETE':
    emp = db_func.emp_find(id_emprestimo)
    if not isinstance(emp, str):
        mongo.db.emprestimos.update_one({'id':id_emprestimo}, {'$set': {'status': 'inativo'}})
        mongo.db.bicicletas.update_one({'id': emp['bicicleta_id']}, {'$set': {'status': 'disponivel'}})
        mongo.db.usuarios.update_one({'id': emp['usuario_id']}, {'$pull': {'emprestimos': {'id': id_emprestimo}}})
        return f'Emprestimo <{id_emprestimo}> deletado com sucesso'
    return 'Erro: Emprestimo não encontdrado existe'



if __name__ == '__main__':
    app.run(debug=True)
