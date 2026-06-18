"""
Supabase connection. Single client instance, cached, used by every view.
"""
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_client() -> Client:
    """Return a cached Supabase client. Streamlit re-uses this across reruns."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def safe_query(query):
    """Wrap any Supabase query with error handling so a single bad query
    doesn't crash the whole view."""
    try:
        result = query.execute()
        return result.data if result and result.data else []
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return []
