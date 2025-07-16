# 🎬 Pelicu – AI-Powered Movie & TV Series Recommendation Website

Pelicu is a full-stack web application for discovering and streaming movies and TV series, equipped with an AI-based **Recommendation System**. While the user interface and core features are still in development, the recommendation engine is fully functional and serves as the heart of this project.

---

## 🚀 Key Features

- 🧠 **AI Recommendation System** (Content-Based Filtering)
- 🖥️ Backend: **Django (Python)**
- 🗄️ Database: `SQLite3` (to be migrated to MySQL)
- 🌐 Frontend: `HTML/CSS`, future support for `AJAX`
- 🎯 Fully responsive design (UI in Persian)
- 🔐 User authentication & profile section

---

## 🧠 About the Recommendation System

Pelicu's recommendation engine is based on **Content-Based Filtering**, which suggests movies and TV series by analyzing content attributes such as:

- Genre  
- Description  
- Cast  
- Keywords  

The system creates a feature vector for each item and uses **cosine similarity** to compute the closeness between items. When a user interacts with a movie (views or likes), the system recommends other content with similar characteristics — **without needing data from other users**, making it ideal for new users (cold start).

---

## 📸 Preview

Here’s a sneak peek at the current design of the website (still in development):

![Pelicu UI Preview](./images/pelicu-mookup.jp)

---

## 🔮 Planned Enhancements

- Replace SQLite with MySQL
- AJAX-based dynamic interactions
- Advanced filtering and personalized recommendation improvements
- Better mobile experience and performance optimization

---

## 🧑‍💻 Developer Info

This project is built and maintained by a developer with a strong background in **Python, Django, and AI systems**. Frontend development is minimal by design to focus on backend and AI logic.

---

> ℹ️ **Note:** This platform is designed for Persian-speaking users and features a **Farsi (RTL)** user interface.
