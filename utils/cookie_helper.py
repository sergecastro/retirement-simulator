"""
Cookie helper for Welcome Back feature.
Stores ONLY user's first name and last save date (non-sensitive).
"""
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime

@st.cache_resource
def get_cookie_manager():
    """Get or create cookie manager instance (cached to prevent duplicate key errors)."""
    return stx.CookieManager(key="ff_cookie_manager")

def set_welcome_back_cookie(first_name: str, save_timestamp: str = None):
    """
    Save user's first name and save date to cookie.
    Called after SAVE to remember the user.

    Args:
        first_name: User's first name only (e.g., "John")
        save_timestamp: ISO format timestamp (e.g., "2025-11-23T18:00:00")
    """
    if first_name and first_name.strip():
        cookie_manager = get_cookie_manager()

        # Extract first name only (before any space)
        first_only = first_name.strip().split()[0]
        cookie_manager.set("ff_user_name", first_only)
        print(f"[COOKIE] Saved user name: {first_only}")

        # Save timestamp
        if save_timestamp:
            cookie_manager.set("ff_last_save", save_timestamp)
            print(f"[COOKIE] Saved last save date: {save_timestamp}")
        else:
            # Use current time if not provided
            now = datetime.now().isoformat()
            cookie_manager.set("ff_last_save", now)
            print(f"[COOKIE] Saved last save date: {now}")

def get_welcome_back_info() -> dict:
    """
    Get user's first name and last save date from cookies.
    Called on Welcome page to show personalized greeting.

    Returns:
        Dict with 'name' and 'last_save' keys (empty strings if not found)
    """
    result = {"name": "", "last_save": "", "formatted_date": ""}

    try:
        cookie_manager = get_cookie_manager()

        name = cookie_manager.get("ff_user_name")
        if name:
            result["name"] = name
            print(f"[COOKIE] Found user name: {name}")

        last_save = cookie_manager.get("ff_last_save")
        if last_save:
            result["last_save"] = last_save
            # Format for display: "November 23rd at 6:00 PM"
            try:
                dt = datetime.fromisoformat(last_save)
                day = dt.day
                suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                result["formatted_date"] = dt.strftime(f"%B {day}{suffix} at %-I:%M %p")
            except:
                result["formatted_date"] = last_save
            print(f"[COOKIE] Found last save: {result['formatted_date']}")

    except Exception as e:
        print(f"[COOKIE] Error reading cookies: {e}")

    return result

def clear_welcome_back_cookies():
    """Clear all welcome back cookies (for Start Fresh)."""
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete("ff_user_name")
        cookie_manager.delete("ff_last_save")
        print("[COOKIE] Cleared welcome back cookies")
    except Exception as e:
        print(f"[COOKIE] Error clearing cookies: {e}")

def has_returning_user() -> bool:
    """
    Quick check if we have a returning user.

    Returns:
        True if user name cookie exists
    """
    try:
        cookie_manager = get_cookie_manager()
        name = cookie_manager.get("ff_user_name")
        return bool(name)
    except:
        return False
