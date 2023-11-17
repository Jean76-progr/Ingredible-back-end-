from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import os

# Intialise l'application Flask
app = Flask(__name__)

# Paramètre de configuration
app.config['SECRET_KEY'] = 'votre_cle_secrete'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ma_base_de_donnees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Test non concluant pour déposer des fichiers photos pour chaque recette
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Fonction qui rejoint la même idée de test non concluant
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Définition du modèle Compte pour les comptes utilisateurs
class Compte(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    favorite_recipes = db.relationship('FavoriteRecipe', backref='user', lazy='dynamic')
    user_ingredients = db.relationship('Ingredient', backref='user', lazy='dynamic')
    recipes = db.relationship('Recipe', backref='user', lazy='dynamic')

# Définition du modèle Ingredient
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('compte.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    recipe_ingredients = db.relationship('RecipeIngredient', backref='ingredient', lazy='dynamic')


# Définition du modèle Recipe
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('compte.id'))
    ingredients = db.relationship('Ingredient', secondary='recipe_ingredient', backref='recipes', lazy='dynamic')
    is_favorite = db.relationship('FavoriteRecipe', backref='recipe', lazy='dynamic')

# Définition du modèle RecipeIngredient
class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'))

# Définition du modèle FavoriteRecipe
class FavoriteRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('compte.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

# Définition du modèle Menu
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appetizer_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    main_course_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    dessert_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

# Créez la base de données
with app.app_context():
    db.create_all()

# Ajoutez cette route pour la création de compte
@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.form

    if 'username' in data and 'password' in data:
        username = data['username']
        password = data['password']

        # Créer un nouveau compte utilisateur
        compte = Compte(username=username, password=password)
        db.session.add(compte)

        try:
            # Listes de noms des ingrédients
            ingredient_data = []

            # Ajoutez chaque ingrédient à la base de données
            for ingredient_info in ingredient_data:
                ingredient = Ingredient(
                    name=ingredient_info['name'],
                    user_id=compte.id,
                )
                db.session.add(ingredient)

            db.session.commit()
            return jsonify({'message': 'Compte créé avec succès'}), 200

        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'Nom d\'utilisateur déjà utilisé'}), 400

    return jsonify({'message': 'Données manquantes'}), 400

# Ajoutez cette route pour supprimer un compte
@app.route('/delete_account', methods=['DELETE'])
def delete_account():
    data = request.get_json()

    if 'username' in data:
        username = data['username']
        compte = Compte.query.filter_by(username=username).first()

        if compte:
            # Supprimez toutes les recettes associées à ce compte
            Recipe.query.filter_by(user_id=compte.id).delete()
            # Supprimez l'utilisateur
            db.session.delete(compte)
            db.session.commit()
            session.clear()  # Déconnectez l'utilisateur après la suppression du compte

            return jsonify({'message': 'Compte supprimé avec succès'}), 200

    return jsonify({'message': 'La suppression du compte a échoué. Assurez-vous d\'inclure le nom d\'utilisateur dans les données de la requête.'}), 400

