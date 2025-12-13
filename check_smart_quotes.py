with open('update_mock_course_data.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Check for smart quotes
smart_quotes = ['"', '"', ''', ''']
for sq in smart_quotes:
        if sq in content:
            print(f"Found smart quote: {repr(sq)}")
            print(f"Count: {content.count(sq)}")
            
# Check first occurrence
for i, char in enumerate(content[:2000]):
    if char in smart_quotes:
        print(f"First smart quote at position {i}: {repr(char)}")
        print(f"Context: {repr(content[max(0,i-20):i+20])}")
        break
else:
    print("No smart quotes found in first 2000 chars")
