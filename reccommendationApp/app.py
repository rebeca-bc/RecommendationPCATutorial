from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import random
import json
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.spatial.distance import cosine

app = Flask(__name__)

# Load MovieLens data
u_data_cols = ['user_id', 'item_id', 'rating', 'timestamp']
u_items_cols = ['item_id', 'movie_title', 'release_date', 'video_release_date', 'IMDb_URL', 
                'unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 
                'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 
                'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']

u_data_df = pd.read_csv('u.data', sep='\t', names=u_data_cols, encoding='latin-1')
u_items_df = pd.read_csv('u.item', sep='|', names=u_items_cols, encoding='latin-1')

# Create user-item matrix
user_item_matrix = u_data_df.pivot_table(index='user_id', columns='item_id', values='rating')

# Get all movies
all_movies = u_items_df[['item_id', 'movie_title', 'release_date', 'IMDb_URL']].copy()
all_movies['release_date'] = pd.to_datetime(all_movies['release_date'], errors='coerce')

# Extract IMDb ID from URL and construct poster URL
def get_poster_url(imdb_url):
    """Extract IMDb ID and construct poster URL"""
    if pd.isna(imdb_url):
        return None
    try:
        # Extract IMDb ID from URL (e.g., "http://www.imdb.com/cgi-bin/find?tt0133093" -> "tt0133093")
        imdb_id = str(imdb_url).split('/')[-1] if '/' in str(imdb_url) else None
        if imdb_id:
            # Use IMDb URL to get poster - format: https://www.imdb.com/title/tt0133093/
            return f"https://www.imdb.com/title/{imdb_id}/"
    except:
        pass
    return None

all_movies['imdb_id'] = all_movies['IMDb_URL'].apply(lambda x: str(x).split('/')[-1] if pd.notna(x) and '/' in str(x) else None)
all_movies['poster_url'] = all_movies['imdb_id'].apply(lambda x: f"https://www.imdb.com/title/{x}/" if x else None)

# User sessions (in-memory, no DB)
user_sessions = {}

# Track total attempts (rated + skipped) separately from actual ratings
user_attempt_counts = {}

def generate_session_id():
    return f"user_{random.randint(100000, 999999)}"

