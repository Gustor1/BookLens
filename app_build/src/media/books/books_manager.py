import pandas as pd
import streamlit as st
from ..base import BaseMediaManager

class BooksManager(BaseMediaManager):
    def __init__(self, recommender=None, df=None):
        self.recommender = recommender
        self.df = df
        
    def _get_recommender(self):
        if self.recommender is not None:
            return self.recommender
        if "recommender" in st.session_state:
            return st.session_state["recommender"]
        return None
        
    def _get_df(self):
        if self.df is not None:
            return self.df
        if "merged_df" in st.session_state:
            return st.session_state["merged_df"]
        return None

    def search(self, query: str, filters: dict = None) -> list:
        df = self._get_df()
        if df is None:
            return []
        
        filtered = df.copy()
        
        if query:
            q = query.lower()
            mask = (
                filtered["Book-Title"].str.lower().str.contains(q, na=False) |
                filtered["Book-Author"].str.lower().str.contains(q, na=False)
            )
            filtered = filtered[mask]
            
        if filters:
            if "genre" in filters and filters["genre"] != "Tous":
                filtered = filtered[filtered["Theme"] == filters["genre"]]
            if "creator" in filters and filters["creator"] != "Tous":
                filtered = filtered[filtered["Book-Author"] == filters["creator"]]
                
        books_agg = filtered.drop_duplicates(subset=["ISBN"])
        
        results = []
        for _, row in books_agg.iterrows():
            rating = row.get("Real-Rating") if pd.notna(row.get("Real-Rating")) else row.get("Book-Rating")
            count = row.get("Real-Rating-Count") if pd.notna(row.get("Real-Rating-Count")) else 10
            source = row.get("Rating-Source") if pd.notna(row.get("Rating-Source")) else "Estimée"
            
            results.append({
                "id": str(row["ISBN"]),
                "title": str(row["Book-Title"]),
                "creator": str(row["Book-Author"]),
                "publisher": str(row.get("Publisher", "N/A")),
                "year": str(int(row["Year-Of-Publication"])) if pd.notna(row.get("Year-Of-Publication")) else "N/A",
                "rating": float(rating) if pd.notna(rating) else None,
                "rating_count": int(count) if pd.notna(count) else 0,
                "rating_source": str(source),
                "cover_url": str(row.get("Cover-URL")) if pd.notna(row.get("Cover-URL")) else row.get("Image-URL-M", ""),
                "description": str(row.get("Description", "")) if pd.notna(row.get("Description")) else "",
                "genres": [str(row["Theme"])] if pd.notna(row.get("Theme")) else []
            })
        return results

    def get_recommendations(self, media_id: str, n: int = 5, filters: dict = None) -> list:
        recommender = self._get_recommender()
        df = self._get_df()
        if recommender is None or df is None:
            return []
            
        book_row = df[df["ISBN"] == media_id]
        if book_row.empty:
            return []
        book_title = book_row.iloc[0]["Book-Title"]
        
        theme_filter = filters.get("genre") if filters and filters.get("genre") != "Tous" else None
        
        recs = recommender.get_recommendations(book_title, n=n, theme_filter=theme_filter)
        if recs is None or recs.empty:
            return []
            
        results = []
        for _, row in recs.iterrows():
            title = row["Book-Title"]
            meta_rows = df[df["Book-Title"] == title]
            if meta_rows.empty:
                continue
            meta = meta_rows.iloc[0]
            
            rating = meta.get("Real-Rating") if pd.notna(meta.get("Real-Rating")) else row.get("Avg-Rating")
            count = meta.get("Real-Rating-Count") if pd.notna(meta.get("Real-Rating-Count")) else row.get("Num-Ratings", 0)
            source = meta.get("Rating-Source") if pd.notna(meta.get("Rating-Source")) else row.get("Rating-Source", "Estimée")
            
            results.append({
                "id": str(meta["ISBN"]),
                "title": title,
                "creator": str(row.get("Author", "Inconnu")),
                "publisher": str(meta.get("Publisher", "N/A")),
                "year": str(int(meta["Year-Of-Publication"])) if pd.notna(meta.get("Year-Of-Publication")) else "N/A",
                "rating": float(rating) if pd.notna(rating) else None,
                "rating_count": int(count) if pd.notna(count) else 0,
                "rating_source": str(source),
                "cover_url": str(meta.get("Cover-URL")) if pd.notna(meta.get("Cover-URL")) else meta.get("Image-URL-M", ""),
                "description": str(meta.get("Description", "")) if pd.notna(meta.get("Description")) else "",
                "genres": [str(row["Theme"])] if pd.notna(row.get("Theme")) else [],
                "similarity": float(row.get("Similarity-Score", 0))
            })
        return results

    def get_details(self, media_id: str) -> dict:
        df = self._get_df()
        if df is None:
            return {}
        book_row = df[df["ISBN"] == media_id]
        if book_row.empty:
            return {}
        row = book_row.iloc[0]
        
        rating = row.get("Real-Rating") if pd.notna(row.get("Real-Rating")) else row.get("Book-Rating")
        count = row.get("Real-Rating-Count") if pd.notna(row.get("Real-Rating-Count")) else 10
        source = row.get("Rating-Source") if pd.notna(row.get("Rating-Source")) else "Estimée"
        
        return {
            "id": str(row["ISBN"]),
            "title": str(row["Book-Title"]),
            "creator": str(row["Book-Author"]),
            "publisher": str(row.get("Publisher", "N/A")),
            "year": str(int(row["Year-Of-Publication"])) if pd.notna(row.get("Year-Of-Publication")) else "N/A",
            "rating": float(rating) if pd.notna(rating) else None,
            "rating_count": int(count) if pd.notna(count) else 0,
            "rating_source": str(source),
            "cover_url": str(row.get("Cover-URL")) if pd.notna(row.get("Cover-URL")) else row.get("Image-URL-M", ""),
            "description": str(row.get("Description", "")) if pd.notna(row.get("Description")) else "",
            "genres": [str(row["Theme"])] if pd.notna(row.get("Theme")) else []
        }

    def get_book_list(self) -> list:
        recommender = self._get_recommender()
        if recommender:
            return recommender.get_book_list()
        df = self._get_df()
        if df is not None:
            return sorted(df["Book-Title"].dropna().unique().tolist())
        return []

    def get_available_genres(self) -> list:
        recommender = self._get_recommender()
        if recommender:
            return recommender.get_available_themes()
        df = self._get_df()
        if df is not None and "Theme" in df.columns:
            return sorted(df["Theme"].dropna().unique().tolist())
        return []
