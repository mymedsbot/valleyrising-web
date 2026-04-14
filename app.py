from flask import Flask, render_template, send_from_directory, jsonify
import os
import requests
import time

app = Flask(__name__)

# ── Google Places config ──────────────────────────────────────────────────────
GOOGLE_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', '')
PLACES = {
    'East Maitland': 'ChIJVzN8YLtGc2sR9xi91dt3ODs',
    'Lorn':          'ChIJ72daE5Rpc2sRt39-Zv10Uns',
}
PLACES_API_BASE = 'https://places.googleapis.com/v1/places'
REFERER = 'https://valleyrising-web-production.up.railway.app'

# Simple in-memory cache: { place_id: { 'data': {...}, 'ts': float } }
_review_cache = {}
CACHE_TTL = 86400  # 24 hours


def _fetch_place(place_id):
    """Fetch rating + reviews for a single place from the Places API (New)."""
    url = f'{PLACES_API_BASE}/{place_id}'
    resp = requests.get(url, headers={
        'X-Goog-Api-Key': GOOGLE_API_KEY,
        'X-Goog-FieldMask': 'displayName,rating,userRatingCount,reviews',
        'Referer': REFERER,
    }, timeout=8)
    resp.raise_for_status()
    return resp.json()


def get_reviews():
    """Return reviews for all locations, using cache where fresh."""
    result = {}
    for location_name, place_id in PLACES.items():
        cached = _review_cache.get(place_id)
        if cached and (time.time() - cached['ts']) < CACHE_TTL:
            result[location_name] = cached['data']
            continue
        try:
            data = _fetch_place(place_id)
            reviews = []
            for r in data.get('reviews', []):
                text = r.get('text', {}).get('text', '')
                if not text:
                    continue
                reviews.append({
                    'author':   r['authorAttribution']['displayName'],
                    'rating':   r.get('rating', 5),
                    'text':     text,
                    'relative': r.get('relativePublishTimeDescription', ''),
                    'photo':    r['authorAttribution'].get('photoUri', ''),
                })
            place_data = {
                'rating':       data.get('rating', 0),
                'review_count': data.get('userRatingCount', 0),
                'reviews':      reviews,
            }
            _review_cache[place_id] = {'data': place_data, 'ts': time.time()}
            result[location_name] = place_data
        except Exception as e:
            app.logger.error(f'Failed to fetch reviews for {location_name}: {e}')
            result[location_name] = {'rating': 0, 'review_count': 0, 'reviews': []}
    return result


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    places = get_reviews()
    # Pick up to 3 reviews for the homepage snippet (mix both locations)
    featured = []
    for loc, data in places.items():
        for r in data['reviews']:
            featured.append({**r, 'location': loc})
    featured = featured[:3]
    return render_template('index.html', featured_reviews=featured, places=places)


@app.route('/reviews')
def reviews():
    places = get_reviews()
    return render_template('reviews.html', places=places)


@app.route('/book')
def book():
    return render_template('book.html')


@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/conditions')
def conditions():
    return render_template('conditions.html')


@app.route('/new-patient')
def new_patient():
    return render_template('new-patient.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/videos')
def videos():
    return render_template('videos.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
