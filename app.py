#!/usr/bin/env python3
"""
prosty interfejs flask do zarzadzania scrapingiem
modul 2 - interface
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import json
from datetime import datetime
import os

# dodaj import config
from config import Config

# (opcjonalnie) automatycznie zaladuj .env jesli nie w dockerze
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# konfiguracja aplikacji
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# url-e do innych modulow (beda w kontenerach)
ENGINE_API_URL = app.config['ENGINE_API_URL']
DATABASE_API_URL = app.config['DATABASE_API_URL']

@app.route('/')
def index():
    """strona glowna"""
    return render_template('index.html')

@app.route('/scrape', methods=['GET', 'POST'])
def scrape():
    """strona scrapingu"""
    if request.method == 'POST':
        urls_text = request.form.get('urls', '').strip()
        
        if not urls_text:
            flash('Proszę podać URL-e do przetworzenia', 'error')
            return render_template('scrape.html')
        
        # Parsowanie URL-i
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            flash('Nie znaleziono prawidłowych URL-i', 'error')
            return render_template('scrape.html')
        
        try:
            # Wysłanie żądania do silnika scrapingu
            response = requests.post(
                f"{ENGINE_API_URL}/scrape",
                json={"urls": urls},
                timeout=300  # 5 minut timeout
            )
            
            if response.status_code == 200:
                results = response.json()
                
                # Zapisanie wyników do bazy danych
                db_response = requests.post(
                    f"{DATABASE_API_URL}/save",
                    json={"results": results}
                )
                
                if db_response.status_code == 200:
                    flash(f'Pomyślnie przetworzono {len(results)} stron', 'success')
                    return redirect(url_for('results'))
                else:
                    flash('Błąd zapisu do bazy danych', 'error')
            else:
                flash(f'Błąd silnika scrapingu: {response.status_code}', 'error')
                
        except requests.exceptions.Timeout:
            flash('Timeout - operacja trwała zbyt długo', 'error')
        except requests.exceptions.ConnectionError:
            flash('Błąd połączenia z silnikiem scrapingu', 'error')
        except Exception as e:
            flash(f'Nieoczekiwany błąd: {str(e)}', 'error')
    
    return render_template('scrape.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    """strona wynikow"""
    if request.method == 'POST':
        url_to_delete = request.form.get('delete_url')
        if url_to_delete:
            try:
                response = requests.post(
                    f"{DATABASE_API_URL}/delete",
                    json={"url": url_to_delete}
                )
                if response.status_code == 200:
                    flash('Wynik został usunięty', 'success')
                else:
                    flash('Błąd usuwania wyniku', 'error')
            except Exception:
                flash('Błąd połączenia z bazą danych', 'error')
        return redirect(url_for('results'))

    try:
        # Pobranie wyników z bazy danych
        response = requests.get(f"{DATABASE_API_URL}/results")
        if response.status_code == 200:
            results = response.json()
            # Statystyki
            stats = {
                'total_pages': len(results),
                'total_emails': sum(len(r.get('emails', [])) for r in results),
                'total_phones': sum(len(r.get('phones', [])) for r in results),
                'total_addresses': sum(len(r.get('addresses', [])) for r in results)
            }
            return render_template('results.html', results=results, stats=stats)
        else:
            flash('Błąd pobierania wyników z bazy danych', 'error')
            return render_template('results.html', results=[], stats={})
    except requests.exceptions.ConnectionError:
        flash('Błąd połączenia z bazą danych', 'error')
        return render_template('results.html', results=[], stats={})

@app.route('/api/status')
def api_status():
    """status api - sprawdzenie polaczen z modulami"""
    status = {
        'interface': 'OK',
        'engine': 'UNKNOWN',
        'database': 'UNKNOWN',
        'timestamp': datetime.now().isoformat()
    }
    
    # Sprawdzenie silnika
    try:
        response = requests.get(f"{ENGINE_API_URL}/health", timeout=5)
        status['engine'] = 'OK' if response.status_code == 200 else 'ERROR'
    except:
        status['engine'] = 'ERROR'
    
    # Sprawdzenie bazy danych
    try:
        response = requests.get(f"{DATABASE_API_URL}/health", timeout=5)
        status['database'] = 'OK' if response.status_code == 200 else 'ERROR'
    except:
        status['database'] = 'ERROR'
    
    return jsonify(status)

@app.route('/clear')
def clear_results():
    """czyszczenie wynikow"""
    try:
        response = requests.delete(f"{DATABASE_API_URL}/clear")
        if response.status_code == 200:
            flash('Wyniki zostały wyczyszczone', 'success')
        else:
            flash('Błąd czyszczenia wyników', 'error')
    except:
        flash('Błąd połączenia z bazą danych', 'error')
    
    return redirect(url_for('results'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)