# Ajoutez cette route pour se connecter
@app.route('/login', methods=['POST'])
def login():
    data = request.form

    if 'username' in data and 'password' in data:
        username = data['username']
        password = data['password']

        # Filtre la base de données à la recherche de l'utilisateur
        compte = Compte.query.filter_by(username=username, password=password).first()

        if compte:
            session['user_id'] = compte.id
            session['username'] = username
            session.modified = True
            return jsonify({'message': 'Connexion réussie'}), 200
        else:
            return jsonify({'message': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401
    else:
        return jsonify({'message': 'Données manquantes'}), 400

# Ajoutez ces routes pour créer et supprimer des ingrédients
@app.route('/create_ingredient', methods=['POST'])
def create_ingredient():
    name = request.form.get('name')
    user_id = session.get('user_id')

    if name and user_id:
        ingredient = Ingredient(name=name, user_id=user_id)
        db.session.add(ingredient)
        db.session.commit()
        return jsonify({'message': 'Ingrédient créé avec succès'}), 200

    return jsonify({'message': 'Données manquantes'}), 400

# Ajoutez cette route pour gérer la déconnexion
@app.route('/logout', methods=['GET'])
def logout():
    data = request.form

    if 'username' in data:
        username = data['username']
        compte = Compte.query.filter_by(username=username).first()

        if compte:
            session.clear()  # Déconnectez l'utilisateur
            return jsonify({'message': 'Déconnexion réussie'}), 200

    return jsonify({'message': 'La suppression du compte a échoué. Assurez-vous d\'inclure le nom d\'utilisateur dans les données de la requête.'}), 400

# Ajoutez cette route pour créer une recette
@app.route('/create_recipe', methods=['POST'])
def create_recipe():
    user_id = session.get('user_id')

    if user_id:
        recipe_name = request.form.get('recipe_name')
        instructions = request.form.get('instructions')

        recipe = Recipe(name=recipe_name, instructions=instructions, user_id=user_id)
        db.session.add(recipe)
        db.session.commit()

        # Récupérez les ingrédients sélectionnés (par exemple, sous forme de liste d'IDs d'ingrédients)
        selected_ingredients = request.form.getlist('selected_ingredients')

        # Ajoutez ces ingrédients à la recette
        for ingredient_id in selected_ingredients:
            recipe_ingredient = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ingredient_id)
            db.session.add(recipe_ingredient)

        db.session.commit()
        return jsonify({'message': 'Recette créée avec succès'}), 200

    return jsonify({'message': 'Vous devez être connecté pour créer une recette'}), 401

# Ajoutez cette route pour afficher les recettes
@app.route('/get_recipes', methods=['GET'])
def get_recipes():
    user_id = session.get('user_id')

    if user_id:
        user_recipes = Recipe.query.filter_by(user_id=user_id).all()

        recipes = []
        for recipe in user_recipes:
            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'instructions': recipe.instructions,
                'image_path': recipe.image_path,
                'ingredients': [ingredient.name for ingredient in recipe.ingredients],
            }
            recipes.append(recipe_data)

        return jsonify({'recipes': recipes}), 200

    return jsonify({'message': 'Vous devez être connecté pour accéder à cette fonctionnalité'}), 401

# Ajoutez cette route pour marquer une recette comme favorite
@app.route('/favorite_recipe/<int:recipe_id>', methods=['POST'])
def favorite_recipe(recipe_id):
    user_id = session.get('user_id')

    if user_id:
        favorite = FavoriteRecipe(user_id=user_id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'message': 'Recette ajoutée aux favoris'}), 200

    return jsonify({'message': 'Vous devez être connecté pour ajouter une recette aux favoris'}), 401

# Ajoutez cette route pour afficher les recettes favorites
@app.route('/get_favorite_recipes', methods=['GET'])
def get_favorite_recipes():
    user_id = session.get('user_id')

    if user_id:
        favorite_recipes = FavoriteRecipe.query.filter_by(user_id=user_id).all()

        recipes = []
        for favorite_recipe in favorite_recipes:
            recipe = favorite_recipe.recipe
            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'instructions': recipe.instructions,
                'image_path': recipe.image_path,
                'ingredients': [ingredient.name for ingredient in recipe.ingredients],
            }
            recipes.append(recipe_data)

        return jsonify({'favorite_recipes': recipes}), 200

    return jsonify({'message': 'Vous devez être connecté pour accéder à cette fonctionnalité'}), 401

# Ajoutez cette route pour supprimer une recette favorite
@app.route('/unfavorite_recipe/<int:recipe_id>', methods=['DELETE'])
def unfavorite_recipe(recipe_id):
    user_id = session.get('user_id')

    if user_id:
        favorite_recipe = FavoriteRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

        if favorite_recipe:
            db.session.delete(favorite_recipe)
            db.session.commit()
            return jsonify({'message': 'Recette retirée des favoris'}), 200
        else:
            return jsonify({'message': 'La recette n est pas dans la liste des favoris'}), 404

    return jsonify({'message': 'Vous devez être connecté pour supprimer une recette des favoris'}), 401

