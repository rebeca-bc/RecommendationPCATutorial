# Understanding Recommendation Systems & PCA in Action

This project is a tutorial to teach 2 fundamental concepts in machine learning: **Principal Component Analysis (PCA)** and **Collaborative Filtering for Recommendations**. Both are demonstrated with working tutorials and a live, interactive web application.

---

## 📚 Learning Path

### Part 1: PCA & Dimensionality Reduction
**Start here to understand how machine learning compresses data while keeping the important parts.**

The PCA notebook (`PCA.ipynb`) teaches you:
- What is variance and why it matters?
- How PCA reduces 1,682 dimensions to just 95 while keeping 95% of the information
- Visual demonstrations of cumulative variance
- Practical evaluation techniques

**[Open PCA Tutorial →](./PCA.html)**

---

### Part 2: Building a Recommendation Engine
**Once you understand PCA, see how recommendation systems actually work in production.**

You can go into the [Recommendation Matrix Notebook](./RecommendationMatrix.html) to understand the logic behiond the basic matrix and SVDs used to generate reommendations, the notebook has some commentary to explain what was done. This one is more for the curious people (not that mandatory to read)

After, and most importamntly, we built MovieMate, a complete recommendation system using collaborative filtering. Instead of complex matrix factorization (which you learn in theory), we use a simpler, faster approach that works in 2-4 seconds.

**Key Question:** Why did we switch from the mathematically "perfect" SVD algorithm (60+ seconds) to cosine similarity (2-4 seconds)?

**[Live App (Deployed) →](https://recommendationpcatutorial.onrender.com/)** *(Deployed)*

---

## 🎬 How to Use MovieMate (The App)

The app has 3 modes:
1. **Search Mode**: Find your 5 favorite movies, rate them, get recommendations
2. **Quick Mode**: Rate 5 random movies, see what similar users loved
3. **Full Mode**: Rate 10 random movies for deeper insights

No setup needed—just click and start rating. The system finds users with similar taste and recommends what they loved.

---

## 📖 Understanding the Recommendation Logic

Want to understand HOW the recommendations work? Read this in order: 
**[RecommendationModel.md](/reccommendationApp/RecommendationModel.md)** — Deep dive
   - Complete story: theory → practice
   - Why we chose this algorithm
   - Industry standards explained
   - All the math, explained clearly

---

## ✨ The Big Idea

**PCA** teaches you how to compress information without losing signal.

**Collaborative Filtering** shows you that you don't need perfect mathematics to solve real problems—you need pragmatism.

Together, they teach you how professionals think: *Pick the right tool for the constraint, not the most sophisticated algorithm.*

---

## 🎓 Quick Facts

- **PCA Compression**: 1,682 dimensions → 95 dimensions (5% of data, 95% of information)
- **Recommendation Speed**: 2-4 seconds per user (vs. 60-120 seconds with pure SVD)
- **Dataset**: 1,682 movies, 943 users, 100,000 ratings (MovieLens)
- **Algorithm**: Cosine similarity on co-rated movies (industry standard)
- **Accuracy**: High quality recommendations with practical speed

---

## 🔗 Everything You Need

**To Learn:**
- [PCA.html](./PCA.html) (visual tutorial on PCA impact, interactive)
- [PCA.ipynb](./PCA.ipynb) (the source notebook)
- [Recommendation Matrix Notebook](./RecommendationMatrix.html) (notebook to see and understand how the basic model of recommendation works)
- [RecommendationMatrix.ipynb](./RecommendationMatrix.ipynb) (the source code file in python)
- [RecommendationModel.md](./reccommendationApp/RecommendationModel.md) (complete story and tutorial on the model and its explanations)

**To Use:**
- Live app link (or deployed, may take time to charge): [Link is https://recommendationpcatutorial.onrender.com/](https://recommendationpcatutorial.onrender.com/)

**The data Files:**
- [u.data](./reccommendationApp/u.data)
- [u.item](./reccommendationApp/u.item)

**The app files**
- [App Readme](./reccommendationApp/README_MovieRecApp.md)
- [app.py](./reccommendationApp/app.py)
- [index.html](./reccommendationApp/templates/index.html)
