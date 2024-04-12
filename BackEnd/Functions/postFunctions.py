import base64
from flask import request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS
import BackEnd.GlobalInfo.Keys as PracticaKeys
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessages
from PIL import Image
from io import BytesIO

if PracticaKeys.dbconn == None:
    mongoConnect = MongoClient(PracticaKeys.strConnection)
    PracticaKeys.dbconn = mongoConnect[PracticaKeys.strDBConnection]
    
    # Definir dbConnPost fuera de cualquier función
dbConnPost = PracticaKeys.dbconn["clChisme"]
    


def getChisme():
    try:
        objFindColab = dbConnPost.find()
        listColab = list(objFindColab)
        
        for colab in listColab:
            colab['_id'] = str(colab['_id'])  # Convierte ObjectId a string
            
            # Verificar si existe la imagen y si no está vacía
            if 'binImage' in colab and colab['binImage']:
                # Procesar la imagen
                img_bytes = colab['binImage']
                img = Image.open(BytesIO(img_bytes))
                
                buffered = BytesIO()
                img.save(buffered, format="PNG")  # Cambia el formato si es necesario
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                colab['image'] = img_str  # Añadir la imagen codificada al diccionario
                del colab['binImage']  # Eliminar la propiedad binImage
            else:
                # Establecer la imagen como None o quitar la propiedad si no se desea guardar
                colab['image'] = None
        
        response_data = {'Response': listColab}
        return jsonify(response_data)
    except Exception as e:
        print("error get colaboradores:", e)
        return jsonify({'error': 'Internal Server Error'}), 500  

def postChisme():
    try:
        data = request.get_json()
        titulo = data.get('strTitulo')
        chisme = data.get('strChisme')
        usuario = data.get('strUsuario')
        categoria = data.get('strCategoria')
        
        nuevo_chisme = {
            'strTitulo': titulo,
            'strChisme': chisme,
            'strUsuario': usuario,
            'strCategoria': categoria
        }
        
        resultado = dbConnPost.insert_one(nuevo_chisme)
        
        if resultado.inserted_id:
            nuevo_chisme['_id'] = str(resultado.inserted_id)
            return jsonify(nuevo_chisme), 200
        else:
            return jsonify(ResponseMessages.message500), 500
    except Exception as e:
        print('Error al agregar chisme', e)
        return jsonify(ResponseMessages.message500), 500
    
    
def postLikes(_id):
    try:
        publicacion = dbConnPost.find_one({'_id':ObjectId(_id)})
        if publicacion:
            # Incrementa el contador de likes de la publicación
            dbConnPost.update_one({'_id': ObjectId(_id)}, {'$inc': {'intLikes': 1}})
            return jsonify({'mensaje': 'Like agregado a la publicación'}), 200
        else:
            return jsonify({'mensaje': 'Publicación no encontrada'}), 404
    except Exception as e:
        print("Error al dar like a la publicación:", e)
        return jsonify({'mensaje': 'Error al dar like a la publicación'}), 500
    
def postDislikes(_id):
    try:
        publicacion = dbConnPost.find_one({'_id':ObjectId(_id)})
        if publicacion:
            # Incrementa el contador de likes de la publicación
            dbConnPost.update_one({'_id': ObjectId(_id)}, {'$inc': {'intDislikes': 1}})
            return jsonify({'mensaje': 'Dislike agregado a la publicación'}), 200
        else:
            return jsonify({'mensaje': 'Publicación no encontrada'}), 404
    except Exception as e:
        print("Error al dar dislike a la publicación:", e)
        return jsonify({'mensaje': 'Error al dar dislike a la publicación'}), 500
    
def postImage():
    try:
        strTitulo = request.form['strTitulo']
        return setImage(strTitulo)
    except Exception as e:
        print("Error al procesar la solicitud:", e)
        return jsonify(ResponseMessages.message500)
    
def getLastImage():
    try:
        objFindColab = dbConnPost.find({}, { 'binImage': 1 }).sort('_id', -1).limit(3)
        listColab = list(objFindColab)
        
        for colab in listColab:
            # Convierto el ObjectId en string para que me lo acepte el programa
            colab['_id'] = str(colab['_id'])
            
            # Convertir bytes de la imagen a imagen
            img_bytes = colab['binImage']
            img = Image.open(BytesIO(img_bytes))
            
            # Convertir la imagen a base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")  # Puedes cambiar el formato según tu necesidad
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            colab['image'] = img_str  # Añadir la imagen codificada al diccionario
            
            # Eliminar la propiedad binImage si no es necesaria después de convertirla a imagen
            del colab['binImage']
        
        # Crear un diccionario con la clave 'Response' y la lista de colaboradores como valor
        response_data = {'Response': listColab}
        return jsonify(response_data)
    except Exception as e:
        print("error get colaboradores:", e)
        return jsonify({'message': 'Internal Server Error'}), 500
        

    
def setImage(strTitulo):
    try:
        binImagen = request.files['imagen']
        datosImagen = binImagen.read()
    
        resultado = dbConnPost.update_one({'strTitulo': strTitulo}, {'$set': {'binImage': datosImagen}})
        
        if resultado.modified_count == 1:
            return jsonify({'mensaje': 'Imagen subida correctamente'}), 200
        else:
            return jsonify({'mensaje': 'Usuario no encontrado'}), 404
    except Exception as e:
        print("Error al subir imagen:", e)
        return jsonify(ResponseMessages.message500)
    
def getAllCategory():
    try:
        objFindColab = dbConnPost.find({}, { 'strCategoria': 1 })
        listColab = list(objFindColab)
        
        for colab in listColab:
            # Convierto el ObjectId en string para que me lo acepte el programa
            colab['_id'] = str(colab['_id'])
            
        # Crear un diccionario con la clave 'Response' y la lista de colaboradores como valor
        response_data = {'Response': listColab}
        return jsonify(response_data)
    except Exception as e:
        print("error get colaboradores:", e)
        return jsonify({'message': 'Internal Server Error'}), 500