"""
scopeREPAIR prototype — single source of content.

All copy comes from the live site scoperepair.de (DE + EN pages) or the
approved design. FR and RU are translations of that copy (marked as
machine translation to be reviewed). Nothing here is invented: where the
live site has no data (prices, delivery times, reviews), the UI shows a
neutral state instead.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = ['de', 'en', 'fr', 'ru']
LANG_NAMES = {'de': 'Deutsch', 'en': 'English', 'fr': 'Français', 'ru': 'Русский'}
DEFAULT_LANG = 'de'


def L(de, en, fr, ru):
    return {'de': de, 'en': en, 'fr': fr, 'ru': ru}


# ──────────────────────────────────────────────────────────────────────────
# Company facts (from Impressum / Kontakt on scoperepair.de)
# ──────────────────────────────────────────────────────────────────────────
COMPANY = {
    'name': 'scopeREPAIR GmbH',
    'street': 'Raiffeisenstraße 11',
    'zip': '21516',
    'city': 'Müssen',
    'country': L('Deutschland', 'Germany', 'Allemagne', 'Германия'),
    'phone': '+49 4155 8237-331',
    'phone_href': 'tel:+4941558237331',
    'fax': '+49 4155 8237-332',
    'email': 'info@scoperepair.de',
    'ceo': 'Maik Nissen',
    'ceo_role': L('Geschäftsführer', 'Managing Director', 'Gérant', 'Управляющий директор'),
    'register': 'Amtsgericht Lübeck, HRB 21027 HL',
    'vat': 'DE341101150',
    'iso': 'DIN EN ISO 9001:2015',
}

HOURS = [
    (L('Montag – Donnerstag', 'Monday – Thursday', 'Lundi – jeudi', 'Понедельник – четверг'), '08:00 – 17:00'),
    (L('Freitag', 'Friday', 'Vendredi', 'Пятница'), '08:00 – 14:00'),
]

# ──────────────────────────────────────────────────────────────────────────
# Navigation. Keys map to page ids (see PAGES in build.py)
# ──────────────────────────────────────────────────────────────────────────
NAV = [
    {'id': 'index', 'label': L('Startseite', 'Home', 'Accueil', 'Главная')},
    {'id': 'reparatur', 'label': L('Reparatur', 'Repair', 'Réparation', 'Ремонт'), 'children': [
        {'id': 'reparatur', 'label': L('Endoskop-Reparatur', 'Endoscope repair', 'Réparation d’endoscopes', 'Ремонт эндоскопов'),
         'sub': L('Ablauf, Gewährleistung, FAQ', 'Process, warranty, FAQ', 'Déroulement, garantie, FAQ', 'Процесс, гарантия, FAQ')},
        {'id': 'reparatur-auftrag', 'label': L('Abholauftrag', 'Pick-up order', 'Demande d’enlèvement', 'Заказ забора'),
         'sub': L('Reparatur online beauftragen', 'Order a repair online', 'Commander une réparation en ligne', 'Заказать ремонт онлайн')},
        {'id': 'leihgeraete', 'label': L('Leihgeräte', 'Loaner devices', 'Appareils de prêt', 'Подменные аппараты'),
         'sub': L('Weiterarbeiten während der Reparatur', 'Keep working during the repair', 'Continuer à travailler pendant la réparation', 'Работайте, пока идёт ремонт')},
        {'id': 'rechner', 'label': L('Kostenrechner', 'Cost calculator', 'Calculateur de coûts', 'Калькулятор затрат'),
         'sub': L('Servicevertrag oder Reparatur nach Bedarf', 'Service contract or repair on demand', 'Contrat de service ou réparation à la demande', 'Сервисный договор или ремонт по необходимости')},
    ]},
    {'id': 'gebrauchte-endoskope', 'label': L('Gebrauchte Endoskope', 'Used endoscopes', 'Endoscopes d’occasion', 'Б/у эндоскопы'), 'children': [
        {'id': 'gebrauchte-endoskope', 'label': L('Alle Endoskope', 'All endoscopes', 'Tous les endoscopes', 'Все эндоскопы'), 'query': ''},
        {'id': 'gebrauchte-endoskope', 'label': L('Olympus', 'Olympus', 'Olympus', 'Olympus'), 'query': '?hersteller=olympus'},
        {'id': 'gebrauchte-endoskope', 'label': L('Pentax', 'Pentax', 'Pentax', 'Pentax'), 'query': '?hersteller=pentax'},
        {'id': 'gebrauchte-endoskope', 'label': L('Fujinon', 'Fujinon', 'Fujinon', 'Fujinon'), 'query': '?hersteller=fujinon'},
    ]},
    {'id': 'ankauf', 'label': L('Ankauf', 'Buy-back', 'Rachat', 'Выкуп')},
    {'id': 'endoskopie-anlagen', 'label': L('Endoskopie-Anlagen', 'Endoscopy systems', 'Systèmes d’endoscopie', 'Эндоскопические системы')},
    {'id': 'ueber-uns', 'label': L('Über uns', 'About us', 'À propos', 'О нас')},
    {'id': 'kontakt', 'label': L('Kontakt', 'Contact', 'Contact', 'Контакты')},
]

FOOTER_COLS = [
    (L('Leistungen', 'Services', 'Services', 'Услуги'), [
        ('reparatur', L('Endoskop-Reparatur', 'Endoscope repair', 'Réparation d’endoscopes', 'Ремонт эндоскопов')),
        ('leihgeraete', L('Leihgeräte', 'Loaner devices', 'Appareils de prêt', 'Подменные аппараты')),
        ('gebrauchte-endoskope', L('Gebrauchte Endoskope', 'Used endoscopes', 'Endoscopes d’occasion', 'Б/у эндоскопы')),
        ('ankauf', L('Ankauf', 'Buy-back', 'Rachat', 'Выкуп')),
        ('endoskopie-anlagen', L('Endoskopie-Anlagen', 'Endoscopy systems', 'Systèmes d’endoscopie', 'Эндоскопические системы')),
    ]),
    (L('Service', 'Service', 'Service', 'Сервис'), [
        ('reparatur-auftrag', L('Abholauftrag', 'Pick-up order', 'Demande d’enlèvement', 'Заказ забора')),
        ('leihgeraet-anfragen', L('Leihgerät anfragen', 'Request a loaner', 'Demander un appareil de prêt', 'Запросить подменный аппарат')),
        ('ankauf-anfrage', L('Gerät verkaufen', 'Sell a device', 'Vendre un appareil', 'Продать аппарат')),
        ('rechner', L('Kostenrechner', 'Cost calculator', 'Calculateur de coûts', 'Калькулятор затрат')),
    ]),
    (L('Unternehmen', 'Company', 'Entreprise', 'Компания'), [
        ('ueber-uns', L('Über uns', 'About us', 'À propos', 'О нас')),
        ('kontakt', L('Kontakt', 'Contact', 'Contact', 'Контакты')),
    ]),
]

LEGAL_LINKS = [
    ('impressum', L('Impressum', 'Imprint', 'Mentions légales', 'Импрессум')),
    ('datenschutz', L('Datenschutz', 'Privacy policy', 'Protection des données', 'Защита данных')),
    ('agb', L('AGB', 'Terms of service', 'CGV', 'Условия')),
    ('rechtliches', L('Text- und Bildrechte', 'Copyright', 'Droits d’auteur', 'Авторские права')),
]

# ──────────────────────────────────────────────────────────────────────────
# UI strings
# ──────────────────────────────────────────────────────────────────────────
T = {
    'skip': L('Zum Inhalt springen', 'Skip to content', 'Aller au contenu', 'Перейти к содержимому'),
    'menu': L('Menü', 'Menu', 'Menu', 'Меню'),
    'close': L('Schließen', 'Close', 'Fermer', 'Закрыть'),
    'language': L('Sprache', 'Language', 'Langue', 'Язык'),
    'cta_repair': L('Reparatur beauftragen', 'Order a repair', 'Commander une réparation', 'Заказать ремонт'),
    'cta_call': L('Anrufen', 'Call', 'Appeler', 'Позвонить'),
    'cta_contact': L('Kontakt aufnehmen', 'Get in touch', 'Nous contacter', 'Связаться с нами'),
    'cta_callback': L('Rückruf anfordern', 'Request a call-back', 'Demander un rappel', 'Заказать обратный звонок'),
    'cta_loaner': L('Leihgerät anfragen', 'Request a loaner', 'Demander un appareil de prêt', 'Запросить подменный аппарат'),
    'cta_sell': L('Gerät verkaufen', 'Sell a device', 'Vendre un appareil', 'Продать аппарат'),
    'cta_catalog': L('Zum Katalog', 'Browse the catalogue', 'Voir le catalogue', 'Перейти в каталог'),
    'cta_all_endoscopes': L('Alle Endoskope', 'All endoscopes', 'Tous les endoscopes', 'Все эндоскопы'),
    'cta_inquire': L('Anfragen', 'Inquire', 'Demander', 'Запросить'),
    'cta_more': L('Mehr erfahren', 'Learn more', 'En savoir plus', 'Подробнее'),
    'cta_calc': L('Zum Kostenrechner', 'Open the cost calculator', 'Ouvrir le calculateur', 'Открыть калькулятор'),
    'next': L('Weiter', 'Next', 'Suivant', 'Далее'),
    'back': L('Zurück', 'Back', 'Retour', 'Назад'),
    'edit': L('Ändern', 'Edit', 'Modifier', 'Изменить'),
    'optional': L('optional', 'optional', 'facultatif', 'необязательно'),
    'required_note': L('Pflichtfelder sind markiert.', 'Required fields are marked.', 'Les champs obligatoires sont indiqués.', 'Обязательные поля отмечены.'),
    'fill_demo': L('Mit Testdaten ausfüllen', 'Fill with test data', 'Remplir avec des données de test', 'Заполнить тестовыми данными'),
    'proto_note': L('Prototyp: Es wird nichts gesendet. In der Live-Version geht die Anfrage per E-Mail an scopeREPAIR.',
                    'Prototype: nothing is sent. In the live version the request is e-mailed to scopeREPAIR.',
                    'Prototype : rien n’est envoyé. Dans la version en ligne, la demande est envoyée par e-mail à scopeREPAIR.',
                    'Прототип: ничего не отправляется. В рабочей версии запрос уходит в scopeREPAIR по e-mail.'),
    'proto_error_hint': L('Zum Testen des Fehlerfalls: E-Mail mit „fehler“ eingeben.',
                          'To test the error state, enter an e-mail containing “error”.',
                          'Pour tester l’erreur, saisissez un e-mail contenant « erreur ».',
                          'Чтобы проверить ошибку, введите e-mail со словом «error».'),
    'send_error_title': L('Senden fehlgeschlagen', 'Sending failed', 'Échec de l’envoi', 'Не удалось отправить'),
    'send_error_text': L('Bitte versuchen Sie es erneut oder rufen Sie uns an:', 'Please try again or call us:', 'Veuillez réessayer ou nous appeler :', 'Попробуйте ещё раз или позвоните нам:'),
    'sending': L('Wird gesendet…', 'Sending…', 'Envoi…', 'Отправка…'),
    'not_built': L('Diese Funktion ist im Prototyp nicht umgesetzt.', 'This feature is not built in the prototype.', 'Cette fonction n’est pas réalisée dans le prototype.', 'Эта функция в прототипе не реализована.'),
    'consent': L('Ich habe die {link} zur Kenntnis genommen und stimme zu, dass meine Angaben zur Bearbeitung meines Anliegens an die scopeREPAIR GmbH übermittelt und dort gespeichert werden.',
                 'I have read the {link} and agree that my details are sent to scopeREPAIR GmbH and stored there to process my request.',
                 'J’ai pris connaissance de la {link} et j’accepte que mes données soient transmises à scopeREPAIR GmbH et y soient conservées pour traiter ma demande.',
                 'Я ознакомлен(а) с {link} и согласен(на), что мои данные будут переданы в scopeREPAIR GmbH и сохранены там для обработки запроса.'),
    'privacy_link': L('Datenschutzerklärung', 'privacy policy', 'politique de confidentialité', 'политикой конфиденциальности'),
    'err_required': L('Bitte füllen Sie dieses Feld aus.', 'Please fill in this field.', 'Veuillez remplir ce champ.', 'Заполните это поле.'),
    'err_choose': L('Bitte wählen Sie eine Option.', 'Please choose an option.', 'Veuillez choisir une option.', 'Выберите вариант.'),
    'err_email': L('Bitte geben Sie eine gültige E-Mail-Adresse ein.', 'Please enter a valid e-mail address.', 'Veuillez saisir une adresse e-mail valide.', 'Введите корректный e-mail.'),
    'err_phone': L('Bitte geben Sie eine Telefonnummer an.', 'Please enter a phone number.', 'Veuillez indiquer un numéro de téléphone.', 'Укажите номер телефона.'),
    'err_zip': L('Bitte geben Sie eine gültige PLZ an.', 'Please enter a valid postcode.', 'Veuillez saisir un code postal valide.', 'Укажите корректный индекс.'),
    'err_consent': L('Bitte bestätigen Sie die Datenschutzerklärung.', 'Please accept the privacy policy.', 'Veuillez accepter la politique de confidentialité.', 'Подтвердите согласие с политикой конфиденциальности.'),
    'err_summary': L('Bitte prüfen Sie die markierten Felder.', 'Please check the highlighted fields.', 'Veuillez vérifier les champs signalés.', 'Проверьте отмеченные поля.'),
    # fields
    'f_salutation': L('Anrede', 'Salutation', 'Civilité', 'Обращение'),
    'sal': [L('Firma', 'Company', 'Société', 'Компания'), L('Frau', 'Ms', 'Madame', 'Г-жа'), L('Herr', 'Mr', 'Monsieur', 'Г-н'), L('Divers', 'Other', 'Autre', 'Другое')],
    'f_company': L('Firma / Praxis / Klinik', 'Company / practice / clinic', 'Société / cabinet / clinique', 'Компания / практика / клиника'),
    'f_firstname': L('Vorname', 'First name', 'Prénom', 'Имя'),
    'f_lastname': L('Nachname', 'Last name', 'Nom', 'Фамилия'),
    'f_name': L('Ihr Name', 'Your name', 'Votre nom', 'Ваше имя'),
    'f_email': L('E-Mail', 'E-mail', 'E-mail', 'E-mail'),
    'f_phone': L('Telefon', 'Phone', 'Téléphone', 'Телефон'),
    'f_street': L('Straße und Hausnummer', 'Street and number', 'Rue et numéro', 'Улица и дом'),
    'f_zip': L('PLZ', 'Postcode', 'Code postal', 'Индекс'),
    'f_city': L('Ort', 'City', 'Ville', 'Город'),
    'f_country': L('Land', 'Country', 'Pays', 'Страна'),
    'f_message': L('Nachricht', 'Message', 'Message', 'Сообщение'),
    'f_subject': L('Betreff', 'Subject', 'Objet', 'Тема'),
    'f_brand': L('Hersteller', 'Manufacturer', 'Fabricant', 'Производитель'),
    'f_type': L('Gerätetyp', 'Device type', 'Type d’appareil', 'Тип аппарата'),
    'f_model': L('Modell', 'Model', 'Modèle', 'Модель'),
    'f_serial': L('Seriennummer', 'Serial number', 'Numéro de série', 'Серийный номер'),
    'f_photos': L('Fotos', 'Photos', 'Photos', 'Фото'),
    'f_onsite': L('Ansprechpartner vor Ort', 'Contact person on site', 'Interlocuteur sur place', 'Контактное лицо на месте'),
    'f_notes': L('Hinweis für den Kurier', 'Note for the courier', 'Remarque pour le coursier', 'Комментарий для курьера'),
    'f_date': L('Wunschtermin', 'Preferred date', 'Date souhaitée', 'Желаемая дата'),
    'f_time': L('Uhrzeit', 'Time of day', 'Moment de la journée', 'Время дня'),
    'morning': L('Vormittag', 'Morning', 'Matin', 'Первая половина дня'),
    'afternoon': L('Nachmittag', 'Afternoon', 'Après-midi', 'Вторая половина дня'),
    'brand_other': L('Anderer Hersteller', 'Other manufacturer', 'Autre fabricant', 'Другой производитель'),
    'brand_other_sub': L('z. B. Karl Storz', 'e.g. Karl Storz', 'p. ex. Karl Storz', 'например, Karl Storz'),
    'model_not_listed': L('Modell nicht in der Liste', 'Model not in the list', 'Modèle absent de la liste', 'Модели нет в списке'),
    'model_free': L('Modellbezeichnung', 'Model name', 'Désignation du modèle', 'Название модели'),
    'model_free_ph': L('wie auf dem Typenschild', 'as on the type plate', 'comme sur la plaque signalétique', 'как на шильдике'),
    'serial_hint': L('Steht auf dem Aufkleber am Geräteanschluss.', 'Printed on the label at the connector.', 'Indiqué sur l’étiquette du connecteur.', 'Указан на наклейке у разъёма.'),
    'photos_drop': L('Fotografieren oder Dateien auswählen', 'Take a photo or choose files', 'Prendre une photo ou choisir des fichiers', 'Сфотографировать или выбрать файлы'),
    'photos_hint': L('Bis zu 10 Fotos · JPG, PNG oder HEIC', 'Up to 10 photos · JPG, PNG or HEIC', 'Jusqu’à 10 photos · JPG, PNG ou HEIC', 'До 10 фото · JPG, PNG или HEIC'),
    'photo_remove': L('Foto entfernen', 'Remove photo', 'Supprimer la photo', 'Удалить фото'),
    'step_of': L('Schritt {n} von {total}', 'Step {n} of {total}', 'Étape {n} sur {total}', 'Шаг {n} из {total}'),
    'progress': L('Fortschritt', 'Progress', 'Progression', 'Прогресс'),
    'summary': L('Ihre Angaben', 'Your details', 'Vos informations', 'Ваши данные'),
    'to_home': L('Zur Startseite', 'Back to home', 'Retour à l’accueil', 'На главную'),
    'new_request': L('Neue Anfrage', 'New request', 'Nouvelle demande', 'Новый запрос'),
    'phone_hours': L('Telefonisch erreichbar', 'Phone hours', 'Joignable par téléphone', 'Часы работы телефона'),
    'opening_hours': L('Öffnungszeiten', 'Opening hours', 'Horaires', 'Часы работы'),
    'address': L('Adresse', 'Address', 'Adresse', 'Адрес'),
    'fax': L('Fax', 'Fax', 'Fax', 'Факс'),
    'faq': L('Häufige Fragen', 'Frequently asked questions', 'Questions fréquentes', 'Частые вопросы'),
    'faq_more': L('Ihre Frage ist nicht dabei? Rufen Sie uns an:', 'Your question isn’t listed? Call us:', 'Votre question n’y figure pas ? Appelez-nous :', 'Не нашли ответ? Позвоните нам:'),
    'breadcrumb': L('Brotkrumen', 'Breadcrumb', 'Fil d’Ariane', 'Навигационная цепочка'),
    'home': L('Startseite', 'Home', 'Accueil', 'Главная'),
    'f_date_ph': L('Datum wählen', 'Choose a date', 'Choisir une date', 'Выберите дату'),
    'price_on_request': L('Preis auf Anfrage', 'Price on request', 'Prix sur demande', 'Цена по запросу'),
    'price_note': L('Richtpreis zzgl. MwSt.', 'Guide price excl. VAT', 'Prix indicatif HT', 'Ориентир. цена без НДС'),
    'warranty_12': L('12 Monate Gewährleistung', '12-month warranty', 'Garantie 12 mois', 'Гарантия 12 месяцев'),
    'no_photo': L('Foto folgt', 'Photo to follow', 'Photo à venir', 'Фото скоро'),
    'iso_cert': L('Zertifiziert nach DIN EN ISO 9001:2015', 'Certified to DIN EN ISO 9001:2015', 'Certifié DIN EN ISO 9001:2015', 'Сертифицировано по DIN EN ISO 9001:2015'),
    'rights': L('Alle Rechte vorbehalten', 'All rights reserved', 'Tous droits réservés', 'Все права защищены'),
    'toc': L('Inhalt', 'Contents', 'Sommaire', 'Содержание'),
    'legal_lang_note': L('', 'This page is shown as published on scoperepair.de.',
                         'Ce texte juridique est affiché dans sa version anglaise publiée sur scoperepair.de. Seule la version allemande fait foi.',
                         'Юридический текст показан в английской версии с scoperepair.de. Юридическую силу имеет только немецкая версия.'),
    'mt_note': L('', '', 'Traduction automatique, à relire.', 'Машинный перевод, требует вычитки.'),
    'desc_lang_note': L('', '', 'Description disponible en anglais.', 'Описание доступно на английском.'),
    'cookie_h': L('Cookies auf dieser Website', 'Cookies on this website', 'Cookies sur ce site', 'Cookies на этом сайте'),
    'cookie_t': L('Wir verwenden technisch notwendige Cookies, damit die Seite funktioniert. Mit Ihrer Zustimmung nutzen wir zusätzlich Statistik-Cookies, um das Angebot zu verbessern.',
                  'We use technically necessary cookies so the site works. With your consent we also use statistics cookies to improve our service.',
                  'Nous utilisons des cookies techniquement nécessaires au fonctionnement du site. Avec votre accord, nous utilisons aussi des cookies statistiques pour améliorer notre offre.',
                  'Мы используем технически необходимые cookies для работы сайта. С вашего согласия — также статистические cookies, чтобы улучшать сервис.'),
    'cookie_all': L('Alle akzeptieren', 'Accept all', 'Tout accepter', 'Принять все'),
    'cookie_min': L('Nur notwendige', 'Necessary only', 'Uniquement nécessaires', 'Только необходимые'),
    'cookie_more': L('Datenschutzerklärung', 'Privacy policy', 'Politique de confidentialité', 'Политика конфиденциальности'),
    'cookie_title': L('Cookie-Einstellungen', 'Cookie settings', 'Paramètres des cookies', 'Настройки cookies'),
}

# ──────────────────────────────────────────────────────────────────────────
# Device vocabulary (from the live catalogue + the live forms)
# ──────────────────────────────────────────────────────────────────────────
TYPES = {
    'Gastroskop': L('Gastroskop', 'Gastroscope', 'Gastroscope', 'Гастроскоп'),
    'Koloskop': L('Koloskop', 'Colonoscope', 'Coloscope', 'Колоноскоп'),
    'Bronchoskop': L('Bronchoskop', 'Bronchoscope', 'Bronchoscope', 'Бронхоскоп'),
    'Duodenoskop': L('Duodenoskop', 'Duodenoscope', 'Duodénoscope', 'Дуоденоскоп'),
    'Zystoskop': L('Zystoskop', 'Cystoscope', 'Cystoscope', 'Цистоскоп'),
    'Ultraschallendoskop': L('Ultraschall-Endoskop', 'Ultrasound endoscope', 'Écho-endoscope', 'Ультразвуковой эндоскоп'),
    'Prozessor/Lichtquelle': L('Prozessor / Lichtquelle', 'Processor / light source', 'Processeur / source lumineuse', 'Процессор / источник света'),
    'HF-Chirurgiegerät': L('HF-Chirurgiegerät', 'Electrosurgical unit', 'Générateur électrochirurgical', 'Электрохирургический аппарат'),
}
TYPES_PLURAL = {
    'Gastroskop': L('Gastroskope', 'Gastroscopes', 'Gastroscopes', 'Гастроскопы'),
    'Koloskop': L('Koloskope', 'Colonoscopes', 'Coloscopes', 'Колоноскопы'),
    'Bronchoskop': L('Bronchoskope', 'Bronchoscopes', 'Bronchoscopes', 'Бронхоскопы'),
    'Duodenoskop': L('Duodenoskope', 'Duodenoscopes', 'Duodénoscopes', 'Дуоденоскопы'),
    'Zystoskop': L('Zystoskope', 'Cystoscopes', 'Cystoscopes', 'Цистоскопы'),
}
CONDITIONS = {
    'Generalüberholt': L('Generalüberholt', 'Refurbished', 'Révisé', 'Восстановлен'),
    'Sehr guter Gebrauchtzustand': L('Sehr guter Gebrauchtzustand', 'Very good used condition', 'Très bon état d’occasion', 'Очень хорошее б/у состояние'),
    'Guter Gebrauchtzustand': L('Guter Gebrauchtzustand', 'Good used condition', 'Bon état d’occasion', 'Хорошее б/у состояние'),
}
SPEC_LABELS = {
    'Einführschlauch': L('Einführungsschlauch', 'Insertion tube', 'Tube d’insertion', 'Вводная трубка'),
    'Arbeitskanal': L('Arbeitskanal', 'Working channel', 'Canal opérateur', 'Рабочий канал'),
    'Abwinkelung': L('Abwinkelung', 'Angulation', 'Béquillage', 'Изгиб'),
    'Optisches System': L('Optisches System', 'Optical system', 'Système optique', 'Оптическая система'),
    'Kompatibilität': L('Kompatibilität', 'Compatibility', 'Compatibilité', 'Совместимость'),
    'Sonstiges': L('Sonstiges', 'Additional information', 'Autres informations', 'Дополнительно'),
    'Lieferumfang': L('Lieferumfang', 'Scope of delivery', 'Contenu de la livraison', 'Комплект поставки'),
}
SPEC_HINT = {  # what the unlabeled values on the live site mean, in order
    'Einführschlauch': L('Ø · Arbeitslänge · Gesamtlänge', 'Ø · working length · total length', 'Ø · longueur utile · longueur totale', 'Ø · рабочая длина · общая длина'),
    'Abwinkelung': L('auf · ab · links · rechts', 'up · down · left · right', 'haut · bas · gauche · droite', 'вверх · вниз · влево · вправо'),
    'Optisches System': L('Blickfeld · Blickrichtung · Tiefenschärfe', 'field of view · direction · depth of field', 'champ de vision · direction · profondeur de champ', 'поле зрения · направление · глубина резкости'),
}
SPEC_VALUE_TR = {  # few textual values used in the catalogue
    '0° Geradeaus': L('0° Geradeaus', '0° forward viewing', '0° vision axiale', '0° прямой обзор'),
    '•': L('•', '•', '•', '•'),
}

# Defect categories (approved design)
DEFECTS = [
    ('bild', L('Bild unscharf oder dunkel', 'Image blurred or dark', 'Image floue ou sombre', 'Изображение размыто или тёмное'),
     L('Flecken, Streifen, kein Bild', 'Spots, stripes, no image', 'Taches, bandes, pas d’image', 'Пятна, полосы, нет изображения')),
    ('dicht', L('Undicht', 'Leaking', 'Non étanche', 'Негерметичен'),
     L('Dichtigkeitstest nicht bestanden', 'Leak test failed', 'Test d’étanchéité échoué', 'Не прошёл тест на герметичность')),
    ('abw', L('Abwinkelung schwergängig', 'Stiff angulation', 'Béquillage dur', 'Тугой изгиб'),
     L('Zu wenig Abwinkelung, Spiel am Rad', 'Too little angulation, play in the wheel', 'Béquillage insuffisant, jeu dans la molette', 'Недостаточный изгиб, люфт колеса')),
    ('kanal', L('Arbeitskanal verstopft', 'Working channel blocked', 'Canal opérateur obstrué', 'Рабочий канал засорён'),
     L('Instrumente gehen schwer durch', 'Instruments pass with difficulty', 'Les instruments passent difficilement', 'Инструменты проходят с трудом')),
    ('schlauch', L('Einführungsschlauch beschädigt', 'Insertion tube damaged', 'Tube d’insertion endommagé', 'Повреждена вводная трубка'),
     L('Knicke, Risse, Abwinkelungsgummi', 'Kinks, cracks, bending rubber', 'Plis, fissures, gaine de béquillage', 'Перегибы, трещины, резина изгиба')),
    ('sonst', L('Sonstiges', 'Other', 'Autre', 'Другое'),
     L('Bitte unten beschreiben', 'Please describe below', 'Veuillez décrire ci-dessous', 'Опишите ниже')),
]

# Device categories of the live pick-up and buy-back forms
FORM_DEVICE_TYPES = ['Gastroskop', 'Koloskop', 'Bronchoskop', 'Duodenoskop', 'Zystoskop', 'Ultraschallendoskop',
                     'Untersuchungsturm', 'Zubehör', 'Sonstiges']
FORM_DEVICE_TYPES_TR = {
    'Untersuchungsturm': L('Untersuchungsturm (komplett)', 'Endoscopy tower (complete)', 'Colonne d’endoscopie (complète)', 'Эндоскопическая стойка (полностью)'),
    'Zubehör': L('Zubehör', 'Accessories', 'Accessoires', 'Принадлежности'),
    'Sonstiges': L('Sonstiges', 'Other', 'Autre', 'Другое'),
}

CONTACT_SUBJECTS = [
    ('beratung', L('Beratungsanfrage', 'Consultation', 'Demande de conseil', 'Консультация')),
    ('kauf', L('Kaufanfrage', 'Purchase inquiry', 'Demande d’achat', 'Запрос на покупку')),
    ('reparatur', L('Reparaturanfrage', 'Repair inquiry', 'Demande de réparation', 'Запрос на ремонт')),
    ('anbieten', L('Gebrauchtes Gerät anbieten', 'Offer a used device', 'Proposer un appareil d’occasion', 'Предложить б/у аппарат')),
    ('anlage', L('Endoskopie-Anlage', 'Endoscopy system', 'Système d’endoscopie', 'Эндоскопическая система')),
    ('sonst', L('Sonstiges', 'Other', 'Autre', 'Другое')),
]

# ──────────────────────────────────────────────────────────────────────────
# Shared blocks
# ──────────────────────────────────────────────────────────────────────────
# Repair process — 7 steps exactly as described on /endoskop-reparatur-service/
REPAIR_STEPS = [
    {'icon': 'truck',
     't': L('Schadensmeldung / Abholauftrag', 'Damage report / pick-up order', 'Signalement / demande d’enlèvement', 'Заявка / заказ забора'),
     's': L('Sie melden den Schaden, wir holen das Gerät ab.', 'You report the damage, we collect the device.', 'Vous signalez le dommage, nous enlevons l’appareil.', 'Вы сообщаете о поломке, мы забираем аппарат.'),
     'l': L('Stellen Sie direkt einen Abholauftrag oder melden Sie den Schaden telefonisch oder per E-Mail. Bei sichtbaren Schäden hilft uns ein Foto. Während der Reparatur können Sie unseren Leihgeräte-Service nutzen.',
            'Place a pick-up order directly or report the damage by phone or e-mail. For visible damage, a photo helps us. During the repair you can use our loaner service.',
            'Passez directement une demande d’enlèvement ou signalez le dommage par téléphone ou e-mail. Pour un dommage visible, une photo nous aide. Pendant la réparation, vous pouvez utiliser notre service de prêt.',
            'Оформите заказ забора онлайн или сообщите о поломке по телефону или e-mail. При видимых повреждениях поможет фото. На время ремонта можно взять подменный аппарат.'),
     'm': None},
    {'icon': 'search',
     't': L('Analyse', 'Analysis', 'Analyse', 'Диагностика'),
     's': L('Detaillierte Schadensanalyse inklusive Dichtigkeitstest.', 'Detailed damage analysis including leak test.', 'Analyse détaillée, test d’étanchéité compris.', 'Подробная диагностика, включая тест на герметичность.'),
     'l': L('Nach dem Eingang führen wir eine detaillierte Schadensanalyse durch und prüfen verschiedene Kontrollpunkte. In einigen Fällen ist eine teilweise Demontage nötig, um alle Fehlfunktionen zu finden.',
            'Once the device arrives, we carry out a detailed damage analysis and check various control points. In some cases, partial disassembly is needed to identify all malfunctions.',
            'À réception, nous effectuons une analyse détaillée et contrôlons différents points. Un démontage partiel est parfois nécessaire pour identifier tous les défauts.',
            'После поступления мы проводим подробную диагностику по контрольным точкам. Иногда для поиска всех неисправностей нужна частичная разборка.'),
     'm': None},
    {'icon': 'doc',
     't': L('Kostenvoranschlag', 'Cost estimate', 'Devis', 'Смета'),
     's': L('Detailliert und unverbindlich.', 'Detailed and non-binding.', 'Détaillé et sans engagement.', 'Подробная и ни к чему не обязывающая.'),
     'l': L('Nach der Analyse erhalten Sie einen detaillierten, unverbindlichen Kostenvoranschlag. Wir beantworten alle Fragen zur Reparatur, damit Sie fundiert entscheiden können.',
            'After the analysis you receive a detailed, non-binding cost estimate. We answer all your questions so you can make an informed decision.',
            'Après l’analyse, vous recevez un devis détaillé et sans engagement. Nous répondons à toutes vos questions pour une décision éclairée.',
            'После диагностики вы получаете подробную смету без обязательств. Отвечаем на все вопросы, чтобы вы могли принять взвешенное решение.'),
     'm': L('unverbindlich', 'non-binding', 'sans engagement', 'без обязательств')},
    {'icon': 'check-doc',
     't': L('Ihre Freigabe', 'Your approval', 'Votre accord', 'Ваше согласие'),
     's': L('Wir reparieren erst nach Ihrer Zustimmung.', 'We only repair after you approve.', 'Nous réparons seulement après votre accord.', 'Ремонтируем только после вашего согласия.'),
     'l': L('Nach Erhalt des Kostenvoranschlags benötigen wir Ihre schriftliche Freigabe, per E-Mail oder Fax. Erst dann beginnt die Reparatur.',
            'After receiving the estimate, we need your written approval by e-mail or fax. Only then does the repair begin.',
            'Après réception du devis, nous avons besoin de votre accord écrit, par e-mail ou fax. La réparation ne commence qu’ensuite.',
            'Получив смету, вы подтверждаете её письменно — по e-mail или факсу. Только после этого начинается ремонт.'),
     'm': L('Sie entscheiden', 'You decide', 'Vous décidez', 'Решение за вами')},
    {'icon': 'wrench',
     't': L('Reparatur', 'Repair', 'Réparation', 'Ремонт'),
     's': L('Nur, was wirklich defekt ist.', 'Only what is actually broken.', 'Seulement ce qui est réellement défectueux.', 'Только то, что действительно сломано.'),
     'l': L('Unsere Techniker beginnen so schnell wie möglich. Bei Verfügbarkeit stellen wir ein kostenloses Leihgerät, Sie tragen nur die Versandkosten. Wir informieren Sie über den Fortschritt und die voraussichtliche Fertigstellung.',
            'Our technicians start as soon as possible. Subject to availability we provide a free loaner — you only pay shipping. We keep you updated on progress and expected completion.',
            'Nos techniciens commencent dès que possible. Selon disponibilité, nous prêtons un appareil gratuitement — seuls les frais d’envoi sont à votre charge. Nous vous informons de l’avancement.',
            'Техники приступают как можно скорее. При наличии предоставляем подменный аппарат бесплатно — вы оплачиваете только доставку. Сообщаем о ходе работ и сроке готовности.'),
     'm': None},
    {'icon': 'shield',
     't': L('Ausgangskontrolle', 'Final inspection', 'Contrôle final', 'Выходной контроль'),
     's': L('Mit dokumentiertem Prüfergebnis.', 'With documented test results.', 'Avec résultats documentés.', 'С документированным результатом.'),
     'l': L('Nach der Reparatur durchläuft Ihr Endoskop eine gründliche Abschlusskontrolle. Das Ergebnis erhalten Sie mit dem Gerät, es wird zusätzlich in unserem Archiv dokumentiert.',
            'After the repair, your endoscope undergoes a thorough final inspection. You receive the result with the device; it is also documented in our archive.',
            'Après la réparation, votre endoscope passe un contrôle final approfondi. Le résultat vous est remis avec l’appareil et archivé chez nous.',
            'После ремонта эндоскоп проходит тщательный выходной контроль. Результат вы получаете вместе с аппаратом, он также хранится в нашем архиве.'),
     'm': L('Prüfprotokoll', 'Test report', 'Rapport de test', 'Протокол проверки')},
    {'icon': 'box',
     't': L('Rückversand', 'Return shipping', 'Retour', 'Обратная доставка'),
     's': L('Per Expressversand zurück zu Ihnen.', 'Sent back by express.', 'Renvoyé en express.', 'Возвращаем экспресс-доставкой.'),
     'l': L('Wir senden Ihr Endoskop per Expressversand zurück. Die Rückholung eines Leihgeräts stimmen wir mit Ihnen ab, damit Sie Ihr Gerät vor dem nächsten Einsatz testen können.',
            'We send your endoscope back by express. We arrange collection of any loaner with you, so you have time to test your device before its next use.',
            'Nous renvoyons votre endoscope en express. Le retour de l’appareil de prêt est convenu avec vous, pour que vous puissiez tester votre appareil.',
            'Отправляем эндоскоп обратно экспресс-доставкой. Возврат подменного аппарата согласуем с вами, чтобы вы успели проверить свой.'),
     'm': L('Express', 'Express', 'Express', 'Экспресс')},
]

TRUST = [
    ('award', L('Zertifiziert nach ISO 9001:2015', 'ISO 9001:2015 certified', 'Certifié ISO 9001:2015', 'Сертификат ISO 9001:2015')),
    ('clock', L('Erfahrung im Team seit 2010', 'Team experience since 2010', 'Expérience de l’équipe depuis 2010', 'Опыт команды с 2010 года')),
    ('shield', L('12 Monate Gewährleistung auf Gebrauchtgeräte', '12-month warranty on used devices', 'Garantie 12 mois sur l’occasion', '12 месяцев гарантии на б/у')),
    ('box', L('Leihgeräte ab Lager', 'Loaners from stock', 'Appareils de prêt en stock', 'Подменные аппараты со склада')),
]

# Figures stated on the live site (repair page, FAQ, about page)
FIGURES = [
    {'num': '95', 'pre': L('über', 'over', 'plus de', 'более'), 'unit': '%',
     'label': L('erfolgreich gelöste Schadensfälle', 'of damage cases solved', 'de pannes résolues', 'успешно решённых случаев')},
    {'num': '2010', 'pre': L('seit', 'since', 'depuis', 'с'), 'unit': '',
     'label': L('Erfahrung im Team mit flexiblen Endoskopen', 'team experience with flexible endoscopes', 'd’expérience de l’équipe en endoscopie souple', 'опыт команды с гибкими эндоскопами')},
    {'num': '12', 'pre': None, 'unit': L('Monate', 'months', 'mois', 'мес.'),
     'label': L('Gewährleistung auf generalüberholte Endoskope', 'warranty on refurbished endoscopes', 'de garantie sur les endoscopes révisés', 'гарантии на восстановленные эндоскопы')},
    {'num': '6', 'pre': None, 'unit': L('Monate', 'months', 'mois', 'мес.'),
     'label': L('Gewährleistung auf jede Reparatur', 'warranty on every repair', 'de garantie sur chaque réparation', 'гарантии на каждый ремонт')},
]

# ──────────────────────────────────────────────────────────────────────────
# FAQ — DE/EN verbatim from the live site, FR/RU translated
# (indices refer to data/faq_live.json)
# ──────────────────────────────────────────────────────────────────────────
FAQ_PICK = {
    'home': [0, 1, 2, 3, 4, 5, 6],
    'repair': [1, 2, 3, 5, 8, 9, 10, 0],
    'used': [0, 1, 5, 6, 8, 9],
    'buy': [0, 1, 2, 4, 6, 8],
    'systems': [0, 2, 3, 4, 5, 7],
    'loaner': [('repair', 4), ('home', 6)],
}

FAQ_TR = {
    'home': {
        'fr': [
            ['Que représente scopeREPAIR ?', 'Spécialiste indépendant des fabricants, scopeREPAIR assure la réparation, la maintenance et la vente d’endoscopes médicaux souples. Grâce à une longue expérience et à un système de management de la qualité certifié DIN EN ISO 9001:2015, nous accompagnons hôpitaux, cliniques et cabinets avec des solutions économiques, durables et multimarques.'],
            ['Quels endoscopes scopeREPAIR répare-t-il ?', 'Nous réparons et entretenons les endoscopes souples des grandes marques Olympus, Pentax et Fujinon : gastroscopes, coloscopes, bronchoscopes, cystoscopes et duodénoscopes.'],
            ['Pourquoi une réparation professionnelle sans contrat de maintenance est-elle rentable ?', 'Notre philosophie : les réparations nécessaires plutôt que des coûts fixes inutiles. Une remise en état professionnelle prolonge la durée de vie de votre équipement, réduit les investissements et constitue une alternative économique aux contrats de maintenance. Nous ne remplaçons que les composants réellement défectueux.'],
            ['scopeREPAIR propose-t-il aussi des endoscopes d’occasion ?', 'Notre gamme comprend des endoscopes révisés et contrôlés ainsi que des systèmes d’endoscopie complets de fabricants réputés. Pour plus de sécurité, vous bénéficiez de 12 mois de garantie à l’achat d’un endoscope d’occasion.'],
            ['Utilisez-vous des pièces d’origine pour la remise en état ?', 'Pour chaque remise en état, scopeREPAIR utilise exclusivement des pièces de haute qualité. Cela garantit un fonctionnement fiable, une grande sécurité et une longue durée d’utilisation.'],
            ['Comment se déroule le service de réparation ?', 'Simplement et en toute transparence : vous passez une demande d’enlèvement ou nous contactez pour un conseil personnalisé. Après l’analyse technique, vous recevez un devis détaillé. La réparation n’a lieu qu’après votre accord.'],
            ['Proposez-vous des appareils de prêt pendant la réparation ?', 'Oui. Pour limiter l’indisponibilité dans votre cabinet ou votre hôpital, nous mettons à disposition, selon disponibilité, un appareil de remplacement adapté issu de notre parc de prêt.'],
        ],
        'ru': [
            ['Что такое scopeREPAIR?', 'scopeREPAIR — независимый от производителей специалист по ремонту, обслуживанию и продаже гибких медицинских эндоскопов. Многолетний опыт и система менеджмента качества по DIN EN ISO 9001:2015 позволяют нам предлагать клиникам, больницам и практикам экономичные, долговечные и мультибрендовые решения.'],
            ['Какие эндоскопы ремонтирует scopeREPAIR?', 'Мы ремонтируем и обслуживаем гибкие эндоскопы ведущих марок Olympus, Pentax и Fujinon: гастроскопы, колоноскопы, бронхоскопы, цистоскопы и дуоденоскопы.'],
            ['Почему выгоден ремонт без сервисного договора?', 'Наш принцип — необходимый ремонт вместо лишних постоянных расходов. Профессиональный ремонт продлевает срок службы техники, снижает затраты на закупку и служит экономичной альтернативой долгосрочным договорам. Мы меняем только действительно неисправные компоненты.'],
            ['Продаёт ли scopeREPAIR б/у эндоскопы?', 'В ассортименте — проверенные восстановленные эндоскопы и полные эндоскопические системы известных производителей. При покупке б/у эндоскопа вы получаете 12 месяцев гарантии.'],
            ['Используются ли оригинальные запчасти?', 'При каждом ремонте scopeREPAIR использует только качественные запчасти. Это обеспечивает надёжную работу, безопасность и долгий срок службы.'],
            ['Как проходит ремонт?', 'Просто и прозрачно: вы оформляете заказ забора или связываетесь с нами для консультации. После технической диагностики вы получаете подробную смету. Ремонт начинается только после вашего согласия.'],
            ['Есть ли подменные аппараты на время ремонта?', 'Да. Чтобы свести простой к минимуму, на время ремонта мы предоставляем подходящий аппарат из нашего подменного фонда — при наличии.'],
        ],
    },
    'repair': {
        'fr': [
            ['Comment se déroule une réparation d’endoscope ?', 'Après votre signalement, nous organisons l’enlèvement de l’endoscope sur demande. Suit une analyse minutieuse, test d’étanchéité compris. Vous recevez un devis transparent. La réparation suit des standards de qualité stricts avec des procédures de test validées, puis un contrôle final de sécurité et de fonctionnement avant le renvoi.'],
            ['Combien de temps dure une réparation ?', 'La durée dépend du dommage et de la disponibilité des pièces. Après votre accord, nos techniciens commencent dès que possible. Notre objectif : réduire au minimum l’indisponibilité de vos endoscopes.'],
            ['Proposez-vous un service d’enlèvement ?', 'Oui. Nous organisons l’enlèvement de votre endoscope défectueux, vous n’avez pas à gérer l’envoi. Après la réparation, nous vous le renvoyons.'],
            ['Quelle garantie ai-je sur la réparation ?', 'Toutes nos réparations d’endoscopes sont garanties 6 mois. La garantie couvre les défauts corrigés lors de la réparation.'],
            ['Dois-je signer un contrat de maintenance ?', 'Non. Aucun contrat n’est nécessaire pour une réparation. Nous ne réparons que les composants réellement nécessaires, de façon transparente et sans frais cachés.'],
            ['Recevrai-je une documentation de la réparation ?', 'Oui. Chaque endoscope passe un contrôle de sortie complet. Le résultat est documenté et remis avec l’appareil.'],
            ['Que se passe-t-il si une réparation n’est plus rentable ?', 'Si une réparation n’est pas économiquement pertinente, nous vous conseillons en toute transparence sur les alternatives. Sur demande, nous proposons des endoscopes révisés avec 12 mois de garantie.'],
            ['Quels endoscopes réparez-vous ?', 'Nous réparons les endoscopes souples de tous les fabricants courants, en particulier Olympus, Pentax, Fujinon et Storz, ainsi que ceux d’autres fabricants.'],
        ],
        'ru': [
            ['Как проходит ремонт эндоскопа?', 'После заявки мы по желанию организуем забор эндоскопа. Затем — тщательная диагностика, включая тест на герметичность. Вы получаете прозрачную смету. Ремонт выполняется по строгим стандартам с валидированными методами проверки, после чего — финальная проверка безопасности и работы перед отправкой.'],
            ['Сколько длится ремонт?', 'Срок зависит от характера поломки и наличия запчастей. После вашего согласия техники приступают как можно скорее. Наша цель — минимальный простой ваших эндоскопов.'],
            ['Есть ли услуга забора?', 'Да. Мы организуем забор неисправного эндоскопа, вам не нужно заниматься отправкой. После ремонта возвращаем аппарат.'],
            ['Какая гарантия на ремонт?', 'На все выполненные ремонты эндоскопов — 6 месяцев гарантии. Она распространяется на устранённые при ремонте неисправности.'],
            ['Нужен ли сервисный договор?', 'Нет. Для ремонта договор не нужен. Мы ремонтируем только действительно необходимые компоненты — прозрачно, экономично и без скрытых расходов.'],
            ['Получу ли я документацию по ремонту?', 'Да. После ремонта каждый эндоскоп проходит полный выходной контроль. Результат документируется и передаётся вместе с аппаратом.'],
            ['Что, если ремонт уже невыгоден?', 'Если ремонт экономически нецелесообразен, мы честно расскажем об альтернативах. По желанию предложим восстановленные эндоскопы с гарантией 12 месяцев.'],
            ['Какие эндоскопы вы ремонтируете?', 'Гибкие эндоскопы всех распространённых производителей, особенно Olympus, Pentax, Fujinon и Storz, а также других марок.'],
        ],
    },
    'used': {
        'fr': [
            ['Qu’est-ce qu’un endoscope révisé (reconditionné) ?', 'Un endoscope révisé a déjà été utilisé en milieu médical, puis entièrement contrôlé, remis en état et retravaillé techniquement par nos techniciens. Les pièces d’usure sont remplacées et chaque appareil est testé avant la vente.'],
            ['Vos endoscopes d’occasion sont-ils sûrs et contrôlés ?', 'Oui. Tous nos endoscopes d’occasion passent par un processus de reconditionnement en plusieurs étapes. Chaque appareil est révisé techniquement et visuellement, puis entièrement testé.'],
            ['Ai-je une garantie sur les endoscopes d’occasion ?', 'Oui. Tous les endoscopes révisés sont garantis 12 mois, pour une plus grande sécurité d’investissement.'],
            ['Peuvent-ils être intégrés à mon équipement existant ?', 'Oui. Nous vérifions la compatibilité avec votre équipement d’endoscopie et vous conseillons dans le choix des endoscopes et composants adaptés, afin d’éviter des coûts supplémentaires.'],
            ['Puis-je aussi acheter des systèmes d’endoscopie complets ?', 'Oui. En plus des endoscopes, nous proposons des systèmes complets adaptés à vos besoins : endoscopes, processeurs vidéo, sources lumineuses, moniteurs et accessoires.'],
            ['scopeREPAIR rachète-t-il aussi des appareils usagés ?', 'Oui. Nous rachetons ou reprenons les endoscopes usagés, anciens ou défectueux, pour aider cliniques et cabinets à moderniser leur parc.'],
        ],
        'ru': [
            ['Что такое восстановленный (refurbished) эндоскоп?', 'Это эндоскоп, который уже использовался в медицине, а затем был полностью проверен, отремонтирован и технически доработан нашими техниками. Изнашиваемые детали заменяются, каждый аппарат тестируется перед продажей.'],
            ['Безопасны ли ваши б/у эндоскопы?', 'Да. Все б/у эндоскопы проходят многоэтапную подготовку: техническое и визуальное восстановление и полную проверку работоспособности.'],
            ['Есть ли гарантия на б/у эндоскопы?', 'Да. На все восстановленные эндоскопы — 12 месяцев гарантии.'],
            ['Можно ли подключить их к имеющемуся оборудованию?', 'Да. Мы проверяем совместимость с вашим оборудованием и помогаем подобрать подходящие эндоскопы и компоненты, чтобы избежать лишних расходов.'],
            ['Можно ли купить полную эндоскопическую систему?', 'Да. Кроме отдельных эндоскопов, мы предлагаем полные системы под ваши задачи: эндоскопы, видеопроцессоры, источники света, мониторы и принадлежности.'],
            ['Выкупаете ли вы старые аппараты?', 'Да. Мы выкупаем или принимаем в зачёт б/у, старые и неисправные эндоскопы, помогая клиникам и практикам обновлять парк.'],
        ],
    },
    'buy': {
        'fr': [
            ['Quels endoscopes scopeREPAIR rachète-t-il ?', 'Nous rachetons des endoscopes souples et de l’équipement d’endoscopie de différents fabricants, notamment Olympus, Pentax, Fujinon et Storz, ainsi que des composants comme processeurs vidéo, sources lumineuses et accessoires.'],
            ['Rachetez-vous aussi des endoscopes défectueux ?', 'Oui. Les endoscopes défectueux, anciens ou incomplets peuvent nous intéresser. Nous évaluons chaque appareil selon son état, son modèle, le coût de remise en état et les composants présents.'],
            ['Quels appareils puis-je vous vendre ?', 'Outre les endoscopes souples : processeurs vidéo, sources lumineuses, moniteurs, chariots d’endoscopie, pompes d’aspiration et accessoires.'],
            ['Comment la valeur de mon endoscope est-elle déterminée ?', 'Selon le fabricant, le modèle, l’état technique, l’âge, l’équipement, les accessoires et l’effort de reconditionnement. Nous estimons ainsi la valeur de marché réelle de votre appareil.'],
            ['Puis-je vendre plusieurs endoscopes ou tout un parc ?', 'Oui. Nous examinons volontiers l’ensemble de votre équipement. Pour les parcs importants, une évaluation sur place est possible.'],
            ['Puis-je échanger mon ancien endoscope contre un autre appareil ?', 'Oui. Dans le cadre de la modernisation de votre parc, nous étudions une reprise : la valeur de votre équipement est déduite à l’achat d’un appareil révisé.'],
        ],
        'ru': [
            ['Какие эндоскопы выкупает scopeREPAIR?', 'Мы выкупаем б/у гибкие эндоскопы и эндоскопическую технику разных производителей — прежде всего Olympus, Pentax, Fujinon и Storz, а также видеопроцессоры, источники света и принадлежности.'],
            ['Выкупаете ли вы неисправные эндоскопы?', 'Да. Нам интересны и неисправные, старые или некомплектные аппараты. Каждый оцениваем индивидуально с учётом состояния, модели, объёма ремонта и комплектации.'],
            ['Какие аппараты можно продать?', 'Кроме гибких эндоскопов — видеопроцессоры, источники света, мониторы, эндоскопические тележки, аспираторы и принадлежности.'],
            ['Как определяется стоимость?', 'По производителю, модели, техническому состоянию, возрасту, комплектации, принадлежностям и объёму подготовки. Так мы реалистично оцениваем рыночную стоимость.'],
            ['Можно ли продать несколько аппаратов или весь парк?', 'Да. Охотно оценим всё оборудование. Для крупных партий возможна оценка на месте.'],
            ['Можно ли обменять старый эндоскоп на другой?', 'Да. При обновлении парка мы рассматриваем приём в зачёт: стоимость вашего аппарата учитывается при покупке восстановленного.'],
        ],
    },
    'systems': {
        'fr': [
            ['Que comprend un système d’endoscopie ?', 'Tous les composants nécessaires à un examen endoscopique professionnel : processeur vidéo, source lumineuse, moniteur, endoscopes souples et accessoires adaptés. Nous composons volontiers un système adapté à vos besoins.'],
            ['Les systèmes d’occasion sont-ils une alternative fiable au neuf ?', 'Oui. Tous les systèmes sont contrôlés techniquement et testés avant livraison. Ils constituent une alternative économique au neuf, avec des standards de qualité élevés.'],
            ['Ai-je une garantie sur les systèmes révisés ?', 'Oui. Nos systèmes d’occasion sont garantis 6 à 12 mois.'],
            ['Mes endoscopes existants peuvent-ils être intégrés ?', 'Souvent, oui. Nous vérifions la compatibilité de vos endoscopes et composants et vous conseillons pour une intégration optimale.'],
            ['scopeREPAIR aide-t-il à planifier un système ?', 'Oui. Nous vous conseillons indépendamment des fabricants et élaborons avec vous une solution sur mesure, du composant isolé à l’équipement complet.'],
            ['Proposez-vous l’installation et la formation ?', 'Oui. Sur demande, nous assurons l’installation, la mise en service et la formation de votre personnel.'],
        ],
        'ru': [
            ['Что входит в эндоскопическую систему?', 'Все компоненты для профессионального эндоскопического исследования: видеопроцессор, источник света, монитор, гибкие эндоскопы и принадлежности. Соберём систему под ваши задачи.'],
            ['Надёжны ли б/у системы по сравнению с новыми?', 'Да. Все системы проходят техническую проверку и тестирование перед поставкой. Это экономичная альтернатива новым при высоких стандартах качества.'],
            ['Есть ли гарантия на восстановленные системы?', 'Да. На б/у эндоскопические системы — от 6 до 12 месяцев гарантии.'],
            ['Можно ли интегрировать имеющиеся эндоскопы?', 'Во многих случаях — да. Мы проверим совместимость и подскажем, как лучше встроить их в новую или существующую систему.'],
            ['Помогаете ли вы спланировать систему?', 'Да. Консультируем независимо от производителей и вместе с вами разрабатываем решение — от отдельных компонентов до полного оснащения.'],
            ['Выполняете ли вы монтаж и обучение?', 'Да. По желанию выполняем монтаж, ввод в эксплуатацию и инструктаж персонала.'],
        ],
    },
}

# ──────────────────────────────────────────────────────────────────────────
# Page copy
# ──────────────────────────────────────────────────────────────────────────
FAQ_TR['loaner'] = {
    'fr': [
        ['Puis-je obtenir un appareil de prêt pendant la réparation ?', 'Oui. Pour réduire l’indisponibilité dans votre clinique ou cabinet, nous mettons à disposition des endoscopes de prêt compatibles pendant la réparation. La disponibilité dépend du modèle.'],
        FAQ_TR['home']['fr'][6],
    ],
    'ru': [
        ['Можно ли получить подменный аппарат на время ремонта?', 'Да. Чтобы сократить простой в клинике или практике, на время ремонта мы предоставляем совместимые подменные эндоскопы. Наличие зависит от модели.'],
        FAQ_TR['home']['ru'][6],
    ],
}

P = {}

P['index'] = {
    'title': L('Endoskop-Reparatur, Verkauf und Ankauf', 'Endoscope repair, sales and buy-back', 'Réparation, vente et rachat d’endoscopes', 'Ремонт, продажа и выкуп эндоскопов'),
    'h1': L('Endoskop defekt? Wir reparieren – ohne Servicevertrag.', 'Endoscope broken? We repair it – no service contract.',
            'Endoscope en panne ? Nous le réparons – sans contrat de service.', 'Эндоскоп сломался? Отремонтируем — без сервисного договора.'),
    'lead': L('Unabhängiger Service für Olympus, Pentax und Fujinon. Kostenvoranschlag vor jeder Reparatur, Leihgerät auf Wunsch.',
              'Independent service for Olympus, Pentax and Fujinon. A cost estimate before every repair, a loaner on request.',
              'Service indépendant pour Olympus, Pentax et Fujinon. Un devis avant chaque réparation, un appareil de prêt sur demande.',
              'Независимый сервис для Olympus, Pentax и Fujinon. Смета перед каждым ремонтом, подменный аппарат по запросу.'),
    'scenarios': [
        {'id': 'reparatur-auftrag', 'icon': 'wrench', 'primary': True,
         't': L('Reparatur beauftragen', 'Order a repair', 'Commander une réparation', 'Заказать ремонт'),
         's': L('Abholung in wenigen Minuten beauftragen', 'Book a pick-up in a few minutes', 'Demander l’enlèvement en quelques minutes', 'Оформите забор за несколько минут')},
        {'id': 'leihgeraete', 'icon': 'swap',
         't': L('Leihgerät anfragen', 'Request a loaner', 'Demander un appareil de prêt', 'Подменный аппарат'),
         's': L('Arbeiten Sie weiter, während wir reparieren', 'Keep working while we repair', 'Continuez à travailler pendant la réparation', 'Работайте, пока мы ремонтируем')},
        {'id': 'gebrauchte-endoskope', 'icon': 'cart',
         't': L('Endoskop kaufen', 'Buy an endoscope', 'Acheter un endoscope', 'Купить эндоскоп'),
         's': L('Generalüberholt, 12 Monate Gewährleistung', 'Refurbished, 12-month warranty', 'Révisé, garantie 12 mois', 'Восстановленные, гарантия 12 месяцев')},
        {'id': 'ankauf', 'icon': 'tag',
         't': L('Endoskop verkaufen', 'Sell an endoscope', 'Vendre un endoscope', 'Продать эндоскоп'),
         's': L('Auch defekt oder demontiert', 'Even defective or disassembled', 'Même défectueux ou démonté', 'Даже неисправный или разобранный')},
    ],
    'band_t': L('Schnelle Hilfe bei einem Defekt?', 'Need help with a defect fast?', 'Besoin d’aide rapide pour une panne ?', 'Нужна быстрая помощь при поломке?'),
    'band_s': L('Rufen Sie direkt in der Werkstatt an. Wir klären das Vorgehen am Telefon.', 'Call the workshop directly. We’ll sort out the next steps on the phone.',
                'Appelez directement l’atelier. Nous définissons la suite au téléphone.', 'Позвоните прямо в мастерскую — договоримся обо всём по телефону.'),
    'process_o': L('So läuft die Reparatur', 'How the repair works', 'Déroulement de la réparation', 'Как проходит ремонт'),
    'process_h': L('Sieben Schritte – und das Gerät ist wieder in Ihrer Praxis', 'Seven steps – and the device is back in your practice',
                   'Sept étapes – et l’appareil revient dans votre cabinet', 'Семь шагов — и аппарат снова у вас'),
    'process_s': L('Sie wissen immer, was als Nächstes passiert. Repariert wird erst nach Ihrer Freigabe.', 'You always know what happens next. We only repair once you approve.',
                   'Vous savez toujours ce qui se passe ensuite. Nous réparons seulement après votre accord.', 'Вы всегда знаете, что дальше. Ремонт — только после вашего согласия.'),
    'principle_o': L('Unser Prinzip', 'Our principle', 'Notre principe', 'Наш принцип'),
    'principle_h1': L('Wir reparieren, was kaputt ist.', 'We repair what is broken.', 'Nous réparons ce qui est cassé.', 'Ремонтируем то, что сломано.'),
    'principle_h2': L('Nicht mehr.', 'Nothing more.', 'Rien de plus.', 'Не больше.'),
    'principle_a_o': L('Üblich', 'Usual', 'Habituel', 'Обычно'),
    'principle_a_t': L('Servicevertrag', 'Service contract', 'Contrat de service', 'Сервисный договор'),
    'principle_a': [L('Feste Kosten – auch wenn nichts kaputt ist', 'Fixed costs – even when nothing is broken', 'Coûts fixes – même sans panne', 'Постоянные расходы — даже без поломок'),
                    L('Bindung über die Vertragslaufzeit', 'Tied in for the contract term', 'Engagement sur la durée du contrat', 'Обязательства на весь срок договора'),
                    L('Pauschalen für Leistungen, die Sie vielleicht nie brauchen', 'Flat fees for services you may never need', 'Forfaits pour des services dont vous n’aurez peut-être jamais besoin', 'Оплата услуг, которые могут не понадобиться')],
    'principle_b_o': L('Mit uns', 'With us', 'Avec nous', 'С нами'),
    'principle_b': [L('Sie zahlen nur die nötige Reparatur', 'You only pay for the repair you need', 'Vous ne payez que la réparation nécessaire', 'Платите только за нужный ремонт'),
                    L('Erst der Kostenvoranschlag – Sie entscheiden', 'Cost estimate first – you decide', 'D’abord le devis – vous décidez', 'Сначала смета — решаете вы'),
                    L('Kein Wartungsvertrag nötig', 'No maintenance contract required', 'Aucun contrat de maintenance nécessaire', 'Сервисный договор не нужен')],
    'principle_cta': L('Wie viel spart Ihre Praxis? Zum Rechner', 'How much does your practice save? Open the calculator', 'Combien votre cabinet économise-t-il ? Calculateur', 'Сколько сэкономит ваша практика? К калькулятору'),
    'used_o': L('Gebrauchte Endoskope', 'Used endoscopes', 'Endoscopes d’occasion', 'Б/у эндоскопы'),
    'used_h': L('Generalüberholte Endoskope ab Lager', 'Refurbished endoscopes from stock', 'Endoscopes révisés en stock', 'Восстановленные эндоскопы со склада'),
    'tradein_t': L('Altgerät in Zahlung geben', 'Trade in your old device', 'Faire reprendre votre ancien appareil', 'Сдать старый аппарат в зачёт'),
    'tradein_s': L('Nach einer Begutachtung verrechnen wir den Restwert mit Ihrem neuen Gerät.', 'After an assessment we credit the residual value against your new device.',
                   'Après expertise, nous déduisons la valeur résiduelle de votre nouvel appareil.', 'После оценки зачтём остаточную стоимость в цену нового аппарата.'),
    'tradein_cta': L('Altgerät bewerten lassen', 'Get your device valued', 'Faire évaluer l’appareil', 'Оценить аппарат'),
    'workshop_o': L('Werkstatt statt Callcenter', 'A workshop, not a call centre', 'Un atelier, pas un centre d’appels', 'Мастерская, а не колл-центр'),
    'workshop_h': L('Echte Technik, echte Menschen', 'Real technology, real people', 'Vraie technique, vraies personnes', 'Настоящая техника, живые люди'),
    'workshop_cap1': L('Reparatur flexibler Endoskope', 'Repair of flexible endoscopes', 'Réparation d’endoscopes souples', 'Ремонт гибких эндоскопов'),
    'workshop_cap2': L('Generalüberholt und geprüft', 'Refurbished and tested', 'Révisé et contrôlé', 'Восстановлен и проверен'),
    'brands_o': L('Hersteller und Typen', 'Manufacturers and types', 'Fabricants et types', 'Производители и типы'),
    'brands_h': L('Was wir aktuell auf Lager haben', 'What we currently have in stock', 'Ce que nous avons actuellement en stock', 'Что сейчас есть на складе'),
    'brands_s': L('Geräte im Katalog nach Hersteller und Typ. Reparieren können wir alle gängigen Modelle.', 'Devices in the catalogue by manufacturer and type. We can repair all common models.',
                  'Appareils au catalogue par fabricant et type. Nous réparons tous les modèles courants.', 'Аппараты в каталоге по производителю и типу. Ремонтируем все распространённые модели.'),
    'contact_h': L('Fragen? Rufen Sie uns direkt an.', 'Questions? Call us directly.', 'Des questions ? Appelez-nous directement.', 'Вопросы? Звоните напрямую.'),
}

P['reparatur'] = {
    'title': L('Endoskop-Reparatur', 'Endoscope repair', 'Réparation d’endoscopes', 'Ремонт эндоскопов'),
    'o': L('Endoskop-Reparatur-Service', 'Endoscope repair service', 'Service de réparation d’endoscopes', 'Сервис ремонта эндоскопов'),
    'h1': L('Reparatur flexibler Endoskope für Kliniken und Praxen', 'Flexible endoscope repair for hospitals and practices',
            'Réparation d’endoscopes souples pour hôpitaux et cabinets', 'Ремонт гибких эндоскопов для клиник и практик'),
    'lead': L('Herstellerunabhängig für Olympus, Pentax, Fujinon und Storz. Mit Kostenvoranschlag vor jeder Reparatur und 6 Monaten Gewährleistung.',
              'Manufacturer-independent for Olympus, Pentax, Fujinon and Storz. A cost estimate before every repair and a 6-month warranty.',
              'Indépendamment des fabricants pour Olympus, Pentax, Fujinon et Storz. Un devis avant chaque réparation et 6 mois de garantie.',
              'Независимо от производителя: Olympus, Pentax, Fujinon и Storz. Смета перед каждым ремонтом и 6 месяцев гарантии.'),
    'facts': [
        ('percent', L('über 95 %', 'over 95 %', 'plus de 95 %', 'более 95 %'), L('erfolgreich gelöste Schadensfälle', 'of damage cases solved', 'de pannes résolues', 'успешно решённых случаев')),
        ('shield', L('6 Monate', '6 months', '6 mois', '6 месяцев'), L('Gewährleistung auf die Reparatur', 'warranty on the repair', 'de garantie sur la réparation', 'гарантии на ремонт')),
        ('doc', L('Prüfprotokoll', 'Test report', 'Rapport de test', 'Протокол'), L('nach jeder Reparatur', 'after every repair', 'après chaque réparation', 'после каждого ремонта')),
    ],
    'intro_h': L('Ihr Partner für Endoskop-Reparaturen', 'Your partner for endoscope repairs', 'Votre partenaire pour la réparation d’endoscopes', 'Ваш партнёр по ремонту эндоскопов'),
    'intro': [
        L('Wir bieten Reparatur, Wartung und Aufbereitung für Arztpraxen und Kliniken im In- und Ausland. Langjährige Erfahrung mit Endoskopie-Systemen und strukturierte Prozesse sorgen für eine zuverlässige Betreuung.',
          'We offer repair, maintenance and reprocessing for practices and hospitals in Germany and abroad. Years of experience with endoscopy systems and structured processes ensure reliable support.',
          'Nous assurons réparation, maintenance et reconditionnement pour cabinets et cliniques en Allemagne et à l’étranger. Notre expérience des systèmes d’endoscopie et des processus structurés garantissent un suivi fiable.',
          'Мы выполняем ремонт, обслуживание и подготовку эндоскопов для практик и клиник в Германии и за рубежом. Многолетний опыт и чёткие процессы обеспечивают надёжный сервис.'),
        L('Unser Fokus liegt auf wirtschaftlichen und nachhaltigen Lösungen: teure Neuanschaffungen vermeiden und die Verfügbarkeit Ihrer Geräte sichern. Dafür setzen wir geeignete, hochwertige Ersatzteile ein.',
          'Our focus is on economical and sustainable solutions: avoiding costly new purchases and keeping your devices available. We use suitable, high-quality spare parts.',
          'Nous privilégions des solutions économiques et durables : éviter des achats coûteux et garantir la disponibilité de vos appareils, avec des pièces de haute qualité.',
          'Мы делаем ставку на экономичные и долговечные решения: избежать дорогих закупок и сохранить доступность техники. Используем подходящие качественные запчасти.'),
    ],
    'process_h': L('Ablauf einer Endoskop-Reparatur', 'How an endoscope repair works', 'Déroulement d’une réparation', 'Как проходит ремонт эндоскопа'),
    'loaner_t': L('Reibungslose Abläufe dank Leihgeräten', 'Smooth operations thanks to loaners', 'Fonctionnement fluide grâce au prêt', 'Без простоя благодаря подменным аппаратам'),
    'loaner_s': L('Bei Bedarf stellen wir schnell und unkompliziert ein Leihgerät zur Verfügung – kostenlos bei Verfügbarkeit, Sie tragen nur die Versandkosten.',
                  'If needed, we quickly provide a loaner – free of charge subject to availability; you only pay shipping.',
                  'Si nécessaire, nous prêtons rapidement un appareil – gratuitement selon disponibilité, seuls les frais d’envoi sont à votre charge.',
                  'При необходимости быстро предоставим подменный аппарат — бесплатно при наличии, вы оплачиваете только доставку.'),
    'swap_t': L('Austausch statt Reparatur', 'Replace instead of repair', 'Remplacer plutôt que réparer', 'Замена вместо ремонта'),
    'swap_s': L('Lohnt sich eine Reparatur nicht mehr, bieten wir generalüberholte Endoskope mit 12 Monaten Gewährleistung an.',
                'If a repair is no longer worthwhile, we offer refurbished endoscopes with a 12-month warranty.',
                'Si une réparation n’est plus rentable, nous proposons des endoscopes révisés avec 12 mois de garantie.',
                'Если ремонт невыгоден, предложим восстановленный эндоскоп с гарантией 12 месяцев.'),
    'call_t': L('Fragen zum Ablauf? Rufen Sie uns an.', 'Questions about the process? Call us.', 'Des questions sur le déroulement ? Appelez-nous.', 'Вопросы о процессе? Позвоните нам.'),
}

P['reparatur-auftrag'] = {
    'title': L('Abholauftrag', 'Pick-up order', 'Demande d’enlèvement', 'Заказ забора'),
    'h1': L('Abholauftrag', 'Pick-up order', 'Demande d’enlèvement', 'Заказ забора'),
    'lead': L('Wir prüfen Ihre Anfrage umgehend: Kommt ein Techniker zur Fehleranalyse oder holt ein Kurier das Gerät ab? Danach erhalten Sie einen Kostenvoranschlag.',
              'We review your request right away: will a technician come for analysis, or will a courier collect the device? You then receive a cost estimate.',
              'Nous examinons votre demande sans attendre : un technicien vient-il pour l’analyse ou un coursier enlève-t-il l’appareil ? Vous recevez ensuite un devis.',
              'Мы сразу рассмотрим заявку: приедет техник для диагностики или курьер заберёт аппарат. Затем вы получите смету.'),
    'steps': [L('Gerät', 'Device', 'Appareil', 'Аппарат'), L('Defekt', 'Defect', 'Panne', 'Поломка'), L('Leihgerät', 'Loaner', 'Prêt', 'Подмена'),
              L('Abholung', 'Pick-up', 'Enlèvement', 'Забор'), L('Kontakt', 'Contact', 'Contact', 'Контакты'), L('Prüfen', 'Review', 'Vérifier', 'Проверка')],
    'heads': [
        (L('Welches Gerät soll repariert werden?', 'Which device needs repairing?', 'Quel appareil faut-il réparer ?', 'Какой аппарат нужно отремонтировать?'),
         L('Wählen Sie Hersteller, Typ und Modell. In einem Auftrag können Sie mehrere Geräte einsenden.', 'Choose manufacturer, type and model. You can send several devices in one order.',
           'Choisissez fabricant, type et modèle. Vous pouvez envoyer plusieurs appareils en une demande.', 'Выберите производителя, тип и модель. В одной заявке можно отправить несколько аппаратов.')),
        (L('Was stimmt mit dem Gerät nicht?', 'What is wrong with the device?', 'Quel est le problème ?', 'Что с аппаратом?'),
         L('Je genauer die Beschreibung, desto schneller die Diagnose. Bei sichtbaren Schäden hilft ein Foto.', 'The more precise the description, the faster the diagnosis. For visible damage, a photo helps.',
           'Plus la description est précise, plus le diagnostic est rapide. Pour un dommage visible, une photo aide.', 'Чем точнее описание, тем быстрее диагностика. При видимых повреждениях поможет фото.')),
        (L('Leihgerät während der Reparatur?', 'A loaner during the repair?', 'Un appareil de prêt pendant la réparation ?', 'Подменный аппарат на время ремонта?'),
         L('Kostenlos bei Verfügbarkeit, Sie tragen nur die Versandkosten.', 'Free of charge subject to availability; you only pay shipping.',
           'Gratuit selon disponibilité, seuls les frais d’envoi sont à votre charge.', 'Бесплатно при наличии, вы оплачиваете только доставку.')),
        (L('Wo sollen wir das Gerät abholen?', 'Where should we collect the device?', 'Où devons-nous enlever l’appareil ?', 'Где забрать аппарат?'),
         L('Den Termin bestätigen wir telefonisch oder per E-Mail.', 'We confirm the appointment by phone or e-mail.', 'Nous confirmons le rendez-vous par téléphone ou e-mail.', 'Время подтвердим по телефону или e-mail.')),
        (L('Wie erreichen wir Sie?', 'How can we reach you?', 'Comment vous joindre ?', 'Как с вами связаться?'),
         L('An diese Adresse senden wir den Kostenvoranschlag.', 'We send the cost estimate to this address.', 'Nous envoyons le devis à cette adresse.', 'На этот адрес мы отправим смету.')),
        (L('Auftrag prüfen', 'Review your order', 'Vérifier la demande', 'Проверьте заявку'),
         L('Alles korrekt? Dann senden Sie den Abholauftrag.', 'All correct? Then send the pick-up order.', 'Tout est correct ? Envoyez la demande.', 'Всё верно? Тогда отправьте заказ.')),
    ],
    'ai_t': L('Fotografieren Sie das Typenschild – wir füllen alles für Sie aus', 'Photograph the type plate – we fill in the rest', 'Photographiez la plaque signalétique – nous remplissons le reste', 'Сфотографируйте шильдик — остальное заполним мы'),
    'ai_s': L('Aufkleber am Geräteanschluss: Modell und Seriennummer', 'Label at the connector: model and serial number', 'Étiquette au connecteur : modèle et numéro de série', 'Наклейка у разъёма: модель и серийный номер'),
    'ai_btn': L('Fotografieren oder hochladen', 'Take or upload a photo', 'Prendre ou importer une photo', 'Сфотографировать или загрузить'),
    'ai_demo': L('Mit Beispiel testen', 'Try with an example', 'Essayer avec un exemple', 'Попробовать на примере'),
    'ai_scan': L('KI erkennt das Typenschild…', 'AI is reading the type plate…', 'L’IA lit la plaque…', 'ИИ распознаёт шильдик…'),
    'ai_ok': L('Fertig. Bitte prüfen Sie die Daten – Sie können sie ändern.', 'Done. Please check the details – you can edit them.', 'Terminé. Vérifiez les données – vous pouvez les modifier.', 'Готово. Проверьте данные — их можно изменить.'),
    'ai_found': L('Erkannt', 'Recognised', 'Reconnu', 'Распознано'),
    'ai_undo': L('Rückgängig', 'Undo', 'Annuler', 'Отменить'),
    'ai_badge': L('Von KI erkannt', 'Recognised by AI', 'Reconnu par l’IA', 'Распознано ИИ'),
    'ai_note': L('Demo: Im Prototyp wird die Erkennung simuliert.', 'Demo: recognition is simulated in the prototype.', 'Démo : la reconnaissance est simulée dans le prototype.', 'Демо: в прототипе распознавание имитируется.'),
    'add_device': L('Weiteres Gerät hinzufügen', 'Add another device', 'Ajouter un autre appareil', 'Добавить ещё аппарат'),
    'remove': L('Entfernen', 'Remove', 'Retirer', 'Удалить'),
    'defects_l': L('Was ist Ihnen aufgefallen?', 'What have you noticed?', 'Qu’avez-vous constaté ?', 'Что вы заметили?'),
    'multi': L('Mehrfachauswahl möglich', 'Multiple choice possible', 'Plusieurs choix possibles', 'Можно выбрать несколько'),
    'desc_l': L('Beschreibung', 'Description', 'Description', 'Описание'),
    'desc_ph': L('Was ist passiert? Seit wann? Bei welcher Untersuchung?', 'What happened? Since when? During which examination?', 'Que s’est-il passé ? Depuis quand ? Pendant quel examen ?', 'Что случилось? С какого момента? Во время какого исследования?'),
    'photo_tip': L('Tipp: distales Ende, Einführungsschlauch und Typenschild fotografieren.', 'Tip: photograph the distal end, insertion tube and type plate.', 'Astuce : photographiez l’extrémité distale, le tube d’insertion et la plaque.', 'Совет: снимите дистальный конец, вводную трубку и шильдик.'),
    'loaner_q': L('Brauchen Sie ein Leihgerät?', 'Do you need a loaner?', 'Avez-vous besoin d’un appareil de prêt ?', 'Нужен подменный аппарат?'),
    'loaner_yes': L('Ja, bitte Leihgerät anfragen', 'Yes, request a loaner', 'Oui, demander un prêt', 'Да, запросить подмену'),
    'loaner_yes_s': L('Untersuchungen laufen ohne Unterbrechung weiter', 'Examinations continue without interruption', 'Les examens continuent sans interruption', 'Исследования продолжаются без перерыва'),
    'loaner_no': L('Nein, nicht nötig', 'No, not needed', 'Non, pas nécessaire', 'Нет, не нужно'),
    'loaner_no_s': L('Wir haben Ersatz in der Praxis', 'We have a spare in the practice', 'Nous avons un appareil de remplacement', 'У нас есть замена'),
    'loaner_panel': L('Wir prüfen die Verfügbarkeit für Ihr Modell und melden uns. Leihgeräte sind auf Lagerbestandsgeräte begrenzt.',
                      'We check availability for your model and get back to you. Loaners are limited to devices in stock.',
                      'Nous vérifions la disponibilité pour votre modèle et revenons vers vous. Le prêt est limité aux appareils en stock.',
                      'Проверим наличие для вашей модели и свяжемся с вами. Подменные аппараты — только из складского наличия.'),
    'date_hint': L('Mo–Fr. Wir bestätigen den Termin.', 'Mon–Fri. We will confirm the appointment.', 'Lun–ven. Nous confirmons le rendez-vous.', 'Пн–Пт. Мы подтвердим время.'),
    'date_ph': L('Datum wählen', 'Choose a date', 'Choisir une date', 'Выберите дату'),
    'review_dev': L('Gerät', 'Device', 'Appareil', 'Аппарат'),
    'review_def': L('Defekt', 'Defect', 'Panne', 'Поломка'),
    'review_loan': L('Leihgerät', 'Loaner', 'Prêt', 'Подмена'),
    'review_pick': L('Abholung', 'Pick-up', 'Enlèvement', 'Забор'),
    'review_contact': L('Kontakt', 'Contact', 'Contact', 'Контакты'),
    'review_panel': L('Sie erhalten zuerst einen Kostenvoranschlag. Die Reparatur beginnt erst nach Ihrer Freigabe.', 'You receive a cost estimate first. The repair only starts after your approval.',
                      'Vous recevez d’abord un devis. La réparation ne commence qu’après votre accord.', 'Сначала вы получите смету. Ремонт начнётся только после вашего согласия.'),
    'submit': L('Abholauftrag senden', 'Send pick-up order', 'Envoyer la demande', 'Отправить заказ'),
    'side_t': L('Ihr Abholauftrag', 'Your pick-up order', 'Votre demande', 'Ваш заказ'),
    'side_list': [L('Kostenvoranschlag vor jeder Reparatur', 'Cost estimate before every repair', 'Devis avant chaque réparation', 'Смета перед каждым ремонтом'),
                  L('Reparatur erst nach Freigabe', 'Repair only after approval', 'Réparation après accord', 'Ремонт только после согласия'),
                  L('6 Monate Gewährleistung', '6-month warranty', 'Garantie 6 mois', 'Гарантия 6 месяцев')],
    'done_h': L('Abholauftrag gesendet', 'Pick-up order sent', 'Demande envoyée', 'Заказ отправлен'),
    'done_s': L('Vielen Dank. Wir melden uns kurzfristig, um die Abholung abzustimmen.', 'Thank you. We will be in touch shortly to arrange the pick-up.',
                'Merci. Nous vous contactons rapidement pour organiser l’enlèvement.', 'Спасибо. Мы скоро свяжемся с вами, чтобы согласовать забор.'),
    'done_next': L('Wie geht es weiter?', 'What happens next?', 'Et ensuite ?', 'Что дальше?'),
    'done_steps': [
        (L('Terminabstimmung', 'Scheduling', 'Prise de rendez-vous', 'Согласование времени'),
         L('Wir klären, ob ein Techniker kommt oder ein Kurier abholt.', 'We decide whether a technician comes or a courier collects.', 'Nous voyons si un technicien vient ou un coursier enlève.', 'Решим, приедет техник или курьер.')),
        (L('Analyse und Kostenvoranschlag', 'Analysis and cost estimate', 'Analyse et devis', 'Диагностика и смета'),
         L('Detailliert und unverbindlich.', 'Detailed and non-binding.', 'Détaillé et sans engagement.', 'Подробно и без обязательств.')),
        (L('Ihre Freigabe', 'Your approval', 'Votre accord', 'Ваше согласие'),
         L('Erst danach reparieren wir.', 'Only then do we repair.', 'Seulement ensuite nous réparons.', 'Только после этого начнём ремонт.')),
    ],
}

P['leihgeraete'] = {
    'title': L('Leihgeräte', 'Loaner devices', 'Appareils de prêt', 'Подменные аппараты'),
    'o': L('Leihgeräte-Service', 'Loaner service', 'Service de prêt', 'Подменный фонд'),
    'h1': L('Weiterarbeiten, während wir reparieren', 'Keep working while we repair', 'Continuez à travailler pendant la réparation', 'Работайте, пока мы ремонтируем'),
    'lead': L('Bei Bedarf stellen wir Ihnen schnell und unkompliziert ein Leihgerät zur Verfügung, damit Untersuchungen in Ihrer Praxis oder Klinik nicht ausfallen.',
              'If needed, we quickly provide a loaner so examinations in your practice or hospital don’t have to be cancelled.',
              'Si nécessaire, nous prêtons rapidement un appareil pour que les examens de votre cabinet ou clinique ne soient pas annulés.',
              'При необходимости быстро предоставим подменный аппарат, чтобы исследования в вашей практике или клинике не отменялись.'),
    'facts': [
        ('tag', L('Kostenlos', 'Free of charge', 'Gratuit', 'Бесплатно'), L('bei Verfügbarkeit, nur Versandkosten', 'subject to availability, shipping only', 'selon disponibilité, frais d’envoi seulement', 'при наличии, только доставка')),
        ('box', L('Ab Lager', 'From stock', 'En stock', 'Со склада'), L('begrenzt auf Lagerbestandsgeräte', 'limited to devices in stock', 'limité aux appareils en stock', 'только из складского наличия')),
        ('swap', L('Kompatibel', 'Compatible', 'Compatible', 'Совместимо'), L('Verfügbarkeit hängt vom Modell ab', 'availability depends on the model', 'la disponibilité dépend du modèle', 'наличие зависит от модели')),
    ],
    'how_h': L('So funktioniert der Leihgeräte-Service', 'How the loaner service works', 'Fonctionnement du service de prêt', 'Как работает подменный фонд'),
    'how': [
        (L('Anfrage', 'Request', 'Demande', 'Запрос'), L('Mit dem Abholauftrag oder separat über das Formular.', 'With the pick-up order or separately via the form.', 'Avec la demande d’enlèvement ou séparément via le formulaire.', 'Вместе с заказом забора или отдельно через форму.')),
        (L('Verfügbarkeit', 'Availability', 'Disponibilité', 'Наличие'), L('Wir prüfen, welches kompatible Gerät auf Lager ist, und melden uns.', 'We check which compatible device is in stock and get back to you.', 'Nous vérifions quel appareil compatible est en stock et vous recontactons.', 'Проверим, какой совместимый аппарат есть на складе, и свяжемся.')),
        (L('Lieferung', 'Delivery', 'Livraison', 'Доставка'), L('Das Leihgerät kommt zu Ihnen, Ihr Gerät geht in die Werkstatt.', 'The loaner comes to you, your device goes to the workshop.', 'L’appareil de prêt arrive chez vous, le vôtre part à l’atelier.', 'Подменный аппарат приезжает к вам, ваш — в мастерскую.')),
        (L('Rückholung', 'Collection', 'Retour', 'Возврат'), L('Nach Rücksprache – wenn Sie Ihr repariertes Gerät getestet haben.', 'By arrangement – once you have tested your repaired device.', 'Sur rendez-vous – après avoir testé votre appareil réparé.', 'По договорённости — после проверки отремонтированного аппарата.')),
    ],
    'cta_h': L('Leihgerät für Ihr Modell anfragen', 'Request a loaner for your model', 'Demander un prêt pour votre modèle', 'Запросите подменный аппарат для вашей модели'),
    'cta_s': L('Zwei Minuten, fünf kurze Schritte.', 'Two minutes, five short steps.', 'Deux minutes, cinq étapes courtes.', 'Две минуты, пять коротких шагов.'),
}

P['leihgeraet-anfragen'] = {
    'title': L('Leihgerät anfragen', 'Request a loaner', 'Demander un appareil de prêt', 'Запрос подменного аппарата'),
    'h1': L('Leihgerät anfragen', 'Request a loaner', 'Demander un appareil de prêt', 'Запрос подменного аппарата'),
    'lead': L('Wir prüfen die Verfügbarkeit eines kompatiblen Geräts und melden uns.', 'We check availability of a compatible device and get back to you.',
              'Nous vérifions la disponibilité d’un appareil compatible et vous recontactons.', 'Проверим наличие совместимого аппарата и свяжемся с вами.'),
    'steps': [L('Gerät', 'Device', 'Appareil', 'Аппарат'), L('Anlass', 'Reason', 'Motif', 'Причина'), L('Lieferung', 'Delivery', 'Livraison', 'Доставка'),
              L('Kontakt', 'Contact', 'Contact', 'Контакты'), L('Prüfen', 'Review', 'Vérifier', 'Проверка')],
    'heads': [
        (L('Welches Gerät brauchen Sie?', 'Which device do you need?', 'De quel appareil avez-vous besoin ?', 'Какой аппарат нужен?'),
         L('Das Leihgerät muss zu Ihrem Prozessor passen. Geben Sie ihn an, wenn Sie ihn kennen.', 'The loaner must match your processor. Tell us which one if you know it.',
           'L’appareil doit être compatible avec votre processeur. Indiquez-le si vous le connaissez.', 'Аппарат должен подходить к вашему процессору. Укажите его, если знаете.')),
        (L('Wofür brauchen Sie das Leihgerät?', 'Why do you need the loaner?', 'Pourquoi avez-vous besoin du prêt ?', 'Для чего нужен аппарат?'),
         L('So können wir Lieferung und Reparatur zusammen planen.', 'This lets us plan delivery and repair together.', 'Cela nous permet de planifier livraison et réparation ensemble.', 'Так мы спланируем доставку и ремонт вместе.')),
        (L('Wohin sollen wir liefern?', 'Where should we deliver?', 'Où livrer ?', 'Куда доставить?'),
         L('Den Liefertermin bestätigen wir.', 'We will confirm the delivery date.', 'Nous confirmons la date de livraison.', 'Дату доставки мы подтвердим.')),
        (L('Wie erreichen wir Sie?', 'How can we reach you?', 'Comment vous joindre ?', 'Как с вами связаться?'), L('', '', '', '')),
        (L('Anfrage prüfen', 'Review your request', 'Vérifier la demande', 'Проверьте запрос'), L('Alles korrekt? Dann senden Sie die Anfrage.', 'All correct? Then send the request.', 'Tout est correct ? Envoyez la demande.', 'Всё верно? Тогда отправьте запрос.')),
    ],
    'proc_l': L('Prozessor / Lichtquelle', 'Processor / light source', 'Processeur / source lumineuse', 'Процессор / источник света'),
    'proc_ph': L('z. B. EPK-i5000', 'e.g. EPK-i5000', 'p. ex. EPK-i5000', 'например, EPK-i5000'),
    'reasons': [
        ('mit', L('Zusammen mit einem Reparaturauftrag', 'Together with a repair order', 'Avec une demande de réparation', 'Вместе с заказом ремонта'), L('Ich beauftrage jetzt auch die Reparatur', 'I am ordering the repair now as well', 'Je commande aussi la réparation', 'Я также заказываю ремонт')),
        ('laufend', L('Mein Gerät ist bereits bei scopeREPAIR', 'My device is already at scopeREPAIR', 'Mon appareil est déjà chez scopeREPAIR', 'Мой аппарат уже в scopeREPAIR'), L('Reparatur läuft schon', 'Repair already in progress', 'Réparation en cours', 'Ремонт уже идёт')),
        ('sonst', L('Anderer Anlass', 'Other reason', 'Autre motif', 'Другая причина'), L('z. B. Ausfall eines weiteren Geräts', 'e.g. another device has failed', 'p. ex. panne d’un autre appareil', 'например, вышел из строя другой аппарат')),
    ],
    'from_l': L('Ab wann?', 'From when?', 'À partir de quand ?', 'С какого числа?'),
    'note_l': L('Hinweis', 'Note', 'Remarque', 'Комментарий'),
    'submit': L('Anfrage senden', 'Send request', 'Envoyer la demande', 'Отправить запрос'),
    'done_h': L('Anfrage gesendet', 'Request sent', 'Demande envoyée', 'Запрос отправлен'),
    'done_s': L('Vielen Dank. Wir prüfen die Verfügbarkeit und melden uns.', 'Thank you. We are checking availability and will get back to you.', 'Merci. Nous vérifions la disponibilité et revenons vers vous.', 'Спасибо. Проверяем наличие и свяжемся с вами.'),
    'review_reason': L('Anlass', 'Reason', 'Motif', 'Причина'),
    'review_del': L('Lieferung', 'Delivery', 'Livraison', 'Доставка'),
}

P['gebrauchte-endoskope'] = {
    'title': L('Gebrauchte Endoskope', 'Used endoscopes', 'Endoscopes d’occasion', 'Б/у эндоскопы'),
    'h1': L('Gebrauchte Endoskope – generalüberholt und geprüft', 'Used endoscopes – refurbished and tested', 'Endoscopes d’occasion – révisés et contrôlés', 'Б/у эндоскопы — восстановлены и проверены'),
    'lead': L('Jedes Gerät wurde in unserer Werkstatt geprüft und generalüberholt, Verschleißteile wurden erneuert. Mit 12 Monaten Gewährleistung.',
              'Every device has been tested and refurbished in our workshop, with wear parts replaced. With a 12-month warranty.',
              'Chaque appareil a été contrôlé et révisé dans notre atelier, pièces d’usure remplacées. Avec 12 mois de garantie.',
              'Каждый аппарат проверен и восстановлен в нашей мастерской, изнашиваемые детали заменены. Гарантия 12 месяцев.'),
    'search_ph': L('Modell suchen, z. B. GIF-H190', 'Search model, e.g. GIF-H190', 'Rechercher un modèle, p. ex. GIF-H190', 'Поиск модели, например GIF-H190'),
    'f_cond': L('Zustand', 'Condition', 'État', 'Состояние'),
    'all': L('Alle', 'All', 'Tous', 'Все'),
    'reset': L('Filter zurücksetzen', 'Reset filters', 'Réinitialiser', 'Сбросить фильтры'),
    'count': L('{n} Geräte', '{n} devices', '{n} appareils', 'Аппаратов: {n}'),
    'sort': L('Sortieren', 'Sort', 'Trier', 'Сортировка'),
    'sort_opts': [('photo', L('Mit Foto zuerst', 'With photo first', 'Avec photo d’abord', 'Сначала с фото')), ('model', L('Modell A–Z', 'Model A–Z', 'Modèle A–Z', 'Модель А–Я')), ('brand', L('Hersteller', 'Manufacturer', 'Fabricant', 'Производитель'))],
    'more': L('Weitere {n} anzeigen', 'Show {n} more', 'Afficher {n} de plus', 'Показать ещё {n}'),
    'empty': L('Für diese Filter ist aktuell nichts auf Lager.', 'Nothing in stock for these filters right now.', 'Rien en stock pour ces filtres actuellement.', 'По этим фильтрам сейчас ничего нет.'),
    'filters': L('Filter', 'Filters', 'Filtres', 'Фильтры'),
    'show_results': L('{n} Geräte anzeigen', 'Show {n} devices', 'Afficher {n} appareils', 'Показать: {n}'),
    'quality_h': L('Geprüfte Qualität für mehr Sicherheit', 'Tested quality for more security', 'Qualité contrôlée pour plus de sécurité', 'Проверенное качество — больше уверенности'),
    'quality': [
        L('Die Geräte waren im medizinischen Einsatz und wurden professionell gewartet.', 'The devices were in medical use and professionally maintained.', 'Les appareils ont été utilisés en milieu médical et entretenus professionnellement.', 'Аппараты использовались в медицине и профессионально обслуживались.'),
        L('Verschleißteile wurden nach dem Kauf durch scopeREPAIR vollständig erneuert.', 'Wear parts were fully replaced by scopeREPAIR after purchase.', 'Les pièces d’usure ont été entièrement remplacées par scopeREPAIR.', 'Изнашиваемые детали полностью заменены scopeREPAIR.'),
        L('Jedes Gerät wurde technisch geprüft und generalüberholt, bevor es angeboten wird.', 'Every device was technically tested and refurbished before being offered.', 'Chaque appareil a été contrôlé et révisé avant d’être proposé.', 'Каждый аппарат проверен и восстановлен перед продажей.'),
    ],
}

P['produkt'] = {
    'inquiry_t': L('Kaufanfrage', 'Purchase inquiry', 'Demande d’achat', 'Запрос на покупку'),
    'inquiry_s': L('Sie erhalten ein unverbindliches Angebot per E-Mail.', 'You will receive a non-binding offer by e-mail.', 'Vous recevrez une offre sans engagement par e-mail.', 'Вы получите предложение без обязательств по e-mail.'),
    'tradein_cb': L('Ich möchte mein Altgerät in Zahlung geben', 'I would like to trade in my old device', 'Je souhaite faire reprendre mon ancien appareil', 'Хочу сдать старый аппарат в зачёт'),
    'send': L('Kaufanfrage senden', 'Send purchase inquiry', 'Envoyer la demande', 'Отправить запрос'),
    'sent_t': L('Anfrage gesendet', 'Inquiry sent', 'Demande envoyée', 'Запрос отправлен'),
    'sent_s': L('Wir senden Ihnen das Angebot per E-Mail.', 'We will send you the offer by e-mail.', 'Nous vous envoyons l’offre par e-mail.', 'Мы пришлём предложение по e-mail.'),
    'repair_this': L('Dieses Modell reparieren lassen', 'Have this model repaired', 'Faire réparer ce modèle', 'Отремонтировать такую модель'),
    'specs': L('Technische Daten', 'Technical data', 'Caractéristiques techniques', 'Технические данные'),
    'device': L('Gerät', 'Device', 'Appareil', 'Аппарат'),
    'acc': L('Zubehör', 'Accessories', 'Accessoires', 'Принадлежности'),
    'acc_more': L('Weiteres Zubehör auf Anfrage.', 'More accessories on request.', 'Autres accessoires sur demande.', 'Другие принадлежности — по запросу.'),
    'desc': L('Beschreibung', 'Description', 'Description', 'Описание'),
    'related': L('Ähnliche Geräte', 'Similar devices', 'Appareils similaires', 'Похожие аппараты'),
    'photo_n': L('Foto {n} von {total}', 'Photo {n} of {total}', 'Photo {n} sur {total}', 'Фото {n} из {total}'),
    'prev': L('Vorheriges Foto', 'Previous photo', 'Photo précédente', 'Предыдущее фото'),
    'nextp': L('Nächstes Foto', 'Next photo', 'Photo suivante', 'Следующее фото'),
    'zoom': L('Foto vergrößern', 'Enlarge photo', 'Agrandir la photo', 'Увеличить фото'),
    'facts_note': L('Werte wie auf scopeREPAIR.de angegeben', 'Values as stated on scopeREPAIR.de', 'Valeurs telles qu’indiquées sur scopeREPAIR.de', 'Значения как на scopeREPAIR.de'),
}

P['ankauf'] = {
    'title': L('Ankauf von Endoskopen', 'Endoscope buy-back', 'Rachat d’endoscopes', 'Выкуп эндоскопов'),
    'o': L('Ankauf und Inzahlungnahme', 'Buy-back and trade-in', 'Rachat et reprise', 'Выкуп и приём в зачёт'),
    'h1': L('Sie wollen Ihr Endoskop verkaufen? Hier sind Sie richtig.', 'Want to sell your endoscope? You’re in the right place.',
            'Vous voulez vendre votre endoscope ? Vous êtes au bon endroit.', 'Хотите продать эндоскоп? Вы по адресу.'),
    'lead': L('Wir kaufen gebrauchte Endoskope – auch defekt, unvollständig oder demontiert – zu fairen Konditionen.',
              'We buy used endoscopes – even defective, incomplete or disassembled – on fair terms.',
              'Nous rachetons les endoscopes d’occasion – même défectueux, incomplets ou démontés – à des conditions équitables.',
              'Выкупаем б/у эндоскопы — даже неисправные, некомплектные или разобранные — на честных условиях.'),
    'points': [
        ('tool', L('Auch defekte Geräte', 'Defective devices too', 'Appareils défectueux aussi', 'И неисправные аппараты'),
         L('Wir bewerten jedes Gerät individuell und berücksichtigen Zustand, Reparatur- und Wartungskosten.', 'We assess each device individually, considering condition and repair or maintenance costs.',
           'Chaque appareil est évalué individuellement selon son état et les coûts de remise en état.', 'Каждый аппарат оцениваем индивидуально с учётом состояния и стоимости ремонта.')),
        ('truck', L('Mehrere Geräte? Wir kommen vorbei', 'Several devices? We come to you', 'Plusieurs appareils ? Nous venons', 'Несколько аппаратов? Приедем'),
         L('Bei mehreren Geräten prüft in der Regel einer unserer Techniker vor Ort.', 'For several devices, one of our technicians usually inspects them on site.',
           'Pour plusieurs appareils, un technicien les examine généralement sur place.', 'При нескольких аппаратах обычно приезжает наш техник для оценки на месте.')),
        ('swap', L('Inzahlungnahme', 'Trade-in', 'Reprise', 'Приём в зачёт'),
         L('Den Restwert verrechnen wir auf Wunsch mit einem generalüberholten Gerät.', 'On request we credit the residual value against a refurbished device.',
           'Sur demande, la valeur résiduelle est déduite d’un appareil révisé.', 'По желанию зачтём остаточную стоимость в покупку восстановленного аппарата.')),
    ],
    'how_h': L('So läuft der Ankauf', 'How the buy-back works', 'Déroulement du rachat', 'Как проходит выкуп'),
    'how': [
        (L('Angaben senden', 'Send details', 'Envoyer les infos', 'Отправьте данные'), L('Hersteller, Modell, Zustand, Zubehör – und gern Fotos.', 'Manufacturer, model, condition, accessories – and photos if possible.', 'Fabricant, modèle, état, accessoires – et des photos si possible.', 'Производитель, модель, состояние, комплектация — и по возможности фото.')),
        (L('Bewertung', 'Assessment', 'Évaluation', 'Оценка'), L('Wir prüfen die Angaben und erstellen eine individuelle Einschätzung.', 'We review the details and prepare an individual assessment.', 'Nous examinons les infos et préparons une estimation.', 'Изучим данные и подготовим индивидуальную оценку.')),
        (L('Angebot und Abwicklung', 'Offer and handling', 'Offre et suite', 'Предложение и сделка'), L('Nach einer Einigung organisieren wir die Abholung.', 'Once agreed, we arrange the pick-up.', 'Après accord, nous organisons l’enlèvement.', 'После согласования организуем забор.')),
    ],
    'cta_h': L('Gerät zur Bewertung anbieten', 'Offer a device for assessment', 'Proposer un appareil à l’évaluation', 'Предложить аппарат на оценку'),
    'cta_s': L('Je mehr Informationen wir erhalten, desto genauer die Einschätzung.', 'The more information we receive, the more accurate the assessment.', 'Plus nous avons d’informations, plus l’estimation est précise.', 'Чем больше информации, тем точнее оценка.'),
    'replace_h': L('Wollen Sie Ihr Gerät ersetzen?', 'Want to replace your device?', 'Vous voulez remplacer votre appareil ?', 'Хотите заменить аппарат?'),
    'replace_s': L('Stöbern Sie in unserem Angebot generalüberholter Endoskope.', 'Browse our range of refurbished endoscopes.', 'Parcourez notre offre d’endoscopes révisés.', 'Посмотрите наши восстановленные эндоскопы.'),
}

P['ankauf-anfrage'] = {
    'title': L('Gerät verkaufen', 'Sell a device', 'Vendre un appareil', 'Продать аппарат'),
    'h1': L('Gerät zum Ankauf anbieten', 'Offer a device for buy-back', 'Proposer un appareil au rachat', 'Предложить аппарат на выкуп'),
    'lead': L('Mehrere Geräte? Fügen Sie sie hinzu oder rufen Sie uns an – dann kommt ein Techniker zur Bewertung vor Ort.', 'Several devices? Add them or call us – a technician will come for an on-site assessment.',
              'Plusieurs appareils ? Ajoutez-les ou appelez-nous – un technicien viendra les évaluer sur place.', 'Несколько аппаратов? Добавьте их или позвоните — техник приедет для оценки.'),
    'steps': [L('Gerät', 'Device', 'Appareil', 'Аппарат'), L('Zustand', 'Condition', 'État', 'Состояние'), L('Preis und Fotos', 'Price and photos', 'Prix et photos', 'Цена и фото'),
              L('Kontakt', 'Contact', 'Contact', 'Контакты'), L('Prüfen', 'Review', 'Vérifier', 'Проверка')],
    'heads': [
        (L('Welches Gerät möchten Sie verkaufen?', 'Which device would you like to sell?', 'Quel appareil souhaitez-vous vendre ?', 'Какой аппарат вы хотите продать?'), L('', '', '', '')),
        (L('In welchem Zustand ist das Gerät?', 'What condition is the device in?', 'Dans quel état est l’appareil ?', 'В каком состоянии аппарат?'),
         L('Auch defekte oder unvollständige Geräte können einen Restwert haben.', 'Defective or incomplete devices can still have residual value.', 'Les appareils défectueux ou incomplets peuvent avoir une valeur résiduelle.', 'Даже неисправные или некомплектные аппараты имеют остаточную стоимость.')),
        (L('Preisvorstellung und Fotos', 'Price expectation and photos', 'Prix souhaité et photos', 'Желаемая цена и фото'), L('', '', '', '')),
        (L('Wie erreichen wir Sie?', 'How can we reach you?', 'Comment vous joindre ?', 'Как с вами связаться?'), L('', '', '', '')),
        (L('Angaben prüfen', 'Review your details', 'Vérifier les informations', 'Проверьте данные'), L('Alles korrekt? Dann senden Sie das Angebot.', 'All correct? Then send your offer.', 'Tout est correct ? Envoyez votre offre.', 'Всё верно? Отправьте предложение.')),
    ],
    'qty_l': L('Anzahl', 'Quantity', 'Quantité', 'Количество'),
    'year_l': L('Baujahr', 'Year of manufacture', 'Année de fabrication', 'Год выпуска'),
    'cond': [
        ('ok', L('Funktionsfähig', 'Working', 'Fonctionnel', 'Исправен'), L('im Einsatz oder eingelagert', 'in use or stored', 'en service ou stocké', 'в работе или на хранении')),
        ('def', L('Defekt', 'Defective', 'Défectueux', 'Неисправен'), L('bitte kurz beschreiben', 'please describe briefly', 'veuillez décrire brièvement', 'кратко опишите')),
        ('inc', L('Unvollständig / demontiert', 'Incomplete / disassembled', 'Incomplet / démonté', 'Некомплектен / разобран'), L('Teile fehlen', 'parts missing', 'pièces manquantes', 'не хватает деталей')),
    ],
    'defect_l': L('Defekt / Schaden', 'Defect / damage', 'Panne / dommage', 'Неисправность / повреждение'),
    'acc_l': L('Vorhandenes Zubehör', 'Accessories included', 'Accessoires présents', 'Имеющиеся принадлежности'),
    'price_l': L('Preisvorstellung', 'Price expectation', 'Prix souhaité', 'Желаемая цена'),
    'price_hint': L('in Euro, netto', 'in euros, net', 'en euros, HT', 'в евро, нетто'),
    'submit': L('Angebot senden', 'Send offer', 'Envoyer l’offre', 'Отправить предложение'),
    'done_h': L('Angebot gesendet', 'Offer sent', 'Offre envoyée', 'Предложение отправлено'),
    'done_s': L('Vielen Dank. Wir prüfen Ihre Angaben und melden uns mit einer Einschätzung.', 'Thank you. We will review your details and get back to you with an assessment.',
                'Merci. Nous examinons vos informations et revenons vers vous avec une estimation.', 'Спасибо. Мы изучим данные и вернёмся с оценкой.'),
    'review_cond': L('Zustand', 'Condition', 'État', 'Состояние'),
    'review_price': L('Preis und Fotos', 'Price and photos', 'Prix et photos', 'Цена и фото'),
}

P['endoskopie-anlagen'] = {
    'title': L('Endoskopie-Anlagen', 'Endoscopy systems', 'Systèmes d’endoscopie', 'Эндоскопические системы'),
    'o': L('Komplettlösungen', 'Complete solutions', 'Solutions complètes', 'Комплексные решения'),
    'h1': L('Endoskopie-Anlagen – herstellerunabhängig geplant', 'Endoscopy systems – planned independently of manufacturers',
            'Systèmes d’endoscopie – conçus indépendamment des fabricants', 'Эндоскопические системы — независимо от производителя'),
    'lead': L('Vom Einzelgerät bis zum kompletten Endoskopieturm: Wir finden mit Ihnen die passenden geprüften Gebrauchtgeräte und begleiten Sie bis zur Inbetriebnahme.',
              'From a single device to a complete endoscopy tower: we find the right tested used equipment with you and support you through to commissioning.',
              'De l’appareil seul à la colonne complète : nous trouvons avec vous les appareils d’occasion contrôlés et vous accompagnons jusqu’à la mise en service.',
              'От отдельного аппарата до полной стойки: подберём проверенное б/у оборудование и сопроводим до ввода в эксплуатацию.'),
    'parts_h': L('Was zu einer Anlage gehört', 'What makes up a system', 'Ce qui compose un système', 'Из чего состоит система'),
    'parts': [L('Endoskope', 'Endoscopes', 'Endoscopes', 'Эндоскопы'), L('Videoprozessor', 'Video processor', 'Processeur vidéo', 'Видеопроцессор'),
              L('Lichtquelle', 'Light source', 'Source lumineuse', 'Источник света'), L('Monitor', 'Monitor', 'Moniteur', 'Монитор'),
              L('Absaugpumpe', 'Suction pump', 'Pompe d’aspiration', 'Аспиратор'), L('Zubehör', 'Accessories', 'Accessoires', 'Принадлежности')],
    'steps_h': L('Planung und Einrichtung Ihrer Endoskopie-Einheit', 'Planning and setting up your endoscopy unit', 'Planification et installation de votre unité', 'Планирование и оснащение вашего отделения'),
    'steps': [
        (L('Beratung und Planung', 'Consulting and planning', 'Conseil et planification', 'Консультация и планирование'),
         L('Wir analysieren Ihren Anwendungsbereich: Typen und Anzahl der Endoskope, Prozessoren, Lichtquellen, Monitore, Absaugpumpen und Zubehör.', 'We analyse your area of application: types and number of endoscopes, processors, light sources, monitors, suction pumps and accessories.',
           'Nous analysons votre domaine : types et nombre d’endoscopes, processeurs, sources lumineuses, moniteurs, pompes et accessoires.', 'Анализируем ваши задачи: типы и количество эндоскопов, процессоры, источники света, мониторы, аспираторы и принадлежности.')),
        (L('Bestellung und Terminfindung', 'Order and scheduling', 'Commande et planning', 'Заказ и сроки'),
         L('Liefer- oder Montagetermin passend zu Ihrem Terminplan.', 'A delivery or installation date that fits your schedule.', 'Une date de livraison ou de montage adaptée à votre planning.', 'Дата поставки или монтажа под ваш график.')),
        (L('Lieferung und Installation', 'Delivery and installation', 'Livraison et installation', 'Поставка и монтаж'),
         L('Ein Techniker baut auf, verbindet die Komponenten und integriert sie in Ihre Systemlandschaft.', 'A technician sets up, connects the components and integrates them into your system landscape.', 'Un technicien installe, connecte les composants et les intègre à votre environnement.', 'Техник монтирует, подключает компоненты и интегрирует их в вашу инфраструктуру.')),
        (L('Einweisung und Schulung', 'Instruction and training', 'Formation', 'Инструктаж и обучение'),
         L('Ihr Team erhält eine Einweisung in die Technik und die hygienische Aufbereitung.', 'Your team is trained in the equipment and its hygienic reprocessing.', 'Votre équipe est formée à l’utilisation et au retraitement hygiénique.', 'Ваша команда проходит инструктаж по работе с техникой и её гигиенической обработке.')),
        (L('Reparatur, Prüfung und Wartung', 'Repair, testing and maintenance', 'Réparation, contrôle et maintenance', 'Ремонт, проверка и обслуживание'),
         L('Regelmäßige Inspektionen erkennen Probleme früh und verlängern die Lebensdauer.', 'Regular inspections detect problems early and extend service life.', 'Des inspections régulières détectent les problèmes tôt et prolongent la durée de vie.', 'Регулярные проверки выявляют проблемы заранее и продлевают срок службы.')),
    ],
    'stock_h': L('Prozessoren und Lichtquellen ab Lager', 'Processors and light sources in stock', 'Processeurs et sources lumineuses en stock', 'Процессоры и источники света на складе'),
    'warranty': L('6–12 Monate Gewährleistung auf gebrauchte Anlagen', '6–12-month warranty on used systems', 'Garantie 6–12 mois sur les systèmes d’occasion', 'Гарантия 6–12 месяцев на б/у системы'),
    'cta_h': L('Anlage planen lassen', 'Have your system planned', 'Faire planifier votre système', 'Спланировать систему'),
    'cta_s': L('Wir beraten Sie herstellerunabhängig und transparent.', 'We advise you independently and transparently.', 'Nous vous conseillons de façon indépendante et transparente.', 'Консультируем независимо и прозрачно.'),
    'cta_btn': L('Beratung anfragen', 'Request a consultation', 'Demander un conseil', 'Запросить консультацию'),
}

P['rechner'] = {
    'title': L('Kostenrechner', 'Cost calculator', 'Calculateur de coûts', 'Калькулятор затрат'),
    'o': L('Kostenrechner', 'Cost calculator', 'Calculateur de coûts', 'Калькулятор затрат'),
    'h1': L('Servicevertrag oder Reparatur nach Bedarf?', 'Service contract or repair on demand?', 'Contrat de service ou réparation à la demande ?', 'Сервисный договор или ремонт по необходимости?'),
    'lead': L('Tragen Sie Ihre eigenen Zahlen ein. Der Rechner vergleicht die jährlichen Kosten – ohne Annahmen von unserer Seite.',
              'Enter your own figures. The calculator compares the annual costs – without any assumptions on our side.',
              'Saisissez vos propres chiffres. Le calculateur compare les coûts annuels – sans hypothèse de notre part.',
              'Введите свои цифры. Калькулятор сравнит годовые затраты — без наших допущений.'),
    'in_h': L('Ihre Zahlen', 'Your figures', 'Vos chiffres', 'Ваши данные'),
    'fields': [
        ('devices', L('Anzahl Endoskope', 'Number of endoscopes', 'Nombre d’endoscopes', 'Количество эндоскопов'), L('Stück', 'units', 'unités', 'шт.'), L('', '', '', '')),
        ('contract', L('Servicevertrag pro Jahr', 'Service contract per year', 'Contrat de service par an', 'Сервисный договор в год'), '€', L('Gesamtkosten aller Verträge laut Rechnung', 'Total of all contracts as invoiced', 'Total de tous les contrats facturés', 'Сумма всех договоров по счетам')),
        ('repairs', L('Reparaturen pro Jahr', 'Repairs per year', 'Réparations par an', 'Ремонтов в год'), L('Anzahl', 'number', 'nombre', 'шт.'), L('Ihr Durchschnitt der letzten Jahre', 'Your average over recent years', 'Votre moyenne des dernières années', 'Ваше среднее за последние годы')),
        ('cost', L('Ø Kosten je Reparatur', 'Avg. cost per repair', 'Coût moyen par réparation', 'Средняя стоимость ремонта'), '€', L('z. B. aus früheren Kostenvoranschlägen', 'e.g. from previous estimates', 'p. ex. d’après des devis précédents', 'например, по прошлым сметам')),
    ],
    'out_h': L('Ergebnis pro Jahr', 'Result per year', 'Résultat par an', 'Результат за год'),
    'out_a': L('Servicevertrag', 'Service contract', 'Contrat de service', 'Сервисный договор'),
    'out_b': L('Reparatur nach Bedarf', 'Repair on demand', 'Réparation à la demande', 'Ремонт по необходимости'),
    'out_diff_pos': L('Differenz zugunsten Reparatur nach Bedarf', 'Difference in favour of repair on demand', 'Écart en faveur de la réparation à la demande', 'Разница в пользу ремонта по необходимости'),
    'out_diff_neg': L('Differenz zugunsten Servicevertrag', 'Difference in favour of the service contract', 'Écart en faveur du contrat de service', 'Разница в пользу сервисного договора'),
    'out_empty': L('Füllen Sie alle Felder aus, um das Ergebnis zu sehen.', 'Fill in all fields to see the result.', 'Remplissez tous les champs pour voir le résultat.', 'Заполните все поля, чтобы увидеть результат.'),
    'per_device': L('pro Endoskop', 'per endoscope', 'par endoscope', 'на эндоскоп'),
    'formula_h': L('So rechnet der Rechner', 'How the calculator works', 'Méthode de calcul', 'Как считает калькулятор'),
    'formula': [
        L('Servicevertrag = Ihre jährlichen Vertragskosten.', 'Service contract = your annual contract costs.', 'Contrat de service = vos coûts annuels de contrat.', 'Сервисный договор = ваши годовые расходы по договору.'),
        L('Reparatur nach Bedarf = Reparaturen pro Jahr × Ø Kosten je Reparatur.', 'Repair on demand = repairs per year × average cost per repair.', 'Réparation à la demande = réparations par an × coût moyen.', 'Ремонт по необходимости = ремонтов в год × средняя стоимость.'),
        L('Nicht berücksichtigt: Ausfallzeiten, Leihgeräte, Versand. Für eine belastbare Zahl fordern Sie einen Kostenvoranschlag an.', 'Not included: downtime, loaners, shipping. For a reliable figure, request a cost estimate.',
          'Non inclus : indisponibilité, prêt, envoi. Pour un chiffre fiable, demandez un devis.', 'Не учтены простой, подменные аппараты, доставка. Для точной цифры запросите смету.'),
    ],
    'cta': L('Kostenvoranschlag anfordern', 'Request a cost estimate', 'Demander un devis', 'Запросить смету'),
    'reset': L('Zurücksetzen', 'Reset', 'Réinitialiser', 'Сбросить'),
}

P['ueber-uns'] = {
    'title': L('Über uns', 'About us', 'À propos', 'О нас'),
    'o': L('Über uns', 'About us', 'À propos', 'О нас'),
    'h1': L('Spezialisten für Endoskope', 'Endoscope specialists', 'Spécialistes des endoscopes', 'Специалисты по эндоскопам'),
    'lead': L('Die scopeREPAIR GmbH ist ein unabhängiger Service- und Vertriebspartner für medizinische Endoskopie-Systeme.',
              'scopeREPAIR GmbH is an independent service and sales partner for medical endoscopy systems.',
              'scopeREPAIR GmbH est un partenaire indépendant de service et de vente de systèmes d’endoscopie médicale.',
              'scopeREPAIR GmbH — независимый сервисный и торговый партнёр в области медицинских эндоскопических систем.'),
    'story': [
        L('Wir sind spezialisiert auf Reparatur, Wartung, Aufbereitung und Vertrieb flexibler Endoskope sowie zugehöriger Geräte und Zubehörteile führender Hersteller wie Olympus, Pentax und Fujinon.',
          'We specialise in the repair, maintenance, reprocessing and sale of flexible endoscopes and related equipment and accessories from leading manufacturers such as Olympus, Pentax and Fujinon.',
          'Nous sommes spécialisés dans la réparation, la maintenance, le reconditionnement et la vente d’endoscopes souples et d’équipements associés des grands fabricants Olympus, Pentax et Fujinon.',
          'Мы специализируемся на ремонте, обслуживании, подготовке и продаже гибких эндоскопов, сопутствующего оборудования и принадлежностей ведущих производителей — Olympus, Pentax и Fujinon.'),
        L('Erfahrung in der Endoskopie-Reparatur besteht im Team seit 2010. Dieses Know-how ist heute in der scopeREPAIR GmbH gebündelt, die 2021 aus einem zuvor im gleichen Geschäftsfeld tätigen Unternehmen hervorgegangen ist.',
          'The team has been gaining experience in endoscopy repair since 2010. This know-how is now combined in scopeREPAIR GmbH, founded in 2021 from a company previously active in the same field.',
          'L’équipe a acquis son expérience en réparation d’endoscopes depuis 2010. Ce savoir-faire est aujourd’hui réuni au sein de scopeREPAIR GmbH, fondée en 2021 à partir d’une entreprise du même secteur.',
          'Опыт команды в ремонте эндоскопов — с 2010 года. Сегодня эти знания объединены в scopeREPAIR GmbH, основанной в 2021 году на базе компании из той же сферы.'),
    ],
    'mission_h': L('Unsere Mission', 'Our mission', 'Notre mission', 'Наша миссия'),
    'mission': L('Wir unterstützen Arztpraxen und Kliniken dabei, ihre Endoskopie-Systeme wirtschaftlich und zuverlässig im Einsatz zu halten: weniger Ausfallzeiten, längere Lebensdauer der Geräte.',
                 'We help practices and hospitals keep their endoscopy systems running economically and reliably: less downtime, longer device life.',
                 'Nous aidons cabinets et cliniques à exploiter leurs systèmes d’endoscopie de façon économique et fiable : moins d’indisponibilité, une durée de vie prolongée.',
                 'Помогаем практикам и клиникам экономично и надёжно эксплуатировать эндоскопические системы: меньше простоев, дольше срок службы.'),
    'services_h': L('Unsere Leistungen', 'Our services', 'Nos services', 'Наши услуги'),
    'services': [L('Reparatur flexibler Endoskope', 'Repair of flexible endoscopes', 'Réparation d’endoscopes souples', 'Ремонт гибких эндоскопов'),
                 L('Wartung und technische Überprüfung', 'Maintenance and technical inspection', 'Maintenance et contrôle technique', 'Обслуживание и техническая проверка'),
                 L('Aufbereitung und Funktionsprüfung', 'Reprocessing and function testing', 'Reconditionnement et test de fonctionnement', 'Подготовка и проверка работоспособности'),
                 L('Verkauf geprüfter, generalüberholter Endoskope und Zubehör', 'Sale of tested, refurbished endoscopes and accessories', 'Vente d’endoscopes révisés et contrôlés et d’accessoires', 'Продажа проверенных восстановленных эндоскопов и принадлежностей')],
    'qm_h': L('Zertifiziertes Qualitätsmanagement', 'Certified quality management', 'Management de la qualité certifié', 'Сертифицированная система качества'),
    'qm': L('Wir arbeiten nach DIN EN ISO 9001:2015 und sind entsprechend zertifiziert. Klare Prozesse, regelmäßige Überprüfungen und kontinuierliche Verbesserung sichern eine dauerhaft hohe Servicequalität.',
            'We work to DIN EN ISO 9001:2015 and are certified accordingly. Clear processes, regular reviews and continuous improvement ensure consistently high service quality.',
            'Nous travaillons selon la norme DIN EN ISO 9001:2015 et sommes certifiés. Des processus clairs, des contrôles réguliers et l’amélioration continue garantissent une qualité constante.',
            'Мы работаем по DIN EN ISO 9001:2015 и имеем соответствующий сертификат. Чёткие процессы, регулярные проверки и постоянное улучшение обеспечивают стабильно высокое качество.'),
    'intl_h': L('National und international', 'National and international', 'National et international', 'В Германии и за рубежом'),
    'intl': L('Medizinische Einrichtungen im In- und Ausland vertrauen auf unsere fachliche Kompetenz und partnerschaftlichen Service.',
              'Medical facilities at home and abroad rely on our expertise and partnership-based service.',
              'Des établissements médicaux en Allemagne et à l’étranger font confiance à notre expertise et à notre service.',
              'Медицинские учреждения в Германии и за рубежом доверяют нашей компетенции и партнёрскому сервису.'),
    'why_h': L('Darum scopeREPAIR', 'Why scopeREPAIR', 'Pourquoi scopeREPAIR', 'Почему scopeREPAIR'),
    'why': [
        L('Das Unternehmen ist jung, das Team hat langjährige Erfahrung – wir kennen uns mit Endoskopen bestens aus.', 'The company is young, the team has years of experience – we know endoscopes inside out.', 'L’entreprise est jeune, l’équipe expérimentée – nous connaissons parfaitement les endoscopes.', 'Компания молодая, команда опытная — мы отлично знаем эндоскопы.'),
        L('Wir arbeiten schnell und gründlich, damit Ihre Praxis oder Klinik so wenig wie möglich eingeschränkt ist.', 'We work quickly and thoroughly to keep disruption to your practice or hospital to a minimum.', 'Nous travaillons vite et bien pour limiter au maximum l’impact sur votre activité.', 'Работаем быстро и тщательно, чтобы ваша практика или клиника не простаивала.'),
        L('Unsere Gewährleistung auf gebrauchte und generalüberholte Geräte zeigt, wie sehr wir unserer Arbeit vertrauen.', 'Our warranty on used and refurbished devices shows how much we trust our work.', 'Notre garantie sur les appareils d’occasion et révisés montre notre confiance dans notre travail.', 'Гарантия на б/у и восстановленные аппараты показывает, как мы уверены в своей работе.'),
        L('Für uns zählt Ihre Zufriedenheit, nicht der Umsatz eines bestimmten Produkts oder Herstellers.', 'What counts is your satisfaction, not sales of a particular product or manufacturer.', 'Ce qui compte, c’est votre satisfaction, pas les ventes d’un produit ou d’une marque.', 'Для нас важна ваша удовлетворённость, а не продажи конкретного товара или марки.'),
    ],
}

P['kontakt'] = {
    'title': L('Kontakt', 'Contact', 'Contact', 'Контакты'),
    'o': L('Kontakt', 'Contact', 'Contact', 'Контакты'),
    'h1': L('Kontaktieren Sie uns, wir helfen Ihnen', 'Contact us, we’re here to help', 'Contactez-nous, nous vous aidons', 'Свяжитесь с нами — мы поможем'),
    'lead': L('Bei Fragen zu Reparaturen, sinnvollen Inspektionsintervallen oder passendem Zubehör beraten wir Sie gern – per Telefon, E-Mail oder über das Formular.',
              'For questions about repairs, sensible inspection intervals or the right accessories, we’re happy to advise – by phone, e-mail or via the form.',
              'Pour toute question sur les réparations, les intervalles d’inspection ou les accessoires, nous vous conseillons – par téléphone, e-mail ou via le formulaire.',
              'Вопросы о ремонте, интервалах проверок или подходящих принадлежностях? Проконсультируем по телефону, e-mail или через форму.'),
    'tab_msg': L('Nachricht', 'Message', 'Message', 'Сообщение'),
    'tab_cb': L('Rückruf', 'Call-back', 'Rappel', 'Обратный звонок'),
    'cb_when': L('Wann passt es Ihnen?', 'When suits you?', 'Quand vous convient-il ?', 'Когда удобно?'),
    'cb_topic': L('Worum geht es?', 'What is it about?', 'De quoi s’agit-il ?', 'О чём речь?'),
    'submit': L('Nachricht senden', 'Send message', 'Envoyer le message', 'Отправить сообщение'),
    'submit_cb': L('Rückruf anfordern', 'Request call-back', 'Demander un rappel', 'Заказать звонок'),
    'done_h': L('Nachricht gesendet', 'Message sent', 'Message envoyé', 'Сообщение отправлено'),
    'done_s': L('Vielen Dank. Wir bearbeiten Ihre Anfrage zeitnah.', 'Thank you. We will process your request promptly.', 'Merci. Nous traitons votre demande rapidement.', 'Спасибо. Мы скоро обработаем ваш запрос.'),
    'done_cb_h': L('Rückruf angefordert', 'Call-back requested', 'Rappel demandé', 'Звонок заказан'),
    'done_cb_s': L('Wir rufen Sie zum gewünschten Zeitpunkt zurück.', 'We will call you back at the requested time.', 'Nous vous rappelons au moment souhaité.', 'Мы перезвоним в выбранное время.'),
    'map_h': L('Standort', 'Location', 'Adresse', 'Местоположение'),
    'map_consent': L('Mit dem Laden der Karte werden Daten an Google übertragen.', 'Loading the map transfers data to Google.', 'Le chargement de la carte transmet des données à Google.', 'При загрузке карты данные передаются Google.'),
    'map_btn': L('Google Maps anzeigen', 'Show Google Maps', 'Afficher Google Maps', 'Показать Google Maps'),
}

LEGAL_TITLES = {k: v for k, v in LEGAL_LINKS}

# ──────────────────────────────────────────────────────────────────────────
# Loaders
# ──────────────────────────────────────────────────────────────────────────

def _load(name):
    with open(os.path.join(ROOT, 'data', name), encoding='utf-8') as f:
        return json.load(f)


FAQ_LIVE = _load('faq_live.json')
LEGAL = _load('legal.json')


def faq(key, lang):
    """Return [[q, a], …] for a page in the given language."""
    if key == 'loaner':
        if lang in ('de', 'en'):
            return [FAQ_LIVE[src][lang][i] for src, i in FAQ_PICK['loaner']]
        return FAQ_TR['loaner'][lang]
    return [_faq_item(key, i, n, lang) for n, i in enumerate(FAQ_PICK[key])]


def _faq_item(key, i, n, lang):
    if lang in ('de', 'en'):
        return FAQ_LIVE[key][lang][i]
    return FAQ_TR[key][lang][n]


def slugify(s):
    s = s.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def load_products():
    raw = _load('products_live.json')
    items = []
    for p in raw:
        kind = 'system' if p['kind'] == 'prozessor' else ('endoscope' if p['kind'] == 'endoskop' else 'other')
        specs = []
        for i, (name, vals) in enumerate(p['specs_de']):
            en_vals = p['specs_en'][i][1] if i < len(p['specs_en']) else vals
            vals = [v for v in vals if v and v != '•']
            en_vals = [v for v in en_vals if v and v != '•']
            if not vals:
                continue
            specs.append({'key': name, 'de': vals, 'en': en_vals or vals})
        def spec(key):
            for s in specs:
                if s['key'] == key:
                    return s['de']
            return []
        tube = spec('Einführschlauch')
        chan = spec('Arbeitskanal')
        items.append({
            'slug': p['slug'], 'kind': kind, 'brand': p['brand'], 'brand_slug': slugify(p['brand']),
            'type': p['type_de'], 'type_slug': slugify(p['type_de']), 'cond': p['cond_de'], 'cond_slug': slugify(p['cond_de']),
            'model': p['model'] or p['title_de'], 'title': {'de': p['title_de'], 'en': p['title_en'] or p['title_de']},
            'specs': specs, 'dia': tube[0] if tube else '', 'channel': chan[0] if chan else '',
            'gallery': p['gallery'], 'acc': {'de': p['acc_de'], 'en': p['acc_en'] or p['acc_de']},
            'desc': {'de': p['desc_de'], 'en': p['desc_en']}, 'url_live': p['url_de'],
            'sortkey': p['sortkey'],
        })
    items.sort(key=lambda x: (x['brand'], x['model']))
    return items


PRODUCTS = load_products()


# ── Richtpreise (Platzhalter für den Prototyp, von Alex gewünscht) ─────────
_BASE = {'Gastroskop': 6900, 'Koloskop': 7900, 'Bronchoskop': 5900, 'Duodenoskop': 11900, 'Zystoskop': 3900}
_TIER = {1: .45, 2: .65, 3: 1.0, 4: 1.55}
_SYSTEMS = [('CV-190', 18900), ('CV-180', 9900), ('CV-165', 4900), ('CV-160', 3900), ('CV-145', 2900),
            ('VP-7000', 19900), ('EP-6000', 12900), ('EPX-4450', 6900), ('EPX-4400', 4900), ('EPX-3500', 3900),
            ('i7010', 16900), ('i7000', 13900), ('i5000', 8900), ('EPK-i HD', 5900), ('EPK-1000', 3900), ('EPK-100', 2490),
            ('VIO 200', 6900)]


def _tier(brand, m):
    if brand == 'Olympus':
        return 4 if '190' in m else 3 if ('180' in m or '185' in m) else 2 if ('160' in m or '165' in m) else 1
    if brand == 'Fujinon':
        return 4 if re.search(r'-7\d\d', m) else 3 if re.search(r'-(5|6)9?0\d?', m) and ('590' in m or '600' in m) else 2
    if brand == 'Pentax':
        return 4 if re.search(r'[ijK]10', m) else 3 if '90' in m else 2 if ('80' in m or '70' in m) else 1
    return 2


def price_eur(p):
    if p['kind'] != 'endoscope':
        for k, v in _SYSTEMS:
            if k in p['model']:
                return v
        return None
    base = _BASE.get(p['type'])
    if not base:
        return None
    v = base * _TIER[_tier(p['brand'], p['model'])]
    return int(round(v / 500.0) * 500) - 10


def fmt_eur(v, lang):
    if lang == 'en':
        return '€{:,}'.format(v)
    return '{:,}'.format(v).replace(',', '\u202f') + '\u00a0€'
