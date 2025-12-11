# test_scraper.py
from main import HBOScraper

def test_scraper_initialization():
    """Test scraper initialization and basic functionality"""
    print("Testing HBOScraper initialization...")
    
    # Create scraper without using proxies for testing
    scraper = HBOScraper(use_proxy=False)
    
    # Check that properties are correctly set
    assert scraper.use_proxy == False, "use_proxy setting not applied"
    assert isinstance(scraper.user_agents, list), "user_agents should be a list"
    assert scraper.hbo_data.get('title') == 'House of the Dragon', "Default HBO data title not set correctly"
    
    print("Initialization test PASSED")
    return scraper

def test_json_structure():
    """Test the output JSON structure"""
    scraper = HBOScraper(use_proxy=False)
    
    # Add some test data
    scraper.hbo_data['episodes'].append({
        'title': 'Test Episode',
        'episode_number': 'S01E01',
        'description': 'Test description',
        'url': 'https://example.com/episode1'
    })
    
    scraper.hbo_data['characters'].append({
        'name': 'Test Character',
        'actor': 'Test Actor',
        'description': 'Test character description',
        'url': 'https://example.com/character1'
    })
    
    # Save to a test file
    output_file = scraper.save_data_to_json("test_output.json")
    print(f"JSON test PASSED - saved to {output_file}")

if __name__ == "__main__":
    print("Running HBOScraper tests...")
    scraper = test_scraper_initialization()
    test_json_structure()
    print("All tests PASSED!")
