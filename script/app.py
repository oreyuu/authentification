
from flask import Flask, request, render_template, session, redirect
import mariadb
import os

app = Flask(__name__)

# Configuration Flask
app.secret_key = os.environ["FLASK_SECRET_KEY"]


# Page d'accueil
@app.route("/")
def accueil():
    return render_template("index.html")


# Traitement de la connexion
@app.route("/envoyer", methods=["POST"])
def connexion():

    identifiant = request.form.get("identifient")
    mot_de_passe = request.form.get("password")

    conn = None
    cur = None

    try:
        # Connexion à MariaDB
        conn = mariadb.connect(
            user="flask_user",
            password=os.environ["DB_PASSWORD"],
            host="10.37.55.221",
            port=3306,
            database="authentification"
        )

        cur = conn.cursor()

        # Recherche de l'utilisateur
        query = """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ? AND password_hash = ?
        """

        cur.execute(query, (identifiant, mot_de_passe))

        # Récupération du résultat
        resultat = cur.fetchone()

        if resultat is not None:

            # Création de la session
            session["user_id"] = resultat[0]

            # Redirection vers le tableau de bord
            return redirect("/dashboard")

        else:
            # Identifiants incorrects
            return redirect("/")

    except mariadb.Error as e:
        print(f"Erreur MariaDB : {e}")
        return "Erreur lors de la connexion à la base de données", 500

    finally:
        # Fermeture des ressources
        if cur is not None:
            cur.close()

        if conn is not None:
            conn.close()


# Page privée
@app.route("/dashboard", methods=["GET"])
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    return render_template("dashboard.html")


# Déconnexion
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# Lancement du serveur flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
