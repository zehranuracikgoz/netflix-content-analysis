from flask import Flask, jsonify, render_template
import pandas as pd
import re

app = Flask(__name__)

df = pd.read_csv("data/netflix_titles.csv")

df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

fill_columns = ['country', 'rating', 'duration', 'director', 'cast', 'listed_in']
for col in fill_columns:
    df[col] = df[col].fillna('unknown')


df['year_added'] = df['date_added'].dt.year

all_countries = df['country'].str.split(',').explode().str.strip()
all_genres = df['listed_in'].str.split(',').explode().str.strip()
df['listed_in'] = df['listed_in'].str.replace(r'(,\s*)?Movies(,\s*)?', '', regex=True)
all_directors = df['director'].str.split(',').explode().str.strip()


@app.route("/api/top-countries")
def top_countries():
    all_countries = (
      df['country']
      .loc[df['country'] != 'unknown']
    )
    top_10 = all_countries.value_counts().head(10)
    result = [{"country": name, "count": int(count)} for name, count in top_10.items()]
    return jsonify(result)

@app.route("/api/top-genres")
def top_genres():
    all_genres =(
      df['listed_in']
      .loc[df['listed_in'] != 'unknown']
    )
    top_10 = all_genres.value_counts().head(10)
    result = [{"genre": name, "count": int(count)} for name, count in top_10.items()]
    return jsonify(result)

@app.route("/api/top_actors")
def top_actors():
    all_actors = (
      df['cast']
      .loc[df['cast'] != 'unknown']
      .str.split(',')
      .explode()
      .str.strip()
    )
    top_10 = all_actors.value_counts().head(10)
    result = [{"actor": name, "count": int(count)} for name, count in top_10.items()]
    return jsonify(result)

@app.route("/api/top_directors")
def top_directors():
    all_directors = (
        df['director']
        .loc[df['director'] != 'unknown']
        .str.split(',')
        .explode()
        .str.strip()
    )
    top_10 = all_directors.value_counts().head(10)
    result = [{"director": name, "count": int(count)} for name, count in top_10.items()]
    return jsonify(result)


@app.route("/api/recently-added")
def recently_added():
    try:
        recent = df.sort_values(by='release_year', ascending=False).head(10)
        
        results = []
        for _, row in recent.iterrows():
            item = {
                "type": row['type'],
                "title": row['title'],
                "release_year": int(row['release_year']),
                "date_added": row['date_added'].strftime('%Y-%m-%d'),
                "duration": row['duration'],
                "rating": row['rating'],
                "countries": [c.strip() for c in row['country'].split(',')],
                "genres": [g.strip() for g in row['listed_in'].split(',')]
            }
            
            if 'imdb_id' in df.columns and pd.notna(row['imdb_id']):
                item["imdb_link"] = f"https://www.imdb.com/title/{row['imdb_id']}"
            
            results.append(item)
            
        return jsonify({"count": len(results), "results": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/directors-with-movies")
def directors_with_movies():
    all_directors = (
        df['director']
        .loc[df['director'] != 'unknown']
        .str.split(',')
        .explode()
        .str.strip()
    )
    top_30 = all_directors.value_counts().head(30).index.tolist()

    results = []
    for director in top_30:
        # O yönetmenin filmlerini filtrele
        director_movies = df[df['director'].str.contains(director, na=False)]

        # Son 3 filmi al (release_year göre azalan)
        recent_movies = director_movies.sort_values(by='release_year', ascending=False).head(3)

        movies_info = []
        for _, movie in recent_movies.iterrows():
            movies_info.append({
                "title": movie['title'],
                "release_year": int(movie['release_year']),
                "type": movie['type']
            })

        results.append({
            "director": director,
            "movie_count": len(director_movies),
            "recent_movies": movies_info
        })

    return jsonify(results)


@app.route('/directors')
def directors_page():
    return render_template('pages/directors.html')

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)