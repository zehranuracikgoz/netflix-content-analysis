from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

df = pd.read_csv("data/netflix_titles.csv")

df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

fill_columns = ['country', 'rating', 'duration', 'director', 'cast', 'listed_in']
for col in fill_columns:
    df[col] = df[col].fillna('unknown')

df['year_added'] = df['date_added'].dt.year

all_countries = df['country'].str.split(',').explode().str.strip()
all_genres = df['listed_in'].str.split(',').explode().str.strip()


@app.route("/api/top-countries")
def top_countries():
    top_10 = all_countries.value_counts().head(10).to_dict()
    return jsonify(top_10)

@app.route("/api/top-genres")
def top_genres():
    top_10 = all_genres.value_counts().head(10).to_dict()
    return jsonify(top_10)

@app.route("/api/top_actors")
def top_actors():
    all_actors = df['cast'].str.split(',').explode().str.strip()
    top_10 = all_actors.value_counts().head(10).to_dict()
    return jsonify(top_10)


@app.route("/api/top_directors")
def top_directors():
    all_directors = df['director'].str.split(',').explode().str.strip()
    top_10 = all_directors.value_counts().head(10).to_dict()
    return jsonify(top_10)


@app.route("/api/recently-added")
def recently_added():
    try:
        recent = df.sort_values(by='release_year', ascending=False).head(5)
        
        results = []
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
            
            
            results.append(item)
            
        return jsonify({"count": len(results), "results": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500






@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)