def get_random_unwatched_movie(rated_ids):
    """Get a random movie not yet rated by user, with diversity across decades"""
    available = all_movies[~all_movies['item_id'].isin(rated_ids)].copy()
    if len(available) == 0:
        return None
    
    # Extract decade from release_date
    available['decade'] = (available['release_date'].dt.year // 10 * 10).astype('Int64')
    
    # True stratified sampling: sample uniformly from decades first, then from movies in that decade
    # This ensures we get movies from different eras rather than just the most common ones
    decades_available = available['decade'].unique()
    if len(decades_available) > 0:
        # Keep trying to pick from a random decade until we find one with available movies
        for _ in range(10):  # Safety limit to prevent infinite loop
            selected_decade = np.random.choice(decades_available)
            available_in_decade = available[available['decade'] == selected_decade]
            if len(available_in_decade) > 0:
                movie_row = available_in_decade.sample(1).iloc[0]
                imdb_id = movie_row['imdb_id']
                # Generate poster placeholder - use IMDb if available
                poster_url = f"https://www.imdb.com/title/{imdb_id}/" if pd.notna(imdb_id) else None
                return {
                    'item_id': int(movie_row['item_id']),
                    'movie_title': str(movie_row['movie_title']),
                    'release_date': str(movie_row['release_date']),
                    'decade': int(movie_row['decade']),
                    'poster_url': poster_url
                }
    
    movie_row = available.sample(1).iloc[0]
    imdb_id = movie_row['imdb_id']
    poster_url = f"https://www.imdb.com/title/{imdb_id}/" if pd.notna(imdb_id) else None
    return {
        'item_id': int(movie_row['item_id']),
        'movie_title': str(movie_row['movie_title']),
        'release_date': str(movie_row['release_date']),
        'decade': int(movie_row['decade']),
        'poster_url': poster_url
    }

def compute_recommendations(user_ratings):
    """
    Compute recommendations using collaborative filtering:
    1. Find users with similar ratings to the current user
    2. Get movies they like that current user hasn't rated
    3. Return top 5 highest-rated unrated movies
    """
    from scipy.spatial.distance import cosine
    
    # Step 1: Clean up user ratings
    user_profile = {}
    for item_id, rating in user_ratings.items():
        try:
            item_id_int = int(item_id) if item_id is not None else None
            if item_id_int is not None and rating is not None:
                user_profile[item_id_int] = float(rating)
        except (ValueError, TypeError):
            continue
    
    if not user_profile:
        return []
    
    rated_item_ids = set(user_profile.keys())
    
    # Step 2: Create current user vector for comparison
    user_vector = np.zeros(len(user_item_matrix.columns))
    for item_id, rating in user_profile.items():
        if item_id in user_item_matrix.columns:
            col_idx = list(user_item_matrix.columns).index(item_id)
            user_vector[col_idx] = rating
    
    # Step 3: Find similar users (users who rated same movies similarly)
    similar_users = []
    for uid, row in user_item_matrix.iterrows():
        other_vector = row.values
        # Only compare on movies both users rated
        common_mask = ~(np.isnan(user_vector) | np.isnan(other_vector))
        
        if np.sum(common_mask) >= 2:  # Need at least 2 common ratings
            user_vec_common = user_vector[common_mask]
            other_vec_common = other_vector[common_mask]
            
            # Skip if either vector is all zeros
            if np.sum(user_vec_common) > 0 and np.sum(other_vec_common) > 0:
                try:
                    similarity = 1 - cosine(user_vec_common, other_vec_common)
                    if similarity > 0:
                        similar_users.append((uid, similarity))
                except:
                    pass
    
    # Sort by similarity
    similar_users.sort(key=lambda x: x[1], reverse=True)
    
    # Step 4: Get recommendations from similar users
    recommendations = {}
    for uid, similarity in similar_users[:10]:  # Consider top 10 similar users
        similar_user_row = user_item_matrix.loc[uid]
        
        for item_id in similar_user_row.index:
            if item_id not in rated_item_ids:
                rating = similar_user_row[item_id]
                if pd.notna(rating) and rating > 0:
                    if item_id not in recommendations:
                        recommendations[item_id] = []
                    recommendations[item_id].append((rating, similarity))
    
    # Step 5: Score and rank recommendations
    scored_recs = {}
    for item_id, ratings_similarities in recommendations.items():
        # Weighted average: weight ratings by user similarity
        weighted_sum = sum(r * s for r, s in ratings_similarities)
        weight_sum = sum(s for _, s in ratings_similarities)
        if weight_sum > 0:
            scored_recs[item_id] = weighted_sum / weight_sum
    
    # Step 6: If not enough recommendations, add popular movies
    if len(scored_recs) < 5:
        popular_ratings = user_item_matrix.mean(axis=0).dropna()
        for item_id in popular_ratings.nlargest(100).index:
            if item_id not in rated_item_ids and item_id not in scored_recs:
                scored_recs[item_id] = float(popular_ratings[item_id])
    
    # Step 7: Return top 5 recommendations
    top_recs = sorted(scored_recs.items(), key=lambda x: x[1], reverse=True)[:5]
    
    recommendations = []
    for item_id, score in top_recs:
        try:
            movie_info = all_movies[all_movies['item_id'] == item_id]
            if len(movie_info) > 0:
                movie_info = movie_info.iloc[0]
                recommendations.append({
                    'item_id': int(item_id),
                    'movie_title': str(movie_info['movie_title']),
                    'score': float(score)
                })
        except:
            continue
    
    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/init_session', methods=['POST'])
def init_session():
    """Initialize a new user session"""
    session_id = generate_session_id()
    user_sessions[session_id] = {
        'rated_movies': {},  # {item_id: rating}
        'rated_ids': set()
    }
    user_attempt_counts[session_id] = 0  # Count both ratings and skips
    return jsonify({'session_id': session_id, 'success': True})

@app.route('/api/next_movie', methods=['POST'])
def next_movie():
    """Get next movie to rate"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in user_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    rated_ids = user_sessions[session_id]['rated_ids']
    
    # Check if user already rated 10 movies
    if len(rated_ids) >= 10:
        return jsonify({'error': 'Already rated 10 movies'}), 400
    
    movie = get_random_unwatched_movie(rated_ids)
    
    if movie is None:
        return jsonify({'error': 'No more movies available'}), 400
    
    return jsonify({
        'movie': movie,
        'progress': len(rated_ids),
        'total': 10
    })

@app.route('/api/rate_movie', methods=['POST'])
def rate_movie():
    """Save user's rating for a movie"""
    data = request.json
    session_id = data.get('session_id')
    item_id = data.get('item_id')
    rating = data.get('rating')  # 1-5 or None for "haven't seen"
    
    if session_id not in user_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    # Increment attempt count (both ratings and skips count)
    user_attempt_counts[session_id] += 1
    
    if rating is not None:
        # Only store actual ratings, not skips
        user_sessions[session_id]['rated_movies'][str(item_id)] = rating
        user_sessions[session_id]['rated_ids'].add(item_id)
    
    # Check if we've reached 10 total attempts (ratings + skips)
    total_attempts = user_attempt_counts[session_id]
    actual_ratings = len(user_sessions[session_id]['rated_ids'])
    
    return jsonify({
        'success': True,
        'progress': total_attempts,  # Show total attempts to user
        'actual_ratings': actual_ratings,  # For debugging
        'total': 10,
        'is_complete': total_attempts >= 10
    })

@app.route('/api/get_recommendations', methods=['POST'])
def get_recommendations():
    """Generate recommendations based on user's ratings"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in user_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    user_ratings = user_sessions[session_id]['rated_movies']
    
    # Need at least some ratings (can have skipped some)
    if len(user_ratings) < 1:
        return jsonify({'error': 'Need to rate at least 1 movie'}), 400
    
    try:
        recommendations = compute_recommendations(user_ratings)
        
        if not recommendations:
            # Return fallback if no recommendations
            raise Exception("No recommendations generated")
        
        return jsonify({
            'recommendations': recommendations,
            'user_ratings': user_ratings
        })
    except Exception as e:
        # Return fallback recommendations on error
        print(f"Error computing recommendations: {e}")
        
        # Fallback: Get most popular movies
        try:
            movie_ratings = user_item_matrix.mean(axis=0).sort_values(ascending=False)
            rated_ids = set()
            for item_id in user_ratings.keys():
                try:
                    rated_ids.add(int(item_id) if item_id is not None else None)
                except (ValueError, TypeError):
                    pass
            
            fallback_recs = []
            for item_id in movie_ratings.index:
                if item_id not in rated_ids and len(fallback_recs) < 5:
                    movie_title = u_items_df[u_items_df['item_id'] == item_id]['movie_title'].values
                    if len(movie_title) > 0:
                        fallback_recs.append({
                            'item_id': int(item_id),
                            'movie_title': str(movie_title[0]),
                            'score': float(movie_ratings[item_id])
                        })
            
            return jsonify({
                'recommendations': fallback_recs,
                'user_ratings': user_ratings,
                'note': 'Using popular movies as recommendations'
            })
        except:
            return jsonify({'error': 'Failed to generate recommendations. Please try again.'}), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset user session"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id in user_sessions:
        del user_sessions[session_id]
    
    return jsonify({'success': True})

@app.route('/api/search_movies', methods=['POST'])
def search_movies():
    """Search for movies by title"""
    data = request.json
    query = data.get('query', '').lower().strip()
    
    if not query or len(query) < 2:
        return jsonify({'results': []})
    
    # Search in movie titles (case-insensitive)
    results = all_movies[
        all_movies['movie_title'].str.lower().str.contains(query, na=False)
    ].head(10)  # Limit to 10 results
    
    movies = []
    for _, row in results.iterrows():
        movies.append({
            'item_id': int(row['item_id']),
            'movie_title': str(row['movie_title']),
            'release_date': str(row['release_date'])
        })
    
    return jsonify({'results': movies})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
