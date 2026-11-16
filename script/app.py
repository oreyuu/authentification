from flask import Flask, request, render_template, session, redirect
import mariadb
import os
import hashlib
import subprocess

app = Flask(
    __name__,
    template_folder="../template",
    static_folder="..",
    static_url_path="/static"
)
# Configuration Flask
app.secret_key = os.environ["FLASK_SECRET_KEY"]

##########################################################################
# Fonction pour tester le ping
def tester_ping(ip):
    param = "-n" if subprocess.os.name == "nt" else "-c"
    command = ["ping", param, "1", ip]

    try:
        resultat = subprocess.run(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return "OK" if resultat.returncode == 0 else "KO"
    except Exception:
        return "KO"

####################################################################################

# Page d'accueil
@app.route("/")
def accueil():
    return render_template("index.html")


# Traitement de la connexion
@app.route("/envoyer", methods=["POST"])
def connexion():
    identifiant = request.form.get("identifiant")
    mot_de_passe = request.form.get("password")

    if not identifiant or not mot_de_passe:
        return redirect("/")

    mot_de_passe_encode = mot_de_passe.encode("utf-8") 
    mot_de_passe_hash = hashlib.sha256(mot_de_passe_encode)
    hash_hex = mot_de_passe_hash.hexdigest()

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

        # Recherche de l'utilisateur (on récupère aussi le rôle et le nom)
        query = """
            SELECT id, username, password_hash, role
            FROM users
            WHERE username = ? AND password_hash = ?
        """

        cur.execute(query, (identifiant, hash_hex))

        # Récupération du résultat
        resultat = cur.fetchone()

        if resultat is not None:
            # Création de la session
            session["user_id"] = resultat[0]
            session["username"] = resultat[1]
            session["role"] = resultat[3]

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


# Page privée / Tableau de bord (Hypervision)
@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    # Test des pings pour tous les serveurs du dashboard
    statuts = {
        "srv_web": tester_ping("10.37.55.220"),
        "srv_bdd": tester_ping("10.37.55.221"),
        "srv_rsdk": tester_ping("10.37.55.226"),
        "srv_jmps": tester_ping("10.37.55.227"),
        "srv_gcml": tester_ping("10.37.55.225"),
        "srv_smbd": tester_ping("10.37.55.222"),
        "srv_win": tester_ping("10.37.55.225")
    }

    return render_template(
        "dashboard.html",
        user=session.get("username"),
        role_user=session.get("role"),
        **statuts
    )


# Déconnexion
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/connexion")
def connexion_page():
    return render_template("connexion.html")


@app.route("/actevolis")
def actevolis():
    return render_template("actevolis.html")


@app.route("/mentions-legales")
def mentions_legales():
    return render_template("mention_legal.html")


@app.route("/rgpd")
def rgpd():
    return render_template("rgpd.html")


# Lancement du serveur flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)