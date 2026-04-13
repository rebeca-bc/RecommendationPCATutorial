# 🎬 MovieMate - Personalized Movie Recommender

A beautiful, interactive web app that rates your movie taste and generates personalized recommendations using **collaborative filtering** on the MovieLens dataset. This is a tutorial but also a working app.

---

## **Features**

✅ **Interactive Rating Phase**

- Browse through random movies from the MovieLens dataset (1,682 movies)
- Rate each movie 1-5 stars
- Skip movies you haven't seen
- Visual progress tracker
- Beautiful gradient UI with smooth animations

✅ **Smart Recommendations**

- Generates 5 personalized movie recommendations after rating 10 movies
- Uses **user-user collaborative filtering** to find similar users
- Considers patterns in ratings to predict what you'll like
- Falls back to popular recommendations if insufficient data
- Shows predicted rating for each recommendation

✅ **No Database Required**

- All data stored in-memory (session-based)
- Can reset and start over anytime
- Fresh session for each user

---

## **How It Works**

1. **[RECOMMENDATION_MODEL_EXPLAINED.md](./RECOMMENDATION_MODEL_EXPLAINED.md)** ⭐ **START HERE**

   - The complete story from SysDeRec.ipynb to MovieMate app
   - Explains why we switched to collaborative filtering
   - Theory + practical industry applications
   - ~684 lines, teacher-style explanations

2. **[CODE_WALKTHROUGH.md](./CODE_WALKTHROUGH.md)**
   - Line-by-line code explanation
   - How theory becomes Python code

---

## **Installation & Running**

### **Files**

- MovieLens data files: [u.data](./u.data) and [u.item](./u.item)

### **Setup**

```bash
# Navigate to project directory
cd /Users/rebeca.cavazoss/Documents/examAI

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install flask pandas numpy scikit-learn

# Run the Flask app
python3 app.py
```

### **Access the App**

Open your browser and go to:

```
http://localhost:5000
```

---

## **Industry Best Practices Implemented**

✅ **No Data Leakage**

- Test-set recommendations don't use user's own ratings
- Validation follows proper train/test separation

✅ **Collaborative Filtering**

- User-user approach captures taste similarity
- Weighted predictions account for similarity strength

✅ **Graceful Fallbacks**

- Recommends popular movies if insufficient data
- Handles edge cases (new users, sparse data)

✅ **Frontend Best Practices**

- Progressive enhancement (works without JavaScript too)
- Accessible color contrast
- Touch-friendly mobile design
- Error handling with user-friendly messages

✅ **Scalability Considerations**

- In-memory storage fine for prototypes
- Can add database for persistence and analytics

---

## **Known Limitations & Future Improvements**

⚠️ **Current Limitations:**

- In-memory sessions (lost on server restart)
- No cold-start handling for completely new users
- No content-based filtering (genres, directors, etc.)
- No temporal effects (trending movies, rating drift over time)

🚀 **Future Enhancements:**

- Implement **Implicit Feedback** (clicks, watch time)
- **Hybrid approach** combining collaborative + content-based
- **Real-time updates** as more users join

---

## **Technical Stack**

| Component     | Technology                                  |
| ------------- | ------------------------------------------- |
| **Backend**   | Flask (Python)                              |
| **Frontend**  | HTML5 + CSS3 + Vanilla JavaScript           |
| **ML**        | scikit-learn, NumPy, Pandas                 |
| **Data**      | MovieLens dataset (943 users, 1,682 movies) |
| **Algorithm** | User-User Collaborative Filtering           |
