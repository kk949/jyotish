from support.localization import get_text

def test_localization():
    print("Testing Localization...")
    
    # Test English (Default)
    assert get_text("sun", "en") == "Sun"
    print("English test passed")
    
    # Test Hindi
    assert get_text("sun", "hi") == "सूर्य"
    print("Hindi test passed")
    
    # Test Fallback to default lang
    assert get_text("sun", "unknown_lang") == "Sun"
    print("Fallback to default lang passed")
    
    # Test Fallback to key
    assert get_text("unknown_key", "en") == "unknown_key"
    print("Fallback to key passed")
    
    # Test Case Insensitivity
    assert get_text("sun", "HI") == "सूर्य"
    print("Case insensitivity passed")

    print("All tests passed!")

if __name__ == "__main__":
    test_localization()