# Ajoutez cette route pour supprimer une recette
@app.route('/delete_recipe/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    user_id = session.get('user_id')

    if user_id:
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()

        if recipe:
            db.session.delete(recipe)
            db.session.commit()
            return jsonify({'message': 'Recette supprimée avec succès'}), 200
        else:
            return jsonify({'message': 'La recette n appartient pas à cet utilisateur ou n existe pas'}), 404

    return jsonify({'message': 'Vous devez être connecté pour supprimer une recette'}), 401

# Ajoutez cette route pour mettre à jour une recette
@app.route('/update_recipe/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    user_id = session.get('user_id')

    if user_id:
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()

        if recipe:
            data = request.form
            recipe.name = data.get('recipe_name', recipe.name)
            recipe.instructions = data.get('instructions', recipe.instructions)

            # Mettez à jour les ingrédients de la recette
            selected_ingredients = data.getlist('selected_ingredients')
            recipe.ingredients = Ingredient.query.filter(Ingredient.id.in_(selected_ingredients)).all()

            db.session.commit()
            return jsonify({'message': 'Recette mise à jour avec succès'}), 200
        else:
            return jsonify({'message': 'La recette n appartient pas à cet utilisateur ou n existe pas'}), 404

    return jsonify({'message': 'Vous devez être connecté pour mettre à jour une recette'}), 401

# Ajoutez cette route pour créer un menu
@app.route('/create_menu', methods=['POST'])
def create_menu():
    user_id = session.get('user_id')

    if user_id:
        appetizer_id = request.form.get('appetizer_id')
        main_course_id = request.form.get('main_course_id')
        dessert_id = request.form.get('dessert_id')

        # Vérifiez que les recettes existent
        appetizer = Recipe.query.filter_by(id=appetizer_id, user_id=user_id).first()
        main_course = Recipe.query.filter_by(id=main_course_id, user_id=user_id).first()
        dessert = Recipe.query.filter_by(id=dessert_id, user_id=user_id).first()

        if appetizer and main_course and dessert:
            menu = Menu(appetizer_id=appetizer_id, main_course_id=main_course_id, dessert_id=dessert_id)
            db.session.add(menu)
            db.session.commit()

            return jsonify({'message': 'Menu créé avec succès'}), 200
        else:
            return jsonify({'message': 'Une ou plusieurs recettes du menu n\'existent pas ou n\'appartiennent pas à cet utilisateur'}), 400

    return jsonify({'message': 'Vous devez être connecté pour créer un menu'}), 401

# Ajoutez cette route pour obtenir la liste des recettes favorites
@app.route('/fetch_favorite_recipes', methods=['GET'])
def fetch_favorite_recipes():
    user_id = session.get('user_id')

    if user_id:
        favorite_recipes = FavoriteRecipe.query.filter_by(user_id=user_id).all()

        recipes = []
        for favorite_recipe in favorite_recipes:
            recipe = favorite_recipe.recipe
            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'instructions': recipe.instructions,
                'image_path': recipe.image_path,
                'ingredients': [ingredient.name for ingredient in recipe.ingredients],
            }
            recipes.append(recipe_data)

        return jsonify({'favorite_recipes': recipes}), 200

    return jsonify({'message': 'Vous devez être connecté pour accéder à cette fonctionnalité'}), 401

# Ajoutez cette route pour lister les ingrédients en fonction du nombre de convives
@app.route('/list_ingredients', methods=['GET'])
def list_ingredients():
    user_id = session.get('user_id')
    guests = request.args.get('guests', type=int)

    if user_id and guests:
        # Récupérez tous les ingrédients associés à l'utilisateur
        user_ingredients = Ingredient.query.filter_by(user_id=user_id).all()

        ingredients_list = []
        for ingredient in user_ingredients:
            ingredient_data = {
                'id': ingredient.id,
                'name': ingredient.name,
            }
            ingredients_list.append(ingredient_data)

        return jsonify({'ingredients': ingredients_list, 'guests': guests}), 200

    return jsonify({'message': 'Vous devez être connecté et spécifier le nombre de convives pour accéder à cette fonctionnalité'}), 401

if __name__ == '__main__':
    app.run(debug=True)
