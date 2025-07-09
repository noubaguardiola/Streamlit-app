# Exercice      : 4.2
# Cours         : L1 Outils informatiques collaboratifs, DN22ET01
# Auteur        : Chloé Vlaemynck
# Fichier       : exifstreamlit.py
# Description   : Streamlit Application
# Version       : 1.0
# Date          : 02-07-2025


import streamlit as st
from exif import Image as ExifImage # métadonnées dans une image
from PIL.ExifTags import TAGS, GPSTAGS #metadata
import geocoder #recupere la position actuelle via l'adresse IP
import folium #carte
from streamlit_folium import st_folium #carte dans streamlit
from fractions import Fraction



st.header("Bienvenue sur cette app Streamlit") #ajout d'un titre pour structurer la page


# Charge l’image depuis un fichier local
file_path = "cows.jpeg"

try:
    with open(file_path, "rb") as img_file:
        image_bytes = img_file.read()
        st.image(image_bytes, caption="Image : cows.jpeg", width=400) # Afficher l’image
        exif_img = ExifImage(image_bytes) # Lire les métadonnées exif de l’image avec exif

except FileNotFoundError:
    st.error("L'image cows.jpeg n'a pas été trouvée.")


#formulaire
st.subheader("Modifier les métadonnées EXIF") #ajout d'un titre pour structurer la page
with st.form("exif_form"): #ajout du formulaire
    #ajout de chaque champ de saisie, en liant le champ à la valeur de la métadonnée exif
    auteur = st.text_input("Auteur", value=getattr(exif_img, "artist", ""))
    copyright = st.text_input("Copyright", value=getattr(exif_img, "copyright", ""))
    modele = st.text_input("Modèle", value=getattr(exif_img, "model", ""))
    date = st.text_input("Date de création", value=getattr(exif_img, "datetime_original", ""))

    submit = st.form_submit_button(label = 'Sauvegarder') # bouton submit

# sauvegarde des nouvelles métadonnées 
if submit:
    # modification des attributs EXIF avec les valeurs saisies
    exif_img.artist = auteur
    exif_img.copyright = copyright
    exif_img.model = modele
    exif_img.datetime_original = date

    try:
        # nouvelle version de l’image avec les métadonnées modifiées
        new_bytes = exif_img.get_file()

        # Message de succès
        st.success("Nouvelles métadonnées sauvegardées")

        # Télécharger via bouton
        st.download_button(
            label="Télécharger l'image modifiée",
            data=new_bytes,
            file_name="image_modifiee.jpg",
            mime="image/jpeg"
        )

        # Enregistrer localement (optionnel sur Streamlit Cloud)
        nouveau_fichier = "image_updated.jpg"
        with open(nouveau_fichier, "wb") as f:
            f.write(new_bytes)

    except Exception as e:
        st.error(f"Erreur lors de la génération de l'image modifiée: {e}")


  # affichage des coordonnées GPS sur une carte
if exif_img.has_exif and exif_img.gps_latitude and exif_img.gps_longitude: # appel des coordonnées GPS présentes dans l’image
    # conversion des coordonnées DMS en format décimal
    def dms_to_decimal(coord, ref): 
        d = coord[0]
        m = coord[1]
        s = coord[2]
        decimal = d + (m / 60.0) + (s / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal

        # conversion des coordonnées pour les afficher sur une carte
    latitude = dms_to_decimal(exif_img.gps_latitude, exif_img.gps_latitude_ref)
    longitude = dms_to_decimal(exif_img.gps_longitude, exif_img.gps_longitude_ref)

    # affichage de la carte avec un marqueur 
    st.markdown("### Localisation GPS sur la carte")
    m = folium.Map(location=[latitude, longitude], zoom_start=12)
    folium.Marker([latitude, longitude], popup="Position EXIF de l'image").add_to(m)
    _ = st_folium(m, width=700, height=500)


else:
    st.warning("Aucune coordonnée GPS trouvée dans cette image.")


# remplacer la position actuelle via l'adresse IP

# Fonction : convertir un float en rationnel (x, 1)
def to_rational(number):
    return (Fraction(str(number)).limit_denominator().numerator,
            Fraction(str(number)).limit_denominator().denominator)

# Fonction : convertir coordonnées décimales en format DMS pour EXIF
def decimal_to_dms_rational(decimal):
    decimal = abs(decimal)
    degrees = int(decimal)
    minutes_float = (decimal - degrees) * 60
    minutes = int(minutes_float)
    seconds = round((minutes_float - minutes) * 60, 2)

    return [
        to_rational(degrees),
        to_rational(minutes),
        to_rational(seconds)
    ]

#Donner plus de controle a l'utilisateur en le laissant cliquer un bouton
if st.button("Remplacer les coordonnées GPS par ma position actuelle"):
    g = geocoder.ip('me')
    if g.ok:
        lat, lon = g.latlng

        try:
            exif_img.gps_latitude = decimal_to_dms_rational(lat)
            exif_img.gps_latitude_ref = "N" if lat >= 0 else "S"

            exif_img.gps_longitude = decimal_to_dms_rational(lon)
            exif_img.gps_longitude_ref = "E" if lon >= 0 else "W"

            st.success(f"Coordonnées GPS mises à jour avec ta position actuelle :\n\nLatitude: {lat}, Longitude: {lon}")

        except Exception as e:
            st.error(f"Erreur lors de l'écriture des coordonnées GPS dans l'image : {e}")
    else:
        st.error("Impossible de déterminer votre position actuelle.")


#lieux visités
st.subheader("Lieux visités")
#dictionnaire listant les lieux visités
locations = {
    "Sydney": [-33.8688, 151.2093],
    "Queenstown": [-45.0312, 168.6626],
    "Lille": [50.6292, 3.0573],
    "Stavanger": [58.9699, 5.7331],
    "Melbourne": [-37.8136, 144.9631]
}

# création d'une carte POI
m2 = folium.Map(location=[0, 0], zoom_start=2)
for city, coord in locations.items():
    folium.Marker(coord, popup=city).add_to(m2)
folium.PolyLine(list(locations.values()), color="purple").add_to(m2) #lier les lieux entre eux

_ = st_folium(m, width=700, height=500) #affichage de la carte







